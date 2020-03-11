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

import datetime
import json
import logging
import time

import ckan.plugins as plugins
from rdflib import Graph
from rdflib import XSD
from pylons import config

import ckanext.ecportal.lib.dataset_util as dataset_util
import ckanext.ecportal.lib.uri_util as uri_util
from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.model.schema_validation.schema_validation import ValidationSchema
from ckanext.ecportal.model.schema_validation.validation_type_result import ValidationTypeResult
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP, CatalogRecordSchemaDcatApOp, DataThemeSchemaDcatApOp, \
    DatasetSchemaDcatApOp, DistributionSchemaDcatApOp, DocumentSchemaDcatApOp, FrequencySchemaDcatApOp, \
    ProvenanceStatementSchemaDcatApOp, StandardSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_identifier_schema import IdentifierSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_revision_schema import RevisionSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.model.catalog_dcatapop import CatalogSchemaDcatApOp
from ckanext.ecportal.model.utils_convertor import ConvertorFactory
from ckanext.ecportal.model.utils_convertor import Dataset_Convertor
from ckanext.ecportal.model.schemas.dcatapop_data_extension_schema import DataExtensionSchemaDcatApOp
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
from ckanext.ecportal.model.schema_wrapper_interface import ISchemaWrapper
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import RightsStatementSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_agent_schema import AgentSchemaDcatApOp
from ckanext.ecportal.lib import controlled_vocabulary_util
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH
import ckanext.ecportal.helpers as ckan_helper
import ckan.lib.base as base

from ckanext.ecportal.model.common_constants import DEFAULT_CATALOG_URI
import ckan.plugins as p

log = logging.getLogger(__file__)
abort = base.abort

import logging
import traceback

NOTATION_MAPPING = dataset_util.NOTATION_MAPPING

logging.basicConfig(level=logging.DEBUG)


class DatasetDcatApOp(object):
    p.implements(ISchemaWrapper)

    def __init__(self, dataset_uri, privacy_state=DCATAPOP_PUBLIC_DATASET, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME,
                 data_dict=None):
        '''

        :param str dataset_uri:
        :param str privacy_state:
        :param str graph_name:
        :param data_dict:
        '''
        self.dataset_uri = dataset_uri
        self.graph_name = graph_name
        self.schema = DatasetSchemaDcatApOp(dataset_uri, graph_name)
        self.schema_catalog_record = {}  # type: CatalogRecordSchemaDcatApOp
        self.privacy_state = privacy_state
        self.__last_revision = None
        self.ttl_as_in_ts = ""
        if data_dict:
            self.__dict__.update(data_dict)
        pass
        self.__final_description_dict = dict()  # type: dict[str,dict[str,ResourceValue|SchemaGeneric]]
        # self.__final_graph_of_dataset = Graph()

    def set_state_as_public(self):
        self.graph_name = DCATAPOP_PUBLIC_GRAPH_NAME
        self.privacy_state = DCATAPOP_PUBLIC_DATASET

    def set_state_as_private(self):
        self.graph_name = DCATAPOP_PRIVATE_GRAPH_NAME
        self.privacy_state = DCATAPOP_PRIVATE_DATASET

    def get_description_from_ts(self):
        """
        Get the dataset from triples store
        Returns true if the action is done, otherwise None of False.
        :rtype Boolean:
        """
        try:

            self.schema_catalog_record = {}
            self.schema = DatasetSchemaDcatApOp(self.dataset_uri, self.graph_name)
            self.schema_catalog_record = CatalogRecordSchemaDcatApOp("")

            desc_ds = self.schema.get_description_from_ts()
            if desc_ds is None:
                return False
            if len(desc_ds) == 0:
                return False
            self.__final_description_dict = desc_ds
            desc_catalog = self.get_catalog_record_from_ts()
            if DCATAPOP_PRIVATE_GRAPH_NAME == self.graph_name:
                self.privacy_state = DCATAPOP_PRIVATE_DATASET
            if desc_catalog is None:
                log.error(
                    "[Dataset]. Get description from TS failed for the catalog record [{0}]".format(self.dataset_uri))
            # save the content of the dataset as a graph. To be used when updating the dataset in the triples store
            self.ttl_as_in_ts = self.build_the_graph().serialize(format="nt")
            log.info("[Dataset]. Get description from Triples store successful <{0}>".format(self.dataset_uri))
            return True
        except BaseException as e:
            import traceback
            log.error(traceback.print_exc(e))
            log.error("[Dataset]. Get description from Triples store failed. URI: <{0}>".format(self.dataset_uri))
            return False

    def save_to_ts(self, revision_id=None):
        """
        To insert or update the description of the dataset in the TS.
        all the existing description in TS will be removed.
        :rtype: Boolean
        """
        try:
            start = time.time()
            tsch = TripleStoreCRUDHelpers()
            source_graph = self.graph_name
            target_graph_to_save = DCATAPOP_PUBLIC_GRAPH_NAME
            if self.privacy_state not in [DCATAPOP_PRIVATE_DATASET, DCATAPOP_PUBLIC_DATASET,DCATAPOP_INGESTION_DATASET]:
                self.privacy_state = DCATAPOP_PRIVATE_DATASET

            if self.privacy_state == DCATAPOP_PRIVATE_DATASET:
                target_graph_to_save = DCATAPOP_PRIVATE_GRAPH_NAME

            if self.privacy_state == DCATAPOP_INGESTION_DATASET:
                target_graph_to_save = self.graph_name

            ttl_ds_from_ts = self.ttl_as_in_ts
            ttl_ds_last_version = self.build_the_graph().serialize(format="nt")
            #last check of validity
            if len(ttl_ds_last_version.splitlines()) < MINIMUM_SIZE_VALIDE_DATASET:
                log.error("[Dataset] [Save dataset failed] [Minimum size of dataset is incorrect] [URI:<{0}>]".
                          format(self.dataset_uri))
                return False

            result_execution_querry = tsch.transactional_update_big_dataset(source_graph,target_graph_to_save,ttl_ds_from_ts,ttl_ds_last_version)
            if result_execution_querry:
                duration = time.time() - start
                log.info("[Dataset] [Save dataset successful] [Duration:<{1}>] [URI:<{0}>]".format(self.dataset_uri,duration))
                self.ttl_as_in_ts = ttl_ds_last_version
                if self.privacy_state == DCATAPOP_PRIVATE_DATASET:
                    self.graph_name = DCATAPOP_PRIVATE_GRAPH_NAME
                elif self.privacy_state == DCATAPOP_PUBLIC_DATASET:
                    self.graph_name = DCATAPOP_PUBLIC_GRAPH_NAME
                last_revision = self.create_revision(revision_id)
            else:
                log.info("[Dataset]. [Save dataset failed] [URI:<{0}>]".format(self.dataset_uri))
            return result_execution_querry
        except BaseException as e:
            log.error("[Dataset]. Save dataset failed [{0}]]".format(self.dataset_uri))
            log.error(traceback.print_exc(e))
            return False

    def delete_from_ts(self):
        """
        To delete the dataset from the TS
        :rtype: Boolean
        """
        try:
            tsch = TripleStoreCRUDHelpers()
            source_graph = self.graph_name
            ttl_ds_from_ts = self.ttl_as_in_ts
            rollback_graph = tsch.create_name_of_graph(ttl_ds_from_ts)
            # status = tsch.execute_delete_ttl(source_graph, ttl_ds_from_ts)
            status = tsch.delete_big_ttl_transaction(source_graph,ttl_ds_from_ts, rollback_graph)

            if status:
                # initialization of the schemas
                self.schema_catalog_record = {}
                self.schema = DatasetSchemaDcatApOp(self.dataset_uri, self.graph_name)
                self.ttl_as_in_ts = ""
                log.info("[Dataset]. [delete dataset from ts] [successful] [uri:<{0}>]".format(self.dataset_uri))
                return True
            else:
                log.info("[Dataset]. [delete dataset from ts] [failed[ [uri:<{0}>]. [Message from TS: {1}]".format(
                    self.dataset_uri, tsch.get_virtuoso_query_return()))
                return False

        except BaseException as e:
            log.error("[Dataset]. [delete dataset from ts] [failed]. [uri:<{0}>]".format(self.dataset_uri))
            log.error(traceback.print_exc(e))
            return None

    def build_the_graph(self):
        """
        To build the RDFlib graph of the dataset based on the schema ( pricipal + catalog record)
        :rtype: Graph|None
        """
        try:
            dataset_graph = Graph()
            graph_dataset_schema = None
            graph_catalog_record_schema = None
            if self.schema:
                graph_dataset_schema = self.schema.convert_to_graph_ml()
                # dataset_graph = graph_dataset_schema
            if self.schema_catalog_record:
                graph_catalog_record_schema = self.schema_catalog_record.convert_to_graph_ml()
                # dataset_graph = graph_dataset_schema + graph_catalog_record_schema

            if graph_dataset_schema and graph_catalog_record_schema:
                dataset_graph = graph_dataset_schema + graph_catalog_record_schema
                return dataset_graph
            elif not graph_catalog_record_schema:  # TODO: add restriction of that. One accepts at this moment the geration of the graph
                dataset_graph = graph_dataset_schema
                log.warning("[Dataset]. build the graph without catalog record [{0}]".format(self.dataset_uri))
                return dataset_graph

        except BaseException as e:
            log.error("[Dataset]. build the graph failed [{0}]".format(self.dataset_uri))
            return None

    def get_dataset_as_rdfxml(self):
        """
        get the rdf version of the current dataset's content with the binding of namespaces

        :rtype: str
        """
        try:
            # Get the catalog description to be added forthe export only
            from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
            catalog_of_dataset = self.schema.isPartOfCatalog_dcatapop.get('0', None)
            graph_of_dataset = Graph()
            graph_of_dataset = self.build_the_graph()
            final_graph_of_dataset = NAMESPACE_DCATAPOP.bind_graph_with_namesspace(graph_of_dataset)
            graph_as_xml = final_graph_of_dataset.serialize(format="xml")
            #  TODO restore the value of the ispartOfCatalog
            # self.schema.isPartOfCatalog_dcatapop = None

            return graph_as_xml
        except BaseException as e:
            import traceback
            log.error("Get Data as xml failed. Dataset [uri:{0}]".format(self.dataset_uri))
            log.error(traceback.print_exc(e))
            return None

    def get_dataset_as_json(self):
        """
        get the rdf version of the current dataset's content with the binding of namespaces

        :rtype: str
        """
        try:
            graph_of_dataset = Graph()
            graph_of_dataset = self.build_the_graph()
            dataset_dict = self.schema.export_to_json()
            json_dataset = json.dumps(dataset_dict, ensure_ascii=False).encode('utf8')
            return json_dataset
        except BaseException as e:
            log.error("Get Data as json failed. Dataset [uri:{0}]".format(self.dataset_uri))
            return None

    def build_DOI_dict(self):
        '''
        Generate the dict that will be used by the DOI package
        :return dict:
        '''

        try:

            dataset_dict = self.schema.build_DOI_dict_from_schema()
            # convert to DOI dict
            log.info("build the DOI dict successful for dataset {0} ".format(self.dataset_uri))
            return dataset_dict
        except BaseException as e:
            log.error("build the DOI dict failed for dataset {0} ".format(self.dataset_uri))

    def create_revision(self, revision_id=None):
        """
        return the uri of the revision
        :rtype str :
        """
        try:
            new_revision = RevisionSchemaDcatApOp(self, "api", revision_id=revision_id)
            if new_revision:
                log.info('[Dataset]. Revision saved for dataset {0}. Revision uri: {1}'.format(self.dataset_uri, new_revision.uri))
                return new_revision
            else:
                log.error("[Dataset]. Creation of Dataset revision failed. uri: {0}".format(self.dataset_uri))
                return None
        except BaseException as e:
            log.error("[Dataset]. Creation of Dataset revision failed. uri: {0}".format(self.dataset_uri))
            return None

    def get_last_revision(self):
        try:
            return self.__last_revision
        except BaseException as e:
            return None

    def get_list_revisions_as_uris(self, number_revisions=9999):
        """
        return a list of URIs of revisions related to the current dataset
        <http://data.europa.eu/88u/revision#isRevisionOf>
        :rtype List[str]:
        """
        try:
            tsch = TripleStoreCRUDHelpers()

            isRevisionOf_uri = NAMESPACE_DCATAPOP.revision + "isRevisionOf"
            sparql_query = "SELECT distinct ?revision_uri from <{0}> WHERE {{ " \
                           "?revision_uri  <{1}> <{2}> ." \
                           "?revision_uri <http://data.europa.eu/88u/revision#timestamp> ?date " \
                           "}}" \
                           "ORDER BY DESC (?date)" \
                           "".format(DCATAPOP_REVISION_GRAPH_NAME, isRevisionOf_uri, self.dataset_uri)
            result = tsch.execute_select_query_auth(sparql_query)
            list_revisoins_uri = [revision['revision_uri']['value'] for revision in result]
            list_revisoins_uri = list_revisoins_uri[:number_revisions]
            return list_revisoins_uri
        except BaseException as e:
            log.error("[Dataset] [get list of revisions] [Failed] [Dataset:<{0}>]".format(self.dataset_uri))
            return None

    def get_list_revisions(self):
        """
        return the list of revisions related to  of the revision related to the current dataset
        <http://data.europa.eu/88u/revision#isRevisionOf>
        :rtype dict[str,dict[str,RevisionSchemaDcatApOp]]:
        """
        try:
            import pickle
            import base64
            list_revisions = {}  # type: dict[str, RevisionSchemaDcatApOp]
            for revision_uri in self.get_list_revisions_as_uris():
                rev = RevisionSchemaDcatApOp("", uri_direct=revision_uri)
                rev.get_description_from_ts()
                # the content is the base64 of the pickle
                dataset_content = str(base64.decodestring(str(rev.contentDataset_revision['0'].value_or_uri)))
                ds = pickle.loads(dataset_content)

                list_revisions[revision_uri] = {"revision": rev, "dataset": ds}
            return list_revisions
        except BaseException as e:
            log.error(e)
            log.error("Dataset: get list revisions failed for dataset {0}".format(self.dataset_uri))
            return {}

    def get_list_revisions_ordred(self, number_revisions = 9999):
        """
        return the list of revisions related to  of the revision related to the current dataset
        <http://data.europa.eu/88u/revision#isRevisionOf>
        :rtype dict[str,dict[str,RevisionSchemaDcatApOp]]:
        """
        try:
            import pickle
            import base64
            list_revisions = {}  # type: dict[str, RevisionSchemaDcatApOp]
            list_revisions_ordred = []
            for revision_uri in self.get_list_revisions_as_uris(number_revisions):
                rev = RevisionSchemaDcatApOp("", uri_direct=revision_uri)
                rev.get_description_from_ts()
                #the content is the base64 of the pickle
                dataset_content = str(base64.decodestring(str(rev.contentDataset_revision['0'].value_or_uri)))
                ds= pickle.loads(dataset_content)
                date_rev = rev.timestamp_revision.get('0').value_or_uri
                list_revisions[date_rev] = {"revision":rev,"dataset":ds}
                list_revisions_ordred.append({"revision":rev,"dataset":ds})
            return list_revisions_ordred
        except BaseException as e:
            log.error(e)
            log.error("Dataset: get list revisions failed for dataset {0}".format(self.dataset_uri))
            return {}

    def add_draft_to_title(self, prefix_str="(draft)"):
        """
        add (draft) o the title , if it doesn't exist already
        :param prefix_str:
        :return:
        """
        try:
            for titleDS in self.schema.title_dcterms.values() or {}:
                if titleDS.lang == "en":
                    title_str = titleDS.value_or_uri
                    if prefix_str not in title_str[:len(prefix_str)]:  # add only if there is no prefix
                        titleDS.value_or_uri = "{0} {1}".format(prefix_str, title_str)
                    return True
        except BaseException as e:
            log.error("Can not prefix the title with draft. Dataset: {0}".format(self.dataset_uri))
            return False

    def optimize_update_properties_value(self, graph_name):
        """
        update values of the selected properties and keep the other properties in the model.
        :param graph_name:
        :return:
        """
        pass

    def get_catalog_record_from_ts(self):
        """
        :rtype CatalogRecordSchemaDcatApOp:
        """
        try:
            tsch = TripleStoreCRUDHelpers()
            sparql_query = "select distinct(?s) from <{0}> " \
                           " where {{" \
                           "?s <http://xmlns.com/foaf/0.1/primaryTopic> <{1}>. " \
                           " ?s a <http://www.w3.org/ns/dcat#CatalogRecord>. " \
                           "}}".format(self.graph_name, self.dataset_uri)
            result = tsch.execute_select_query_auth(sparql_query)
            uri_catalog_record = result[0]['s']['value']
            self.schema_catalog_record = CatalogRecordSchemaDcatApOp(uri_catalog_record, graph_name=self.graph_name)
            return self.schema_catalog_record.get_description_from_ts()

        except BaseException as e:
            return None

    def get_schema_contact_point(self):
        try:

            dict_schema = self.schema.contactPoint_dcat  # KindSchemaDcatApOp
            for key, value in dict_schema.iteritems():
                value.get_description_from_ts()

            # Now get the information property by property
            # self.write_address_description_in_dict_schema(dict_schema)
            # self.write_telephone_description_in_dict_schema(dict_schema)
            # self.write_homepage_description_in_dict_schema(dict_schema)
            return self.schema.contactPoint_dcat
        except BaseException as e:
            import traceback
            log.error('{0}'.format(e))
            log.error(traceback.print_exc())
            return None

    def get_telephones(self):
        result_dict = {}
        try:
            if self.schema.contactPoint_dcat:
                for i, contactPoint in self.schema.contactPoint_dcat.iteritems():
                    if contactPoint.hasTelephone_vcard:
                        result_dict[i] = contactPoint.hasTelephone_vcard
                return result_dict
        except BaseException as e:
            None

    def get_telephone_numbers(self):
        try:
            result_dict = {}
            tels = self.get_telephones()
            if tels:
                for i, tel in tels.iteritems():
                    if tel['0'].hasValue_vcard:
                        result_dict[i] = tel['0'].hasValue_vcard['0'].uri
                return result_dict
        except BaseException as e:
            None

    def get_address(self):
        result_dict = {}
        try:
            if self.schema.contactPoint_dcat:
                for i, contactPoint in self.schema.contactPoint_dcat.iteritems():
                    if contactPoint.hasAddress_vcard:
                        result_dict[i] = contactPoint.hasAddress_vcard
                return result_dict
        except BaseException as e:
            None

    def get_owner_org(self):
        return self.schema.publisher_dcterms.get('0', SchemaGeneric('')).uri

    def validate_dataset(self):
        """
        To validate the dataset and return a report of validation.
        the report is a dict with two keys: remark, and final_report which is an array. Each element of final_report is
        the result the validation for each validation rule.
        :rtype: dict
        """
        try:
            start = time.time()
            path_json_validation_rules = config.get('ecodp.validation_rules.file', CKAN_PATH + '/ckanext-ecportal/ckanext/ecportal/model/schema_validation/validation_rules.json')

            validation_rules = ValidationSchema.extract_validation_rules_from_file(path_json_validation_rules)
            ValidationSchema.validation_structre_rules = None

            report_validation_dataset = self.schema.validate_schema(validation_rules)
            report_validation_catalog_record = self.schema_catalog_record.validate_schema(validation_rules)

            final_report = []  # type: list[dict[str,str]]
            if report_validation_dataset and report_validation_catalog_record:
                remark = 'ok'
                final_report = report_validation_dataset + report_validation_catalog_record
            else:
                if report_validation_dataset:
                    final_report = report_validation_dataset
                    log.warning(
                        "[Dataset]. Validation of Dataset. validation of dataset principal schema failed [uri: {0}]".format(
                            self.dataset_uri))
                if report_validation_catalog_record:
                    final_report = report_validation_catalog_record
                    log.warning(
                        "[Dataset]. Validation of Dataset. Validation of dataset catalog record schema failed [uri: {0}].".format(
                            self.schema_catalog_record.uri))

            # convert the list to be used by the controler
            # validation_result = {} # type: dict
            final_validation_dataset_report = {ValidationTypeResult.fatal: [], ValidationTypeResult.error: [],
                                               ValidationTypeResult.warning: [], ValidationTypeResult.success: []}

            for validation_result in final_report:
                result = validation_result.get('result')
                level = validation_result.get('level_of_error')
                mandatory_rule = validation_result.get('mandatory', 'no')
                mandatory = False
                if mandatory_rule in "yes":
                    mandatory = True

                error_type = result
                if result == ValidationTypeResult.error and mandatory:
                    error_type = ValidationTypeResult.fatal
                if result == ValidationTypeResult.error and not mandatory and level in ValidationTypeResult.warning:
                    error_type = ValidationTypeResult.warning

                final_validation_dataset_report[error_type].append(validation_result)

            # remove the success part
            final_validation_dataset_report.pop(ValidationTypeResult.success, None)

            duration = time.time() - start

            log.info("Validation Dataset. Duration {1}. URI. [{0}]".format(self.dataset_uri, duration))
            return final_validation_dataset_report

        except BaseException as e:
            log.error("[Dataset]. Validation failed of the dataset [uri: {0}]".format(self.dataset_uri))
            log.error(traceback.print_exc(e))
            return None

    def create_multi_lang_full_text(self, graph=None):
        """
        To create the full text value of a graph based on literal nodes only. The result is a dict with for each key "lang" an aggregated string value
        of all literal with the language
        the case of literal without language is treated by using the NO_Languages key
        :param Graph graph:
        :rtype: dict
        """
        try:

            if not graph:
                graph_dataset = self.build_the_graph()
            else:
                graph_dataset = graph
            full_text_multi_lang_dataset = ConvertorFactory.create_multi_lang_full_text_field(graph_dataset)
            log.info("[Dataset]. create_multi_lang_full_text successful. [uri: {0}]".format(self.dataset_uri))
            return full_text_multi_lang_dataset
        except BaseException as e:
            log.error("[Dataset]. create_multi_lang_full_text failed. [uri: {0}]".format(self.dataset_uri))
            return None

    def create_dataset_schema_for_package_dict(self, data_dict, errors, context):

        # Catalog Record
        catalogRecord = CatalogRecordSchemaDcatApOp(uri_util.new_catalog_record_uri())
        date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        catalogRecord.issued_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
        catalogRecord.modified_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
        catalogRecord.primaryTopic_foaf['0'] = SchemaGeneric(self.schema.uri)

        self.schema_catalog_record = catalogRecord
        if data_dict.get('name',None):
            self.schema.ckanName_dcatapop['0'] = ResourceValue(data_dict.get('name'))

        self.__set_schema_values_from_dict(data_dict, errors, context)

    def patch_dataset_for_package_dict(self, data_dict, errors, context):

        date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.schema_catalog_record.modified_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
        context['old_dataset'] = self.schema  # needed for keeping the resource ids
        self.__set_schema_values_from_dict(data_dict, errors, context)

    def update_dataset_for_package_dict(self, data_dict, errors, context):

        date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.schema_catalog_record.modified_dcterms = {}
        self.schema_catalog_record.modified_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
        self.schema_catalog_record.numberOfViews_dcatapop = {'0': max(self.schema_catalog_record.numberOfViews_dcatapop.values() or  [ResourceValue("0")] , key=lambda x: int(x.value_or_uri))}
        context['old_dataset'] = self.schema #needed for keeping the resource ids
        self.schema = DatasetSchemaDcatApOp(self.dataset_uri)
        self.__set_schema_values_from_dict(data_dict, errors, context)
        pass

    def __set_schema_values_from_dict(self, data_dict, errors, context):

        private = (data_dict.get('private', 'False'))
        # Privacy state
        if 'False' == private:
            self.privacy_state = DCATAPOP_PUBLIC_DATASET
            # self.graph_name = DCATAPOP_PUBLIC_GRAPH_NAME
            # self.set_state_as_public()
        elif 'True' == private:
            self.privacy_state = DCATAPOP_PRIVATE_DATASET
            # self.graph_name = DCATAPOP_PUBLIC_GRAPH_NAME
            # self.set_state_as_private()

        convertor = Dataset_Convertor()

        # Title
        self.set_title(convertor, data_dict)

        # Alternative-Title
        self.set_alternative_titles(convertor, data_dict)

        # Description
        self.set_descriptions(convertor, data_dict)

        # Publisher
        dataset_util.set_publisher_to_dataset_from_dict(self, data_dict)

        # Creator
        self.set_creator(data_dict)

        # Accrual Periodicity
        self.set_frequency(data_dict)

        # Groups
        self.set_groups(convertor, data_dict)

        # Contact
        self.set_contact(convertor, data_dict)

        # DOI
        self.set_doi(data_dict.get('doi', None))

        # Geographical Coverage
        self.set_geographical_coverage(convertor, data_dict)

        # Eurovoc_domains
        self.set_themes(convertor, data_dict)

        # Identifier
        self.set_identifier(data_dict)

        # Other Identifier
        self.set_other_identifier(data_dict)

        # Interoperability_level - Removed

        # Controlled Keywords
        self.set_controlled_keyword(convertor, data_dict)

        # Keywords
        self.set_keyword_string(convertor, data_dict)

        # Language
        self.set_language(convertor, data_dict)

        # Metadata language - Removed

        # Modified date
        self.set_modified_date(data_dict)

        # Name
        self.set_name(data_dict)

        # Owner org - removed from dataset

        # Release_date
        self.set_release_date(data_dict)

        # TODO: Status - Moved to Distributions

        # Temporal coverage
        self.set_temporal_coverage(convertor, data_dict)

        # Temporal granularity
        # TODO: need to define the class
        self.set_temporal_granularity(data_dict)

        # Landing Page
        self.set_landing_page(data_dict)

        # Type of dataset
        self.set_type_dataset(convertor, data_dict)

        # Version
        self.set_version(data_dict)

        # Version notes
        self.set_version_notes(convertor, data_dict)

        # Resources
        self.set_resources(convertor, data_dict, context)

        # TODO: @Daniel, I had to remove this as it caused error: is_open is not defined in the resource
        # for dist in self.schema.distribution_dcat.values():
        #     for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
        #         item.notify(dist)

        # Source
        self.set_source(data_dict)

        # Provenance
        self.set_provenances(data_dict)

        # Conforms to
        self.set_conforms_to(data_dict)

        # Sample
        self.set_samples(data_dict)

        # Is Version Of
        self.set_is_version_of(data_dict)

        # Has Version
        self.set_has_version(data_dict)

        # Is Part Of
        self.set_is_part_of(data_dict)

        # Has Part
        self.set_has_part(data_dict)

        #Catalog isPartOfCatalog_dcatapop
        if data_dict.get('catalog'):
            self.set_is_part_of_Catalog(data_dict)

        # Related Resource
        self.set_related_resource(data_dict)

        # Related Application
        self.set_related_application(data_dict)

        # StatDcat - AP
        self.set_attribute(convertor, data_dict)
        self.set_dimension(convertor, data_dict)
        self.set_number_of_data_series(convertor, data_dict)
        self.set_quality_annotation(convertor, data_dict)
        self.set_unit_of_measurement(convertor, data_dict)

        self.set_extra_metadata(data_dict)

    def set_unit_of_measurement(self, convertor, data_dict):
        unit_of_measurement = convertor.set_splitted_uris(data_dict, 'unit_of_measurement')
        if unit_of_measurement:
            self.schema.statMeasure_stat = unit_of_measurement

    def set_quality_annotation(self, convertor, data_dict):
        quality_annotation = convertor.set_splitted_uris(data_dict, 'quality_annotation')
        if quality_annotation:
            self.schema.hasQualityAnnotation_dqv = quality_annotation

    def set_number_of_data_series(self, convertor, data_dict):
        number_of_data_series = convertor.set_splitted_labels(data_dict, 'number_of_data_series')
        if number_of_data_series:
            self.schema.numSeries_stat = number_of_data_series

    def set_dimension(self, convertor, data_dict):
        dimension = convertor.set_splitted_uris(data_dict, 'dimension')
        if dimension:
            self.schema.dimension_stat = dimension

    def set_attribute(self, convertor, data_dict):
        attribute = convertor.set_splitted_uris(data_dict, 'attribute')
        if attribute:
            self.schema.attribute_stat = attribute

    def set_themes(self, convertor, data_dict):
        themes = convertor.convert_theme_dcat(data_dict, 'theme', self.schema.theme_dcat)
        if themes:
            self.schema.theme_dcat = themes

    def set_geographical_coverage(self, convertor, data_dict):
        geographical_coverage = convertor.convert_spatial(data_dict.get('geographical_coverage'))
        if geographical_coverage:
            self.schema.spatial_dcterms = geographical_coverage

    def set_contact(self, convertor, data_dict):
        contact_point = convertor.convert_contact_point(data_dict.get('contact_address'),
                                                        data_dict.get('contact_email'),
                                                        data_dict.get('contact_name'),
                                                        data_dict.get('contact_telephone'),
                                                        data_dict.get('contact_webpage'))
        if contact_point:
            self.schema.contactPoint_dcat = contact_point

    def set_groups(self, convertor, data_dict):
        groups = convertor.convert_groups(data_dict.get('groups'))
        if groups:
            self.schema.datasetGroup_dcatapop = groups

    def set_title(self, convertor, data_dict):
        title = convertor.convert_translations_of_parameters(data_dict, 'title')
        if title:
            self.schema.title_dcterms = title

    def set_alternative_titles(self, convertor, data_dict):
        alternative_titles = convertor.convert_translations_of_parameters(data_dict, 'alternative_title')
        if alternative_titles:
            changed_alternative_titles = set(alternative_titles.values()) - set(self.schema.alternative_dcterms.values())
            for changed_alternative_title in changed_alternative_titles:
                is_found = False
                for key, value in self.schema.alternative_dcterms.iteritems():
                    is_found = value.lang == changed_alternative_title.lang
                    if is_found:
                        self.schema.alternative_dcterms[key] = changed_alternative_title
                        break
                if not is_found:
                    length = len(self.schema.alternative_dcterms)
                    self.schema.alternative_dcterms[str(length)] = changed_alternative_title

    def set_descriptions(self, convertor, data_dict):
        # TODO : what must be done if description == None and description-{lang} exists
        descriptions = convertor.convert_translations_of_parameters(data_dict, 'description')
        if descriptions:
            changed_descriptions = set(descriptions.values()) - set(self.schema.description_dcterms.values())
            for changed_description in changed_descriptions:
                is_found = False
                for key, value in self.schema.description_dcterms.iteritems():
                    is_found = value.lang == changed_description.lang
                    if is_found:
                        self.schema.description_dcterms[key] = changed_description
                        break
                if not is_found:
                    length = len(self.schema.description_dcterms)
                    self.schema.description_dcterms[str(length)] = changed_description

    def set_has_part(self, data_dict):
        has_part = data_dict.get('has_part')
        if has_part:
            self.schema.hasPart_dcterms = {}
            for has_part_uri in has_part.split(" "):
                if has_part_uri:
                    # if uri_util.is_uri_valid(has_part_uri):
                    has_part_length = str(len(self.schema.hasPart_dcterms))
                    self.schema.hasPart_dcterms[has_part_length] = SchemaGeneric(has_part_uri)
                # else:
                #    raise Exception("Url [{0}] is not valid".format(has_part_uri))

    def set_other_identifier(self, data_dict):
        lemon_contexts = controlled_vocabulary_util.retrieve_all_notation_skos()
        other_identifier = data_dict.get('other_identifier')
        other_identifier_type = data_dict.get('other_identifier_type', None) #or XSD.string

        if other_identifier:
            other_identifiers = []
            if isinstance(other_identifier, basestring):
                other_identifiers = other_identifier.split(" ")
            elif isinstance(other_identifier, list):
                other_identifiers = other_identifier
            # Special case for bulf edit
            doi = self.get_doi()
            if not doi:
                self.schema.identifier_adms = {}
            else:
                self.schema.identifier_adms = {'0':doi}

            for other_identifier in other_identifiers:
                if other_identifier:
                    # if uri_util.is_uri_valid(other_identifier):
                    source_length = str(len(self.schema.identifier_adms))
                    if data_dict.get('owner_org'):
                        org = ckan_helper.get_organization({"id": data_dict.get('owner_org')})
                        org_name = org[1]
                    else:
                        org_name = self.get_publisher_acronym()
                    other_type = NOTATION_MAPPING.get(other_identifier_type,'')
                    identifier = IdentifierSchemaDcatApOp(uri_util.create_uri_for_schema(IdentifierSchemaDcatApOp))
                    identifier.notation_skos = {"0": ResourceValue(other_identifier, datatype=other_identifier_type), "1": ResourceValue(other_identifier, datatype=other_type)}
                    identifier.issued_dcterms = {"0": ResourceValue(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), datatype=XSD.date)}
                    identifier.schemeAgency_adms = {"0": ResourceValue(org_name)}

                    self.schema.identifier_adms[source_length] = identifier

    def set_related_application(self, data_dict):
        related_application = data_dict.get('related_application')
        if related_application:
            self.schema.applicationUsingDataset_dcatapop = {}
            for related_application_uri in related_application.split(","):
                if related_application_uri:
                    # if uri_util.is_uri_valid(related_application_uri):
                    related_application_length = str(len(self.schema.applicationUsingDataset_dcatapop))
                    self.schema.applicationUsingDataset_dcatapop[related_application_length] = SchemaGeneric(
                        related_application_uri)
                # else:
                #     raise Exception("Url [{0}] is not valid".format(related_application_uri))

    def set_related_resource(self, data_dict):
        related_resource = data_dict.get('related_resource')
        if related_resource:
            self.schema.relation_dcterms = {}
            for related_resource_uri in related_resource.split(" "):
                if related_resource_uri:
                    # if uri_util.is_uri_valid(related_resource_uri):
                    related_resource_length = str(len(self.schema.relation_dcterms))
                    self.schema.relation_dcterms[related_resource_length] = SchemaGeneric(related_resource_uri)
                # else:
                #    raise Exception("Url [{0}] is not valid".format(related_resource_uri))

    def set_is_part_of(self, data_dict):
        is_part_of = data_dict.get('is_part_of')
        if is_part_of:
            self.schema.isPartOf_dcterms = {}
            for is_part_of_uri in is_part_of.split(" "):
                if is_part_of_uri:
                    # if uri_util.is_uri_valid(is_part_of_uri):
                    is_part_of_length = str(len(self.schema.isPartOf_dcterms))
                    self.schema.isPartOf_dcterms[is_part_of_length] = SchemaGeneric(is_part_of_uri)
                # else:
                #    raise Exception("Url [{0}] is not valid".format(is_part_of_uri))

    def set_has_version(self, data_dict):
        has_version = data_dict.get('has_version')
        if has_version:
            self.schema.hasVersion_dcterms = {}
            for has_version_uri in has_version.split(" "):
                if has_version_uri:
                    # if uri_util.is_uri_valid(has_version_uri):
                    has_version_length = str(len(self.schema.hasVersion_dcterms))
                    self.schema.hasVersion_dcterms[has_version_length] = SchemaGeneric(has_version_uri)
                # else:
                #     raise Exception("Url [{0}] is not valid".format(has_version_uri))

    def set_is_version_of(self, data_dict):
        is_version_of = data_dict.get('is_version_of')
        if is_version_of:
            list_is_version_of = is_version_of.split(" ")
            self.schema.isVersionOf_dcterms = {}
            for is_version_of_uri in list_is_version_of:
                if is_version_of_uri:
                    # if uri_util.is_uri_valid(is_version_of_uri):
                    is_version_of_length = str(len(self.schema.isVersionOf_dcterms))
                    self.schema.isVersionOf_dcterms[is_version_of_length] = SchemaGeneric(is_version_of_uri)
                # else:
                #    raise Exception("Url [{0}] is not valid".format(is_version_of_uri))

    def set_frequency(self, data_dict):
        frequency = data_dict.get('frequency')
        if frequency:
            self.schema.accrualPeriodicity_dcterms['0'] = FrequencySchemaDcatApOp(frequency)

    def set_doi(self, doi):
        """
        Set a DOI for this dataset.
        :param str doi: The DOI to set.
        """
        if doi:
            lemon_contexts = controlled_vocabulary_util.retrieve_all_notation_skos()

            org = ckan_helper.get_organization({"name": "publ"})
            lemon_context_type = lemon_contexts.get(controlled_vocabulary_util.DOI_URI, {}).get('exactMatch', '')
            identifier = IdentifierSchemaDcatApOp(uri_util.create_uri_for_schema(IdentifierSchemaDcatApOp))
            identifier.notation_skos = {"0": ResourceValue(doi, datatype=controlled_vocabulary_util.DOI_URI), "1": ResourceValue(doi, datatype='http://purl.org/spar/datacite/doi')}
            identifier.issued_dcterms = {"0": ResourceValue(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), datatype=XSD.date)}
            identifier.schemeAgency_adms = {"0": ResourceValue(org[1])}
            identifier.creator_dcterms = {"0": AgentSchemaDcatApOp(uri_util.create_publisher_uri(org[0]))}

            identifier_adms_length = len(self.schema.identifier_adms)
            self.schema.identifier_adms[str(identifier_adms_length)] = identifier

    def set_identifier(self, data_dict):
        identifier = data_dict.get('identifier')
        if identifier:
            identifiers = identifier if isinstance(identifier, list) else identifier.split(" ")
            self.schema.identifier_dcterms = {}
            for identifier in identifiers:
                length = str(len(self.schema.identifier_dcterms))
                self.schema.identifier_dcterms[length] = ResourceValue(identifier)

    def set_keyword_string(self, convertor, data_dict):
        # validate.keyword_string_convert('keyword_string', data_dict, errors, context)
        keyword_string = data_dict.get('keyword_string')
        if keyword_string:
            self.schema.keyword_dcat = convertor.convert_keywords(keyword_string)

    def set_controlled_keyword(self, convertor, data_dict):
        controlled_keywords = data_dict.get('controlled_keyword')
        if controlled_keywords:
            dict = convertor.build_dict_for_inputs(controlled_keywords, self.schema.subject_dcterms, SchemaGeneric)
            self.schema.subject_dcterms = dict

    def set_language(self, convertor, data_dict):
        language = data_dict.get('language')
        if language:
            self.schema.language_dcterms = convertor.convert_language(language)

    def set_modified_date(self, data_dict):
        modified_date = data_dict.get('modified_date')
        if modified_date:
            self.schema.modified_dcterms['0'] = ResourceValue(modified_date, datatype=XSD.date)

    def set_name(self, data_dict):
        name = data_dict.get('name')
        if name:
            self.schema.ckanName_dcatapop['0'] = ResourceValue(name)

    def set_release_date(self, data_dict):
        release_date = data_dict.get('release_date')
        if release_date:
            self.schema.issued_dcterms['0'] = ResourceValue(release_date, datatype=XSD.date)

    def set_temporal_coverage(self, convertor, data_dict):
        temporal_coverage_from = data_dict.get('temporal_coverage_from')
        temporal_coverage_to = data_dict.get('temporal_coverage_to')
        self.schema.temporal_dcterms = convertor.convert_temporal_coverage(temporal_coverage_from,
                                                                               temporal_coverage_to)

    def set_temporal_granularity(self, data_dict):
        temporal_granularities = data_dict.get('temporal_granularity')
        if temporal_granularities:
            if not isinstance(temporal_granularities, list):
                temporal_granularities = [temporal_granularities]
            self.schema.temporalGranularity_dcatapop = {}
            for temporal_granularity in temporal_granularities:
                if temporal_granularity:
                    length = str(len(self.schema.temporalGranularity_dcatapop))
                    self.schema.temporalGranularity_dcatapop[length] = SchemaGeneric(temporal_granularity)

    def set_landing_page(self, data_dict):
        landing_pages = data_dict.get('landing_page')
        if landing_pages:
            self.schema.landingPage_dcat ={}
            for landing_page in landing_pages.split(" "):
                if landing_page:
                    # if uri_util.is_uri_valid(landing_page):
                    landing_page_length = str(len(self.schema.landingPage_dcat))
                    document = DocumentSchemaDcatApOp(uri_util.create_uri_for_schema(DocumentSchemaDcatApOp))
                    document.url_schema[str(len(document.url_schema))] = ResourceValue(landing_page)
                    # TODO add correct default values for the three properties
                    document.topic_foaf['0'] = SchemaGeneric(self.dataset_uri)
                    document.title_dcterms['0'] = ResourceValue("title_" + landing_page, lang='en')
                    document.type_dcterms['0'] = SchemaGeneric("default_type_dcterms")

                    self.schema.landingPage_dcat[landing_page_length] = document
                    # else:
                    #    raise Exception("Url [{0}] is not valid".format(landing_page))

    def set_type_dataset(self, convertor, data_dict):
        dataset_type = data_dict.get('type_of_dataset')
        if dataset_type:
            self.schema.type_dcterms = convertor.convert_dataset_type(dataset_type)

    def set_version(self, data_dict):
        version = data_dict.get('version')
        if version:
            self.schema.versionInfo_owl['0'] = ResourceValue(version)

    def set_version_notes(self, convertor, data_dict):
        version_notes = convertor.convert_translations_of_parameters(data_dict, 'version_notes')
        if version_notes:
            self.schema.versionNotes_adms = version_notes

    def set_resources(self, convertor, data_dict, context):
        distrib = data_dict.get('resources_distribution')
        documentation = data_dict.get('resources_documentation')
        visualization = data_dict.get('resources_visualization')
        if distrib:
            self.schema.distribution_dcat = convertor.convert_resources_distribution(distrib, context.get('old_dataset', None))
        if documentation:
            self.schema.page_foaf = convertor.convert_resources_page(documentation, context.get('old_dataset', None), dataset_uri=self.dataset_uri)
        if visualization:
            self.merge_dict(self.schema.distribution_dcat, convertor.convert_resources_distribution(visualization, context.get('old_dataset', None)))

    def set_source(self, data_dict):
        sources = data_dict.get('source')
        if sources:
            self.schema.source_dcterms = {}
            for dataset_uri in sources.split(" "):
                if dataset_uri:
                    # if uri_util.is_uri_valid(dataset_uri):
                    source_length = str(len(self.schema.source_dcterms))
                    self.schema.source_dcterms[source_length] = SchemaGeneric(dataset_uri)
                # else:
                #    raise Exception("Url [{0}] is not valid".format(dataset_uri))

    def set_provenances(self, data_dict):
        provenances = data_dict.get('provenance')
        if provenances:
            self.schema.provenance_dcterms = {}
            for provenance_uri in provenances.split(" "):
                if provenance_uri:
                    # if uri_util.is_uri_valid(provenance_uri):
                    provenance_length = str(len(self.schema.provenance_dcterms))
                    self.schema.provenance_dcterms[provenance_length] = ProvenanceStatementSchemaDcatApOp(
                        provenance_uri)
                # else:
                #     raise Exception("Url [{0}] is not valid".format(provenance_uri))

    def set_conforms_to(self, data_dict):
        conforms_to = data_dict.get('conforms_to')
        if conforms_to:
            self.schema.conformsTo_dcterms = {}
            for conforms_to_uri in conforms_to.split(" "):
                if conforms_to_uri:
                    # if uri_util.is_uri_valid(conforms_to_uri):
                    conforms_to_length = str(len(self.schema.conformsTo_dcterms))
                    self.schema.conformsTo_dcterms[conforms_to_length] = StandardSchemaDcatApOp(conforms_to_uri)
                # else:
                #    raise Exception("Url [{0}] is not valid".format(conforms_to_uri))

    def set_samples(self, data_dict):
        sample = data_dict.get('sample')
        if sample:
            self.schema.sample_adms ={}
            for sample_uri in sample.split(" "):
                if sample_uri:
                    # if uri_util.is_uri_valid(sample_uri):
                    sample_length = str(len(self.schema.sample_adms))
                    self.schema.sample_adms[sample_length] = SchemaGeneric(sample_uri)
                # else:
                #    raise Exception("Url [{0}] is not valid".format(sample_uri))

    def set_extra_metadata(self, data_dict):
        try:
            for extra_metadata in data_dict.get('extras', []):
                data_extension_uri = uri_util.new_dataextension_uri()
                key = extra_metadata.get('key', '')
                value = extra_metadata.get('value', '')
                is_int = False
                try:
                    value = int(value)
                    is_int = True
                except BaseException as e:
                    is_int = False

                if is_int:
                    extension = DataExtensionSchemaDcatApOp(data_extension_uri)
                    extension.title_dcterms['0'] = ResourceValue(key)
                    extension.dataExtensionValue_dcatapop['0'] = ResourceValue(value, datatype=XSD.decimal)
                    # extension.title_dcterms = titles
                    self.schema.extensionValue_dcatapop[str(len(self.schema.extensionValue_dcatapop))] = extension
                else:
                    extensionLiteral = DataExtensionSchemaDcatApOp(data_extension_uri)
                    extensionLiteral.title_dcterms['0'] = ResourceValue(key)
                    extensionLiteral.dataExtensionLiteral_dcatapop['0'] = ResourceValue(value)
                    # extensionLiteral.title_dcterms = titles
                    self.schema.extensionLiteral_dcatapop[str(len(self.schema.extensionLiteral_dcatapop))] = extensionLiteral
        except BaseException as e:
            log.error("Creation of the extra metadat failed for {0}".format(self.schema.uri))
            log.error(traceback.print_exc(e))

    def merge_dict(self, distribution_dcat, param):
        for dictionnaries in param.values():
            distribution_dcat[len(distribution_dcat)] = dictionnaries


    def set_is_part_of_Catalog(self,data_dict):
        if data_dict.get('catalog'):
            self.schema.isPartOfCatalog_dcatapop['0'] = SchemaGeneric(data_dict['catalog'])


    def set_accessRights(self, data_dict):
        rights = data_dict.get('accessRights', None)
        if rights:
            rights_obj = RightsStatementSchemaDcatApOp(rights)
            self.schema.accessRights_dcterms['0'] = rights_obj

    def set_creator(self, data_dict):

        creator = data_dict.get('creator', None)

        if not creator:
            publisher_dctermes_object = self.schema.publisher_dcterms.get('0', None)
            if not publisher_dctermes_object:
                self.schema.creator_dcterms['0'] = publisher_dctermes_object
        else:
            self.schema.creator_dcterms['0'] = AgentSchemaDcatApOp(creator)

    def set_new_catalog(self, new_catalog=DEFAULT_CATALOG_URI):
        try:
            catalog_uri = new_catalog
            if not catalog_uri:
                catalog_uri = DEFAULT_CATALOG_URI
            date_issued_catalog_record = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            self.schema_catalog_record.issued_dcterms['0'] = ResourceValue(date_issued_catalog_record, datatype=XSD.datetime)
            self.schema_catalog_record.modified_dcterms['0'] = ResourceValue(date_issued_catalog_record, datatype=XSD.datetime)
            self.schema.isPartOfCatalog_dcatapop['0'] = SchemaGeneric(catalog_uri)
        except BaseException as e:
            log.error("Set default catalog failed. {0}".format(self.dataset_uri))
            log.error(traceback.print_exc(e))

    def find_the_graph_in_ts(self):
        """
            get the correct graph in which the dataset is saved. To be used with the package show to know in which graph is the dataset
            :return str:
        """
        try:
            tsch = TripleStoreCRUDHelpers()
            result = tsch.find_graph_of_dataset(self.dataset_uri)
            if len(result) == 0:
                return ''
            else:
                graph_name = result[0].get("graph",{}).get("value","")
                return graph_name
        except BaseException as e:
            log.error("[Dataset] [find the graph of dataset] [failed] [Dataset:{0}]".format(self.dataset_uri))
            log.error(traceback.print_exc(e))



    def has_doi_identifier(self):
        """
        Check if this dataset has a DOI.
        :return: True if this dataset contains a DOI, else False.
        """
        from ckanext.ecportal.lib.ui_util import _count_doi_from_adms_identifier
        count_doi = _count_doi_from_adms_identifier(self.schema.identifier_adms)
        return count_doi != 0

    def get_publisher_acronym(self):
        '''
        Get the acronym of the publisher
        :return:
        '''
        publisher = self.schema.publisher_dcterms.get('0', SchemaGeneric('')).uri  # type: str
        owner_org = publisher.split('/')[-1].lower()
        return owner_org

    def get_doi(self):
        '''
        Get the DOI identifier of the dataset.
        :return: The found DOI identifier.
        '''
        doi = None
        if self.schema.identifier_adms.values():
            doi_datatypes = [controlled_vocabulary_util.DOI_URI.lower(), "http://purl.org/spar/datacite/doi".lower()]
            for identifier in self.schema.identifier_adms.values():
                if hasattr(identifier, "notation_skos"):
                    notation = next((notation for notation in identifier.notation_skos.values() if notation.datatype.lower() in doi_datatypes),None)  # type: ResourceValue
                    if notation:
                        doi = identifier
                        break

        return doi
