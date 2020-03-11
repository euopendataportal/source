#    Copyright (C) <2018>  <Publications Office of the European Union>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>

import cPickle as pickle
import logging
import time
import ckan.logic as logic

import ckan.lib.navl.dictization_functions
import ckan.model as model
import ckan.plugins as plugins
from ckan.common import _

import ckanext.ecportal.lib.cache.redis_cache as redis_cache
import ckanext.ecportal.lib.search as search
import ckanext.ecportal.action.ecportal_validation as validation
from ckanext.ecportal.model.identifier_mapping import DatasetIdMapping
from pylons import config

import ckanext.ecportal.migration.dataset_transition_util as dataset_transition_util

from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.model.schemas.dcatapop_distribution_schema import DistributionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
import ckanext.ecportal.helpers as helpers

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_get_action = logic.get_action
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
ActionError = logic.ActionError
NotAuthorized = logic.NotAuthorized
_get_or_bust = logic.get_or_bust


def package_update(context, data_dict):
    '''
    This overrides core package_update  to deal with DCAT-AP datasets.
    This method handels old input type CKAN property keys used by API
    :param context:
    :param data_dict:
    :return:
    '''
    user = context['user']
    dataset = None  # type: DatasetDcatApOp
    active_cache = config.get('ckan.cache.active', 'false')
    _check_access('package_update', context, data_dict)
    old_dataset = None
    rdft = True
    if 'DCATAP' == context.get('model', ''):
        package_show_action = 'package_show'
        pkg_dict = logic.get_action('package_show')(context, {'id': data_dict.get('id')})
        dataset = context['package']
        dataset.update_dataset_for_package_dict(data_dict, {}, context)
        old_dataset = pickle.dumps(dataset)
        context['package'] = dataset

    else:  # old model, use migration. this can also be the new model comming from the UI
        # prepare the dataset object with migration function
        package_show_action = 'legacy_package_show'
        rdft = False
        if config.get('ckan.ecodp.backward_compatibility', 'true') in 'false, False':
            raise logic.NotFound('Function not available')

        pkg_dict = logic.get_action('package_show')(context, {'id': data_dict.get('name')})
        dataset = context['package']
        old_dataset = pickle.dumps(dataset)
        try:
            dataset = dataset_transition_util.update_dataset_for_package_dict(dataset, data_dict)
        except ValidationError as e:
            import traceback
            log.error('{0}'.format(e))
            log.error(traceback.print_exc())
            raise e
        except BaseException as e:
            import traceback
            log.error(traceback.print_exc())
            raise ValidationError('Could {0} not transform to new model'.format(dataset.dataset_uri))
            # old_data_dict = logic.get_action('package_show')(context, {'id': data_dict.get('id')})
            # old_dataset = context['package']  # type: DatasetDcatApOp
    start = time.time()
    dataset, errors = validation.validate_dacat_dataset(dataset, context)
    context['errors'] = errors
    log.info('validation took {0} sec'.format(time.time() - start))
    # TODO check the business rule of save
    if errors.get('fatal'):
        raise ValidationError(errors)
    elif errors.get('error') and dataset.privacy_state == DCATAPOP_PUBLIC_DATASET:
        raise ValidationError(errors)
    rev = model.repo.new_revision()
    rev.author = user
    if 'message' in context:
        rev.message = context['message']
    else:
        rev.message = _(u'REST API: Update object %s') % dataset.dataset_uri.split('/')[-1]

    try:
        save_to_ts_status = dataset.save_to_ts(rev.id)
    except BaseException as e:
        log.error('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))
        model.repo.rollback()
        raise ActionError('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))

    if save_to_ts_status:
        context_org_update = context.copy()
        context_org_update['ignore_auth'] = True
        context_org_update['defer_commit'] = True
        if not rdft:
            ext_id = data_dict.get('url')
            publisher = data_dict.get('owner_org')
            int_id = dataset.dataset_uri.split('/')[-1]
            mapping = DatasetIdMapping.by_internal_id(int_id)
            if not mapping:
                mapping = DatasetIdMapping(ext_id,int_id,publisher)
                mapping.save_to_db()
            else:
                mapping.publisher = publisher
                mapping.external_id = ext_id
                mapping.update_db()



        for item in plugins.PluginImplementations(plugins.IPackageController):
            item.edit(dataset)
            item.after_update(context, dataset)

        log.debug('Updated object %s' % dataset.dataset_uri)

        return_id_only = context.get('return_id_only', False)

        # Make sure that a user provided schema is not used on package_show
        context.pop('schema', None)

        if dataset.privacy_state == 'public' and active_cache == 'true':
            redis_cache.set_value_no_ttl_in_cache(dataset.dataset_uri, pickle.dumps(dataset))
        else:
            redis_cache.delete_value_from_cache(dataset.dataset_uri)

        try:
            redis_cache.flush_all_from_db(redis_cache.MISC_POOL)
            search.rebuild(dataset.dataset_uri.split('/')[-1])
        except BaseException as e:
            log.error("Error while index the package {0} to Solr".format(dataset.dataset_uri))
            old_dataset = pickle.loads(old_dataset)
            dataset.schema = old_dataset.schema
            dataset.schema_catalog_record = old_dataset.schema_catalog_record
            dataset.privacy_state = old_dataset.privacy_state
            dataset.save_to_ts()
            search.rebuild(dataset.dataset_uri.split('/')[-1])
            model.repo.rollback()
            raise ActionError('Error while index the package {0} to Solr.'.format(dataset.dataset_uri))

        if not context.get('defer_commit'):
            model.repo.commit()

        for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
            if item.name != 'qa':
                item.notify(dataset, model.domain_object.DomainObjectOperation.changed)

        # we could update the dataset so we should still be able to read it.
        context['ignore_auth'] = True
        return_id_only = context.get('return_id_only', False)
        if return_id_only:
            output = dataset.dataset_uri
        elif 'legacy_package_show' == package_show_action:
            output = _get_action(package_show_action)(context, {'uri': dataset.dataset_uri})
        else:
            _get_action(package_show_action)(context, {'uri': dataset.dataset_uri})
            output = context.get('package')

        return output
    else:
        log.error('[Action] [Update] [Failed] [Dataset:<{0}>]'.format(dataset.dataset_uri))
        raise ActionError('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))


def package_owner_org_update(context, data_dict):
    '''Update the owning organization of a dataset

    :param id: the name or id of the dataset to update
    :type id: string

    :param organization_id: the name or id of the owning organization
    :type id: string
    '''
    name_or_id = data_dict.get('id')
    organization_id = None
    if data_dict.get('organization_id'):
        organization_id = data_dict.get('organization_id').split('/')[-1].lower()

    _check_access('package_owner_org_update', context, data_dict)

    # pkg = model.Package.get(name_or_id)

    pkg = _get_action('package_show')(context, {'uri': name_or_id})
    ds = context['package']
    dataset_uri = ds.schema.uri
    if pkg is None:
        raise NotFound(_('Package was not found.'))
    org = None
    if organization_id:
        org = model.Group.get(organization_id)
        if org is None or not org.is_organization:
            raise NotFound(_('Organization was not found.'))

    members = model.Session.query(model.Member) \
        .filter(model.Member.table_id == dataset_uri) \
        .filter(model.Member.capacity == 'organization')

    need_update = True
    for member_obj in members:
        if org and member_obj.group_id == org.id:
            need_update = False
        else:
            member_obj.state = 'deleted'
            member_obj.save()

    # add the organization to member table
    if org and need_update:
        member_obj = model.Member(table_id=dataset_uri,
                                  table_name='package',
                                  group=org,
                                  capacity='organization',
                                  group_id=org.id,
                                  state='active')
        model.Session.add(member_obj)

    if not context.get('defer_commit'):
        model.Session.commit()


def term_translation_update_many(context, data_dict):
    '''Create or update many term translations at once.
        Override the CKAN Core function

    :param data: the term translation dictionaries to create or update,
        for the format of term translation dictionaries see
        ``term_translation_update()``
    :type data: list of dictionaries

    :returns: a dictionary with key ``'success'`` whose value is a string
        stating how many term translations were updated
    :rtype: string

    '''

    import ckan.logic.action.update as core
    return core.term_translation_update_many(context, data_dict)



def dcat_term_translation_update_many(context, data_dict):
    '''Create or update many term translations at once.

    :param data_dict: the term translation dictionaries to create or update, e.g.:
    {
    "data": [
        {
            "lang_code": "fr",
            "term": "English term",
            "term_translation": "Translated term"
        },
        {
            "lang_code": "de",
            "term": "English term",
            "term_translation": "Translated term"
        }
        ],
        "resources": [
            {
                "de": [
                    {
                        "field": "name",
                        "field_translation": "Translated term",
                        "lang_code": "de",
                    }
                ]

                "da"

            }

             {
                "fr": [
                    {
                        "field": "name",
                        "field_translation": "Translated term",
                        "lang_code": "de",
                    }
                ]

            }

        ],
    "uri": "Uri of the dataset"
    }
    :type data_dict: dict

    :returns: a dictionary with key ``'success'`` whose value is a string
        stating how many term translations were updated
    :rtype: string

    '''
    model = context['model']
    active_cache = config.get('ckan.cache.active', 'false')

    if not (data_dict.get('data') and isinstance(data_dict.get('data'), list)):
        raise ValidationError(
            {'error': 'term_translation_update_many needs to have a '
                      'list of dicts in field data'}
        )

    sorted_dict = {}

    for item in data_dict.get('data'):
        if not sorted_dict.get(item.get('term', None)):
            sorted_dict[item.get('term')] = {item.get('lang_code'): item.get('term_translation')}
        elif not sorted_dict.get(item.get('term')).get(item.get('term_translation', None)):
            sorted_dict[item.get('term')][item.get('lang_code')] = item.get('term_translation')

    sorted_resources = {}

    for resource in data_dict.get('resources', []):

        for language in resource.values():
            for value in language:
                new_resource = sorted_resources.get(value.get('resource_id'), {})
                if not new_resource:

                    new_resource[value.get('field')] = [
                        {'lang': value.get('lang_code'), 'field_translation': value.get('field_translation')}]
                    sorted_resources[value.get('resource_id')] = new_resource
                else:
                    if not new_resource.get(value.get('field'), None):
                        new_resource[value.get('field')] = [{'lang': value.get('lang_code'),
                                                             'field_translation': value.get(
                                                                 'field_translation')}]
                    else:
                        new_resource[value.get('field')].append({'lang': value.get('lang_code'),
                                                                 'field_translation': value.get(
                                                                     'field_translation')})

    context['defer_commit'] = True
    ds_uri = data_dict.get('uri')
    action = _get_action('package_show')
    action(context, {'uri': ds_uri})
    dataset = context.get('package')  # type:DatasetDcatApOp

    titel_en = next(
        (value for value in dataset.schema.title_dcterms.values() if not value.lang or value.lang == 'en'),
        None)
    description_en = next(
        (value for value in dataset.schema.description_dcterms.values() if not value.lang or value.lang == 'en'),
        None)
    alt_title_en = next(
        (value for value in dataset.schema.alternative_dcterms.values() if not value.lang or value.lang == 'en'),
        None)

    if titel_en:
        new_titels = {'0': titel_en}
        for text, value in sorted_dict.items():
            if text == titel_en.value_or_uri:
                for lang, translation in value.items():
                    new_titels[str(len(new_titels))] = ResourceValue(translation, lang=lang)

        dataset.schema.title_dcterms = new_titels

    if description_en:
        new_description = {'0': description_en}
        for text, value in sorted_dict.items():
            if text == description_en.value_or_uri:
                for lang, translation in value.items():
                    new_description[str(len(new_description))] = ResourceValue(translation, lang=lang)

        dataset.schema.description_dcterms = new_description

    if alt_title_en:
        new_dalt_title = {'0': alt_title_en}
        for text, value in sorted_dict.items():
            if text == alt_title_en.value_or_uri:
                for lang, translation in value.items():
                    new_dalt_title[str(len(new_dalt_title))] = ResourceValue(translation, lang=lang)

        dataset.schema.alternative_dcterms = new_dalt_title

    if dataset.schema.distribution_dcat:
        for uri, fields in sorted_resources.items():
            uri = "{0}/{1}".format("http://data.europa.eu/88u/distribution",uri)
            src_distribution = next(
                (dstr for dstr in dataset.schema.distribution_dcat.values() if dstr.uri == uri),
                None)  # type: DistributionSchemaDcatApOp
            if not src_distribution:
                continue

            for field, translations in fields.items():
                if 'name' == field:
                    new_titles = next((titel for titel in src_distribution.title_dcterms.values() if
                                       not titel.lang or titel.lang == 'en'))
                    new_translation = {'0': new_titles}
                    for translation in translations:
                        new_translation[str(len(new_translation))] = ResourceValue(
                            translation.get('field_translation'), lang=translation.get('lang'))

                    src_distribution.title_dcterms = new_translation
                elif 'description':
                    new_desc = next((desc for desc in src_distribution.description_dcterms if
                                     not desc.lang or desc.lang == 'en'))
                    new_translations = {'0': new_desc}
                    for translation in translations:
                        new_translation[str(len(new_translation))] = ResourceValue(
                            translation.get('field_translation'), lang=translation.get('lang'))

                    src_distribution.title_dcterms = new_translation

    if dataset.schema.topic_foaf:
        for uri, fields in sorted_resources.items():
            uri = "{0}/{1}".format("http://data.europa.eu/88u/document", uri)
            src_documnet = next((doc for doc in dataset.schema.topic_foaf.values() if doc.uri == uri),
                                None)  # type: DocumentSchemaDcatApOp
            if not src_documnet:
                continue

            for field, translations in fields.items():
                if 'name' == field:
                    new_titles = next((titel for titel in src_documnet.title_dcterms.values() if
                                       not titel.lang or titel.lang == 'en'))
                    new_translation = {'0': new_titles}
                    for translation in translations:
                        new_translation[str(len(new_translation))] = ResourceValue(
                            translation.get('field_translation'), lang=translation.get('lang'))

                    src_documnet.title_dcterms = new_translation
                elif 'description':
                    new_desc = next((desc for desc in src_documnet.description_dcterms if
                                     not desc.lang or desc.lang == 'en'))
                    new_translations = {'0': new_desc}
                    for translation in translations:
                        new_translation[str(len(new_translation))] = ResourceValue(
                            translation.get('field_translation'), lang=translation.get('lang'))

                    src_documnet.title_dcterms = new_translation

    try:
        result = dataset.save_to_ts()
    except BaseException as e:
        log.error('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))
        raise ActionError('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))

    if dataset.privacy_state == 'public' and active_cache == 'true':
        redis_cache.set_value_no_ttl_in_cache(dataset.dataset_uri, pickle.dumps(dataset))
    else:
        redis_cache.delete_value_from_cache(dataset.dataset_uri)

    try:
        redis_cache.flush_all_from_db(redis_cache.MISC_POOL)
        search.rebuild(dataset.dataset_uri.split('/')[-1])
    except Exception as e:
        log.error("Error while index the package {0} to Solr".format(dataset.dataset_uri))
    if result:
        return {'success': '%s  updated' % (ds_uri)}
    else:
        return {'fails': '%s  not updated' % (ds_uri)}


