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
import datetime

import ckan.lib.navl.dictization_functions
import ckan.logic as logic
from pylons import config
from rdflib import XSD

from ckanext.ecportal.action.rdf2odp_dataset_description import Rdf2odpDatasetDescription
from ckanext.ecportal.lib import uri_util
from ckanext.ecportal.virtuoso import PRIVACY_STATE_PRIVATE, PRIVACY_STATE_PUBLIC
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_helpers import TripleStoreIngestionHelpers
import ckanext.ecportal.lib.cache.redis_cache as redis_cache
import ckanext.ecportal.lib.search as search
import cPickle as pickle
import ckan.model as model
import ckanext.ecportal.helpers as ckanext_helpers
from ckanext.ecportal.migration import dataset_transition_util
import ckan.plugins as plugins
from ckanext.ecportal.model.dataset_dcatapop import  DatasetDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.action.ecportal_validation import validate_dacat_dataset
import ckanext.ecportal.lib.controlled_vocabulary_util as controlled_vocabulary_util

ADD_REPLACE = 'addReplace'

PUBLISHED = 'published'

DRAFT = 'draft'

STATUS_NOT_DEFINED = "status_not_defined"

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

_get_or_bust = logic.get_or_bust

URI_TEMPLATE = config.get('ckan.ecodp.uri_prefix', '')


def package_save(context, data_dict):
    """
    Create or update a package from rdf2odp call.
    """
    # TODO: separate into phases:
    # Phase 1: transform rdf to all datasets (URI replacement)
    # Phase 2: check for new or update and complete dataset object creation (create missing default values or re assign values to keep)
    # Phase 3: validate all datasets
    # Pahse 4: perform the "transaction" of safe (doi, TS, redis, solr)
    import sys
    reload(sys)
    global_report = []
    from ckanext.ecportal.action.ecportal_validation import validate_parameter_package_save
    report_validation_parameter = validate_parameter_package_save(data_dict)
    ret = {"fatal": report_validation_parameter}
    if report_validation_parameter.get("validation_json_structure", None):
        report_dataset = {'errors': ret, 'status_save': False}
        raise ValidationError(report_dataset, "Invalide structure of the JSON: rdfFile missing ")

    sys.setdefaultencoding('utf-8')
    rdfFile = u'{0}'.format(data_dict.get('rdfFile', ''))
    dataset_description_mapped_to_status = {}
    add_replace_actions = data_dict.get('addReplaces', [])
    for add_replace_action in add_replace_actions:
        add_replace = add_replace_action.get(ADD_REPLACE, '')
        uri = add_replace_action.get('objectUri', '')
        ckan_name = add_replace_action.get('objectCkanName', '')
        object_status = add_replace.get("objectStatus")

        # dataset_description_mapped_to_status[uri] = Rdf2odpDatasetDescription(ckan_name, object_status)
        generate_doi = add_replace.get("generateDoi", '') or ''
        generate_doi = generate_doi.upper()
        dataset_description_mapped_to_status[uri] = Rdf2odpDatasetDescription(ckan_name, object_status,
                                                                              generate_doi)

        if 'DCATAP' != context.get('model', ''):
            # todo fix that with Daniel. create dataset based on old model
            # prepare the dataset object with migration function
            # old_model = dataset_transition_util.process_old_model(context, data_dict)
            # old_data_dict = logic.get_action('package_show')(context, {'id': data_dict.get('id')})
            # old_dataset = context['package']  # type: DatasetDcatApOp

            # dataset = DatasetDcatApOp(old_dataset.dataset_uri)
            pass

    embargo_dict, dataset_description_mapped_to_status = handle_uri_and_ckanName_generation(
        dataset_description_mapped_to_status, rdfFile)

    if embargo_dict is None:
        log.warn("Embargo graph is None")
        log.debug("Rdf file creating the embargo graph: {0}".format(rdfFile))
        log.debug("List of corresponding uris: {0}".format(dataset_description_mapped_to_status.keys()))
        rdf_error = {"validation_json_structure": {"rdfFile": "rdfFile value is incorrect"}}
        ret = {"fatal": rdf_error}
        report_dataset = {'errors': ret, 'status_save': False}
        global_report.append({"validation_rdfFile": report_dataset})
        raise ValidationError(report_dataset)

    stop_error = False
    for uri, dataset in embargo_dict.iteritems():
        report_dataset = {'errors': [], 'status_save': False}
        dataset_description = dataset_description_mapped_to_status.get(uri)  # type: Rdf2odpDatasetDescription
        status = dataset_description.status
        if dataset_description.ckan_name:
            dataset.schema.ckanName_dcatapop['0'] = ResourceValue(dataset_description.ckan_name)
        if status == DRAFT:
            dataset.privacy_state = DCATAPOP_PRIVATE_DATASET
        elif status == PUBLISHED:
            dataset.privacy_state = DCATAPOP_PUBLIC_DATASET

        else:
            log.warn(
                "Status of the dataset with uri {0} is neither draft nor published. Status: {1}".format(uri,
                                                                                                        dataset_description))
            # todo check if the default value is allowed
            dataset.privacy_state = STATUS_NOT_DEFINED
        ret = {}

        # add external URI as Identifier
        if dataset_description.external_uri:
            dataset.schema.identifier_dcterms[
                str(len(dataset.schema.identifier_dcterms.keys()))] = ResourceValue(
                dataset_description.external_uri)

        # check if provided rdf did contain a propper cataloge record

        if not dataset.schema_catalog_record.primaryTopic_foaf or not dataset.schema_catalog_record.primaryTopic_foaf.get('0', SchemaGeneric('')).uri == dataset.schema.uri:
            date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            dataset.schema_catalog_record.issued_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
            dataset.schema_catalog_record.modified_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
            dataset.schema_catalog_record.primaryTopic_foaf['0'] = SchemaGeneric(dataset.schema.uri)

        # todo check the business rule of validation
        ds, ret = validate_dacat_dataset(dataset)

        if ret.get('fatal', None):
            msg = "Validation of dataset with uri {0} has failed".format(uri)
            log.warn(msg)
            log.debug("dataset not validated : {0}".format(dataset))
            ret.pop('SUCCESS',None)
            #report_dataset = {'errors': ret,'status_save':False}
            global_report.append({uri:ret, 'status_save':False})
            stop_error = True
            #raise ValidationError(report_dataset, msg)
        if ret.get('error', None) and DCATAPOP_PUBLIC_DATASET == dataset.privacy_state:
            msg = "Dataset with validation errors can not be safed as published".format(uri)
            log.warn(msg)
            log.debug("dataset not validated : {0}".format(dataset))
            ret.pop('SUCCESS', None)
            # report_dataset = {'errors': ret,'status_save':False}
            global_report.append({uri: ret, 'status_save': False})
            stop_error = True
            # raise ValidationError(report_dataset, msg)
        id_dataset = dataset.dataset_uri.split('/')[-1]
        owner_org = dataset.get_publisher_acronym()
        _check_access('package_create', context, {'owner_org': owner_org})


    if stop_error:
        raise ValidationError(global_report)

    for uri, dataset in embargo_dict.iteritems():
        # select the method to add dataset, update or add new

        if not uri_util.is_uri_unique(uri):
            log.info('Dataset with uri {0} already exists'.format(uri))

        # check if the dataset exists
        id_dataset = dataset.dataset_uri.split("/")[-1]
        existing_dataset = None
        pkg_dict = {}
        try:
            pkg_dict = logic.get_action('package_show')(context, {'id': id_dataset})
            existing_dataset = context['package']  # type: DatasetDcatApOp
        except logic.NotFound:
            log.info("dataset not found in the system, a new one will be created. {0}".format(id_dataset))

        if existing_dataset:
            __check_for_doi_consistancy(dataset.schema.identifier_adms, existing_dataset.schema.identifier_adms)
            status_save = update_exisiting_dataset(dataset, existing_dataset, context, data_dict)

        else:
            status_save = add_new_dataset(dataset, context, data_dict)

        if status_save:
            report_dataset = {'errors': {}, 'status_save': True}
            log.info("Save Dataset successful. URI: {0}".format(uri))

        else:
            log.error("Save of dataset failded. URI: {0}".format(uri))
            # log.debug("dataset not saved : {0}".format(dataset))
            report_dataset = {'errors': {}, 'status_save': False}
            # TODO find the correct exception
            raise ValidationError(report_dataset, "Save the dataset Fails")

        pkg_dict = logic.get_action('package_show')(context, {'id': id_dataset})
        report_dataset["uri"] = dataset.dataset_uri
        report_dataset["publisher"] = dataset.schema.publisher_dcterms.get('0', SchemaGeneric).uri
        report_dataset["title"] = dataset.schema.get_resource_value_for_language('title_dcterms', 'en').value_or_uri
        report_dataset["capacity"] = dataset.privacy_state

        report_dataset["dataset"] = pkg_dict.get("dataset",{})
        report_dataset["rdfFile"] = pkg_dict.get("rdf","")

        global_report.append({uri: report_dataset})

    return global_report


def add_new_dataset(dataset, context, data_dict=None):

   """
    To add new dataset in the TS, Redis and solr
   :param DatasetDcatApOp dataset:
   :param context:
   :param data_dict:
   :return:
   """
   if not data_dict:
       data_dict = {}
   id_dataset = dataset.dataset_uri.split("/")[-1]
   if not dataset.schema.isPartOfCatalog_dcatapop:
      dataset.set_new_catalog()

   if dataset.privacy_state not in [DCATAPOP_INGESTION_DATASET, DCATAPOP_PUBLIC_DATASET,
                                    DCATAPOP_PRIVATE_DATASET]:
       dataset.privacy_state = DCATAPOP_PRIVATE_DATASET

   if not context.get("ignore_auth"):
       owner_org = dataset.get_publisher_acronym()
       _check_access('package_create', context, {'id': id_dataset,'owner_org':owner_org})
   context['package'] = dataset
   rev = model.repo.new_revision()
   rev.author = context.get("user")
   if 'message' in context:
       rev.message = context['message']

   try:
       save_to_ts_status = dataset.save_to_ts()

   except BaseException as e:
       log.error("Error while saving the package to Virtuoso.")

   if save_to_ts_status:
       context_org_update = context.copy()
       context_org_update['ignore_auth'] = True
       context_org_update['defer_commit'] = True
       _get_action = logic.get_action

       # get the id of the org
       org_uri = dataset.schema.publisher_dcterms['0'].uri  # type: str
       last_part = org_uri.split('/')[-1].lower()
       organization_name = last_part
       import ckan.model as ckan_model
       q_publisher = ckan_model.Session.query(ckan_model.Group) \
           .filter(ckan_model.Group.name == last_part)
       publisher = q_publisher.one()

       _get_action('package_owner_org_update')(context_org_update,
                                               {'id': dataset.schema.uri,
                                                'organization_id': publisher.id})
       if not context.get('defer_commit'):
           model.repo.commit()
       # Make sure that a user provided schema is not used on package_show
       context.pop('schema', None)
       return_id_only = context.get('return_id_only', False)
       output = context['id'] if return_id_only \
           else _get_action('package_show')(context, {'uri': dataset.dataset_uri})
       from ckanext.ecportal.lib.search.dcat_index import PackageSearchIndex as solar_package_index
       indexer = solar_package_index()
       indexer.update_dict(dataset)

       ckanext_helpers.wait_for_solr_to_update()
       pkgname = dataset.dataset_uri.split("/")[-1]
       log.info("Dataset imported succefully. [{0}] ".format(dataset.dataset_uri))
       return True

def update_exisiting_dataset(dataset, existing_dataset, context, data_dict=None, force_update=False):
    """
     To update exising dataset with the new content in the TS, Redis and solr
    :param DatasetDcatApOp dataset:
    :param DatasetDcatApOp existing_dataset:

    :param context:
    :param data_dict:
    :param Boolean force_update
    :return:
    """
    if not data_dict:
        data_dict = {}

    id_dataset = dataset.dataset_uri.split("/")[-1]
    existing_catalog_uri = existing_dataset.schema.isPartOfCatalog_dcatapop.get('0', SchemaGeneric('')).uri
    new_catalog_uri = dataset.schema.isPartOfCatalog_dcatapop.get('0', SchemaGeneric('')).uri

    context['for_view'] = False
    tmp_context = context.copy()
    tmp_context['model'] = model
    if not context.get("ignore_auth"):
        owner_org = dataset.get_publisher_acronym()
        _check_access('package_update', tmp_context, {'id': id_dataset,'owner_org':owner_org})
    if not existing_dataset:
        pkg_dict = logic.get_action('package_show')(context, {'id': id_dataset})
        existing_dataset = context['package']  # type: DatasetDcatApOp

    if not new_catalog_uri or new_catalog_uri != existing_catalog_uri:
        dataset.set_new_catalog(new_catalog_uri)
        existing_dataset.schema_catalog_record = dataset.schema_catalog_record

    # try to keep statistics of resources if force_update is false
    # force_update = True
    if not force_update:
        old_distribution_list = existing_dataset.schema.distribution_dcat.values()  # type: list[DistributionSchemaDcatApOp]
        if old_distribution_list:
            for schema in dataset.schema.distribution_dcat.values():  # type: DistributionSchemaDcatApOp
                old_res = None

                old_res = next(
                    (old_distr for old_distr in old_distribution_list if old_distr.uri == schema.uri), None)

                if old_res:
                    schema.uri = old_res.uri
                    schema.numberOfDownloads_dcatapop['0'] = old_res.numberOfDownloads_dcatapop.get('0', {})
                else:
                    uri = uri_util.new_distribution_uri()


    existing_dataset.schema = dataset.schema
    existing_dataset.schema_catalog_record = dataset.schema_catalog_record

    if dataset.privacy_state != STATUS_NOT_DEFINED:
        existing_dataset.privacy_state = dataset.privacy_state


    save_to_ts_status = existing_dataset.save_to_ts()
    if save_to_ts_status:
        context_org_update = context.copy()
        context_org_update['ignore_auth'] = True
        context_org_update['defer_commit'] = True

        rev = model.repo.new_revision()
        rev.author = context.get("user")
        if 'message' in context:
            rev.message = context['message']

        for item in plugins.PluginImplementations(plugins.IPackageController):
            item.edit(existing_dataset)

            item.after_update(context, existing_dataset)

        if not context.get('defer_commit'):
            model.repo.commit()

        log.debug('Updated object %s' % existing_dataset.dataset_uri)

        return_id_only = context.get('return_id_only', False)

        # Make sure that a user provided schema is not used on package_show
        context.pop('schema', None)
        redis_cache.set_value_no_ttl_in_cache(existing_dataset.dataset_uri, pickle.dumps(existing_dataset))
        redis_cache.flush_all_from_db(redis_cache.MISC_POOL)
        try:
            status_index = search.rebuild(existing_dataset.dataset_uri.split('/')[-1])
        except BaseException as e:
            log.error("update_exisiting_dataset [Failed indexation] for {0}".format(dataset.dataset_uri))
            return False
        # we could update the dataset so we should still be able to read it.
        context['ignore_auth'] = True
        output = data_dict['id'] if return_id_only \
            else _get_action('package_show')(context, {'id': id_dataset})

        return True
    else:
        log.error("update_exisiting_dataset [Failed save to TS] for {0}".format(dataset.dataset_uri))
        return False


def __check_for_doi_consistancy(identifier_dict, old_identifier_dict):
    """

    :param dict[str, IdentifierSchemaDcatApOp] identifier_dict:
    :param dict[str, IdentifierSchemaDcatApOp] old_identifier_dict:
    :return:
    """

    consistent_doi = False
    old_doi = None
    for identifier in old_identifier_dict.values():
        if hasattr(identifier, "notation_skos"):
            notation = next((notation for notation in identifier.notation_skos.values() if notation.datatype == controlled_vocabulary_util.DOI_URI or notation.datatype.lower() == 'http://purl.org/spar/datacite/doi'.lower()),None) #type: ResourceValue
            if notation:
                doi = notation.value_or_uri
                break

    if not old_doi:
        return

    for identifier in identifier_dict.values():
        if hasattr(identifier, "notation_skos"):
            notation = next((notation for notation in identifier.notation_skos.values() if notation.datatype == controlled_vocabulary_util.DOI_URI or notation.datatype.lower() == 'http://purl.org/spar/datacite/doi'.lower()) and notation.value_or_uri == old_doi,None) #type: ResourceValue
            if notation:
                consistent_doi = True
                break

    if not consistent_doi:
        report_dataset = {'errors': {'identifier_adms': 'DOI is not consistent'}, 'status_save': False}
        raise ValidationError(report_dataset, "Save the dataset Fails")


def handle_uri_and_ckanName_generation(dataset_description_mapped_to_status, rdfFile):
    '''

    :param dict[str, DatasetDcatApOp] embargo_dict:
    :param dict[str,Rdf2odpDatasetDescription] dataset_description_mapped_to_status:
    :param unicode rdfFile:
    :return:
    '''
    ingestion_helper = TripleStoreIngestionHelpers()

    for action_uri in dataset_description_mapped_to_status.keys():
        if not action_uri in rdfFile:
            rdf_error = {"validation_json_structure": {
                "rdfFile": "rdfFile value is incorrect. The objectUri value does not exixt in the RDF"}}
            ret = {"fatal": rdf_error}
            report_dataset = {'errors': ret, 'status_save': False}
            raise ValidationError(report_dataset)
            # raise ValidationError('Action URI {0} is not in RDF file'.format(action_uri))

    embargo_dict = ingestion_helper.build_embargo_datasets_from_string_content(rdfFile,
                                                                               dataset_description_mapped_to_status, doi_flag=False)  # type_ dict[str, DatasetDcatApOp]
    if not embargo_dict:
        return None, dataset_description_mapped_to_status

    for uri, dataset in embargo_dict.items():

        dataset_description = dataset_description_mapped_to_status.get(uri) #type: Rdf2odpDatasetDescription
        if not URI_TEMPLATE +'/dataset' in uri:
            ckan_name = dataset.schema.ckanName_dcatapop.get('0', ResourceValue('')).value_or_uri
            # create
            if not ckan_name:
                new_uri, ckan_name = uri_util.new_dataset_uri_from_title(next(
                    (title.value_or_uri for title in dataset.schema.title_dcterms.values() if
                     not title.lang or title.lang == 'en'), ''))
                dataset_description.ckan_name = ckan_name
            else:
                new_uri = uri_util.new_dataset_uri_from_name(ckan_name)

            dataset_description.ckan_name = ckan_name
            dataset_description.external_uri = uri
            dataset_description_mapped_to_status.pop(uri, None)
            dataset_description_mapped_to_status[new_uri] = dataset_description
            rdfFile = rdfFile.replace(uri, new_uri)

    embargo_dict = ingestion_helper.build_embargo_datasets_from_string_content(rdfFile,
                                                                               dataset_description_mapped_to_status)

    return embargo_dict, dataset_description_mapped_to_status
