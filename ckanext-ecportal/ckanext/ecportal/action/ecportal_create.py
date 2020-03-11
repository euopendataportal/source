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

import logging
import time
import cPickle as pickle

import ckanext.ecportal.lib.cache.redis_cache as redis_cache
import ckanext.ecportal.lib.search as search
import ckan.lib.navl.dictization_functions
import ckan.lib.plugins as lib_plugins
import ckan.logic as logic
import ckan.model as model
import ckanext.ecportal.action.ecportal_validation as validation
import ckanext.ecportal.lib.uri_util as uri_util
import ckanext.ecportal.configuration.configuration_constants as constants


from pylons import config
from ckanext.ecportal.migration import dataset_transition_util
from ckan.common import _
from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.lib.search.dcat_index import PackageSearchIndex as solar_package_index
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp, SchemaGeneric
from ckanext.ecportal.model.identifier_mapping import DatasetIdMapping

from doi.exceptions.doi_registration_exception import DOIRegistrationException
from doi.facade import doi_facade
from ckanext.ecportal.lib.ui_util import _get_doi_from_adms_identifier

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_check_access = logic.check_access
_get_action = logic.get_action
ValidationError = logic.ValidationError
ActionError = logic.ActionError
NotFound = logic.NotFound
_get_or_bust = logic.get_or_bust


def package_create(context, data_dict):
    '''
    This overides core package_create  to deal with DCAT-AP datasets and old CKAN model datasets.
    :param context:
    :param data_dict:
    :return:
    '''
    user = context['user']
    package_type = data_dict.get('type')
    package_plugin = lib_plugins.lookup_package_plugin(package_type)
    if 'schema' in context:
        schema = context['schema']
    else:
        schema = package_plugin.create_package_schema()

    _check_access('package_create', context, data_dict)

    if 'api_version' not in context:
        # check_data_dict() is deprecated. If the package_plugin has a
        # check_data_dict() we'll call it, if it doesn't have the method we'll
        # do nothing.
        check_data_dict = getattr(package_plugin, 'check_data_dict', None)
        if check_data_dict:
            try:
                check_data_dict(data_dict, schema)
            except TypeError:
                # Old plugins do not support passing the schema so we need
                # to ensure they still work
                package_plugin.check_data_dict(data_dict)

    ex_url = data_dict.get('url')
    publisher = data_dict.get('owner_org')

    dataset = None
    mapper = None
    if not 'DCATAP' == context.get('model', ''):
        package_show_action = 'legacy_package_show'
        if config.get('ckan.ecodp.backward_compatibility', 'true') in 'false, False':
            raise logic.NotFound('Function not available')

        #if not validation.is_ckanName_unique(data_dict.get('name', '')):
        #    raise ValidationError(_('That CKAN name is already in use.'))

        try:
            dataset = dataset_transition_util.create_dataset_schema_for_package_dict(data_dict)
        except ValidationError as e:
            import traceback
            log.error('{0}'.format(e))
            log.error(traceback.print_exc())
            raise e
        except BaseException as e:
            import traceback
            log.error('{0}'.format(e))
            log.error(traceback.print_exc())
            raise ValidationError('Could {0} not transform to new model'.format(data_dict.get('name')))

        context['package'] = dataset

        if not ex_url:
            raise ValidationError(_('The URL is mandatory.'))

        int_id = dataset.dataset_uri.split('/')[-1]
        mapper = DatasetIdMapping(ex_url, int_id, publisher)
        if mapper.is_mapping_exists():
            raise ValidationError(_('That URL already exists [{0}] for publisher [{1}].'.format(ex_url, publisher)))

    else:
        package_show_action = 'package_show'
        uri, ds_name = uri_util.new_dataset_uri_from_title(data_dict.get('title'))
        dataset = DatasetDcatApOp(uri)
        context['package'] = dataset
        data_dict['name'] = ds_name #uri.split('/')[-1]# put the correct ckanName alligned with the uri.
        data_dict['accessRights'] = 'http://publications.europa.eu/resource/authority/access-right/PUBLIC' #add default public accessright

        dataset.create_dataset_schema_for_package_dict(data_dict, {}, context)

    start = time.time()
    dataset, errors = validation.validate_dacat_dataset(dataset, context)
    context['errors'] = errors
    log.info('validation took {0} sec'.format(time.time() - start))

    # TODO check the business rule of save
    if errors.get('fatal'):
        # dataset.privacy_state = DCATAPOP_PRIVATE_DATASET
        # dataset.add_draft_to_title()
        raise ValidationError(errors)
    elif errors.get('error') and dataset.privacy_state == DCATAPOP_PUBLIC_DATASET:
        # dataset.privacy_state = DCATAPOP_PRIVATE_DATASET
        # dataset.add_draft_to_title()
        raise ValidationError(errors)
        # elif errors.get('error') and dataset.privacy_state == DCATAPOP_PRIVATE_DATASET:
        #   pass

    # if dataset.privacy_state ==DCATAPOP_PRIVATE_DATASET:
    #    dataset.add_draft_to_title()

    rev = model.repo.new_revision()
    rev.author = user
    if 'message' in context:
        rev.message = context['message']
    else:
        rev.message = _(u'REST API: Create object %s') % dataset.dataset_uri

    try:
        state = dataset.save_to_ts(rev.id)
        if state and mapper:
            mapper.save_to_db()
    except BaseException as e:
        import traceback
        log.error('{0}'.format(e))
        log.error(traceback.print_exc())
        log.error("Error while saving the package to Virtuoso.")
        model.repo.rollback()
        raise ActionError('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))

    context_org_update = context.copy()
    context_org_update['ignore_auth'] = True
    context_org_update['defer_commit'] = True
    _get_action('package_owner_org_update')(context_org_update,
                                            {'id': dataset.schema.uri,
                                             'organization_id': data_dict.get('owner_org') or data_dict.get('organization')})

    # for item in plugins.PluginImplementations(plugins.IPackageController):
    #     item.create(pkg)
    #
    #     item.after_create(context, data)

    ## this is added so that the rest controller can make a new location
    context["id"] = dataset.schema.uri
    log.debug('Created object %s' % dataset.schema.uri)

    # Make sure that a user provided schema is not used on package_show
    context.pop('schema', None)

    return_id_only = context.get('return_id_only', False)
    if return_id_only:
        output = dataset.dataset_uri
    elif 'legacy_package_show' == package_show_action:
        output = _get_action(package_show_action)(context, {'uri': dataset.dataset_uri})
    else:
        _get_action(package_show_action)(context, {'uri': dataset.dataset_uri})
        output = context.get('package')

    indexer = solar_package_index()

    try:
        indexer.update_dict(dataset)
        if not context.get('defer_commit'):
            model.repo.commit()
    except Exception as e:
        dataset.delete_from_ts()
        model.repo.rollback()
        raise ActionError('Error while index the package {0} to Solr.'.format(dataset.dataset_uri))

    return output


def assign_doi(context, pkg_dict):
    doi = doi_facade.DOIFacade(constants.DOI_CONFIG)
    if hasattr(pkg_dict, 'dataset_uri'):
        _check_access('package_update', context, pkg_dict)
        doi_str = _get_doi_from_adms_identifier(pkg_dict.schema.identifier_adms).value_or_uri
        doi.assign_doi(doi_str, pkg_dict.dataset_uri)
    else:
        _check_access('catalog_create', context, pkg_dict)
        doi_str = _get_doi_from_adms_identifier(pkg_dict.schema.identifier_adms).value_or_uri
        doi.assign_doi(doi_str, pkg_dict.catalog_uri)


def publish_doi(context, pkg_dict):
    doi = doi_facade.DOIFacade(constants.DOI_CONFIG)
    doi_dict = pkg_dict.build_DOI_dict()
    doi_str = ''
    if hasattr(pkg_dict, 'dataset_uri'):
        _check_access('package_update', context, pkg_dict)
        doi_str = _get_doi_from_adms_identifier(pkg_dict.schema.identifier_adms).value_or_uri
    else:
        _check_access('catalog_create', context, pkg_dict)
        doi_str = _get_doi_from_adms_identifier(pkg_dict.schema.identifier_adms).value_or_uri

    try:
        doi.register_doi(doi_str, doi_dict)
    except DOIRegistrationException as e:
        log.error(doi_dict['url'] + " : " + e.message)


def resource_create(context, data_dict):
    user = context['user']
    dataset = None  # type: DatasetDcatApOp
    active_cache = config.get('ckan.cache.active', 'false')
    _check_access('package_update', context, data_dict)

    pkg =  pkg_dict = logic.get_action('package_show')(context, {'id': data_dict.pop('package_id','')})
    dataset = context['package']

    old_dataset = pickle.dumps(dataset)
    try:
        dataset = dataset_transition_util.update_dataset_for_package_dict(dataset, data_dict)
        dataset = dataset_transition_util.update_resources_for_dataset([data_dict], dataset, dataset)
    except ValidationError as e:
        import traceback
        log.error('{0}'.format(e))
        log.error(traceback.print_exc())
        raise e
    except Exception as e:
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
        # dataset.privacy_state = DCATAPOP_PRIVATE_DATASET
        # dataset.add_draft_to_title()
        raise ValidationError(errors)
    elif errors.get('error') and dataset.privacy_state == DCATAPOP_PUBLIC_DATASET:
        # dataset.privacy_state = DCATAPOP_PRIVATE_DATASET
        # dataset.add_draft_to_title()
        raise ValidationError(errors)
    elif errors.get('error') and dataset.privacy_state == DCATAPOP_PRIVATE_DATASET:
        # dataset.add_draft_to_title()
        pass

    rev = model.repo.new_revision()
    rev.author = user
    if 'message' in context:
        rev.message = context['message']
    else:
        rev.message = _(u'REST API: Update object %s') % dataset.dataset_uri.split('/')[-1]

    try:
        result = dataset.save_to_ts(rev.id)
    except BaseException as e:
        log.error('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))
        model.repo.rollback()
        raise ActionError('Error while saving the package {0} to Virtuoso.'.format(dataset.dataset_uri))

    context_org_update = context.copy()
    context_org_update['ignore_auth'] = True
    context_org_update['defer_commit'] = True

    for item in lib_plugins.PluginImplementations(lib_plugins.IPackageController):
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
    except Exception as e:
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

    for item in lib_plugins.PluginImplementations(lib_plugins.IResourceUrlChange):
        if item.name != 'qa':
            item.notify(dataset, model.domain_object.DomainObjectOperation.changed)

    # we could update the dataset so we should still be able to read it.
    context['ignore_auth'] = True
    return_id_only = context.get('return_id_only', False)

    output = _get_action('legacy_package_show')(context, {'uri': dataset.dataset_uri})

    return output