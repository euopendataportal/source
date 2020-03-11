import logging
import pickle

import ckan.plugins as p
import ckanext.ecportal.lib.cache.redis_cache as redis_cache
from ckanext.ecportal.configuration.configuration_constants import MDR_HOST_NAME, MDR_HOST_NAME_AUTHENTICATED
from ckanext.ecportal.model.schema_wrapper_interface import ISchemaWrapper
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
from ckanext.ecportal.model.schemas.controlled_vocabulary_schema import ConceptSchemaSkos, ConceptSchemeSchemaSkos, CorporateBody
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
from pylons import config
from rdflib import Graph

DEFAULT_VOCABULARY_CLASS = NAMESPACE_DCATAPOP.skos + 'Concept'

log = logging.getLogger(__file__)

CORPORATE_BODY = 'http://publications.europa.eu/resource/authority/corporate-body'

logging.basicConfig(level=logging.DEBUG)


class ConceptSchemaSkosWrapper(object):
    p.implements(ISchemaWrapper)

    SCHEMA_TYPE=ConceptSchemaSkos

    def __init__(self, uri, graph_name,
                 data_dict=None):
        self.uri = uri
        self.graph_name = graph_name
        self.schema = self.SCHEMA_TYPE(uri, graph_name)
        self.ttl_as_in_ts = ""
        self.cache_id = "ConceptSchemaSkos_description_{0}".format(uri)
        if data_dict:
            self.__dict__.update(data_dict)
        pass
        self.__final_description_dict = dict()  # type: dict[str,dict[str,ResourceValue|SchemaGeneric]]

    def get_description_from_ts(self):
        """
        get the Concept from triples store

        :rtype Boolean:
        """
        try:
            # initialization of the schemas
            self.schema = self.SCHEMA_TYPE(self.uri, self.graph_name)
            desc_ds = self.schema.get_description_from_ts()
            if desc_ds is None:
                return None
            if len(desc_ds) == 0:
                return False
            self.__final_description_dict = desc_ds

            # save the content of the Vocabulary as a graph. To be used when updating the Vocabulary in the triples store
            self.ttl_as_in_ts = self.build_the_graph().serialize(format="nt")
            log.info("[Vocabulary]. Get description from Triples stores successful [{0}]".format(self.uri))
            return True
        except BaseException as e:
            log.error("[Vocabulary]. Get description from Triples stores failed [uri: {0}]. [Exception: {1}]".format(
                self.uri, e.message))
            return None

    def get_vocabulary_description(self):
        try:

            active_cache = config.get('ckan.cache.active', 'false')
            vocabulary = None  # type: ConceptSchemaSkosWrapper

            if active_cache == 'true':
                # get the ds from cache
                vocabulary_string = redis_cache.get_from_cache(self.cache_id)
                if vocabulary_string:
                    catalog = pickle.loads(vocabulary_string)
                    log.info('Load ConceptSchemaSkosWrapper from cache: {0}'.format(self.cache_id))

            if active_cache != 'true' or vocabulary is None:
                self.get_description_from_ts()
                redis_cache.set_value_in_cache(self.cache_id, pickle.dumps(self), 864000)
            return vocabulary
        except BaseException as e:
            log.error("[Vocabulary]. Get ConceptSchemaSkosWrapper description failed for {0}".format(self.uri))

    def save_to_ts(self):
        log.warn('ConceptSchemaSkosWrapper can not be stored back to TS')
        raise NotImplementedError('ConceptSchemaSkosWrapper can not be stored fromTS')

    def delete_from_ts(self):
        log.warn('ConceptSchemaSkosWrapper can not be deleted back to TS')
        raise NotImplementedError('ConceptSchemaSkosWrapper can not be deleted from TS')

    def build_the_graph(self):
        """
        To build the RDFlib graph of the dataset based on the schema ( pricipal)
        :rtype: Graph|None
        """
        try:
            dataset_graph = Graph()
            graph_catalog_schema = None
            if self.schema:
                graph_catalog_schema = self.schema.convert_to_graph_ml()
                # dataset_graph = graph_dataset_sch

            if graph_catalog_schema:
                dataset_graph = graph_catalog_schema
                return dataset_graph

        except BaseException as e:
            log.error("[ConceptSchemaSkosWrapper]. build the graph failed [{0}]".format(self.uri))
            return None


    @staticmethod
    def get_map_vocabulary(graph_name, vocabulary_class_uri=DEFAULT_VOCABULARY_CLASS):
        '''
        get the list of catalogs in the the triple stores
        :return:
        '''
        ts_host = config.get(MDR_HOST_NAME)
        ts_host_auth = config.get(MDR_HOST_NAME_AUTHENTICATED)
        try:
            tsch = TripleStoreCRUDHelpers(ts_host, ts_host_auth)
            list_uris_vocabulary = tsch.get_list_resources_by_class(graph_name, vocabulary_class_uri)
            map_vocabulary = {}
            for uri_vocabulary in list_uris_vocabulary:
                vocabulary = ConceptSchemaSkosWrapper(uri_vocabulary,graph_name)
                vocabulary.get_description_from_ts()
                map_vocabulary[uri_vocabulary] = vocabulary
            return map_vocabulary

        except BaseException as e:
            log.error("Can not get the list of vocabulary")



class ConceptSchemeSchemaSkosWrapper(object):
    p.implements(ISchemaWrapper)

    def __init__(self, uri, graph_name,
                 data_dict=None):
        self.uri = uri
        self.graph_name = graph_name
        self.schema = ConceptSchemeSchemaSkos(uri, graph_name)
        self.ttl_as_in_ts = ""
        self.cache_id = "ConceptSchemeSchemaSkos_description_{0}".format(uri)
        if data_dict:
            self.__dict__.update(data_dict)
        pass
        self.__final_description_dict = dict()  # type: dict[str,dict[str,ResourceValue|SchemaGeneric]]

    def get_description_from_ts(self):
        """
        get the Concept from triples store

        :rtype Boolean:
        """
        try:
            # initialization of the schemas
            self.schema = ConceptSchemeSchemaSkos(self.uri, self.graph_name)
            desc_ds = self.schema.get_description_from_ts()
            if desc_ds is None:
                return None
            if len(desc_ds) == 0:
                return False
            self.__final_description_dict = desc_ds

            # save the content of the Vocabulary as a graph. To be used when updating the Vocabulary in the triples store
            self.ttl_as_in_ts = self.build_the_graph().serialize(format="nt")
            log.info("[Vocabulary]. Get description from Triples stores successful [{0}]".format(self.uri))
            return True
        except BaseException as e:
            log.error("[Vocabulary]. Get description from Triples stores failed [uri: {0}]. [Exception: {1}]".format(
                self.uri, e.message))
            return None

    def get_vocabulary_description(self):
        try:

            active_cache = config.get('ckan.cache.active', 'false')
            vocabulary = None  # type: ConceptSchemeSchemaSkosWrapper

            if active_cache == 'true':
                # get the ds from cache
                vocabulary_string = redis_cache.get_from_cache(self.cache_id)
                if vocabulary_string:
                    catalog = pickle.loads(vocabulary_string)
                    log.info('Load ConceptSchemeSchemaSkosWrapper from cache: {0}'.format(self.cache_id))

            if active_cache != 'true' or vocabulary is None:
                self.get_description_from_ts()
                redis_cache.set_value_in_cache(self.cache_id, pickle.dumps(self), 864000)
            return vocabulary
        except BaseException as e:
            log.error("[Vocabulary]. Get ConceptSchemeSchemaSkosWrapper description failed for {0}".format(self.uri))

    def save_to_ts(self):
        log.warn('ConceptSchemeSchemaSkosWrapper can not be stored back to TS')
        raise NotImplementedError('ConceptSchemeSchemaSkosWrapper can not be stored fromTS')

    def delete_from_ts(self):
        log.warn('ConceptSchemeSchemaSkosWrapper can not be deleted back to TS')
        raise NotImplementedError('ConceptSchemeSchemaSkosWrapper can not be deleted from TS')

    def build_the_graph(self):
        """
        To build the RDFlib graph of the dataset based on the schema ( pricipal)
        :rtype: Graph|None
        """
        try:
            dataset_graph = Graph()
            graph_catalog_schema = None
            if self.schema:
                graph_catalog_schema = self.schema.convert_to_graph_ml()
                # dataset_graph = graph_dataset_sch

            if graph_catalog_schema:
                dataset_graph = graph_catalog_schema
                return dataset_graph

        except BaseException as e:
            log.error("[ConceptSchemeSchemaSkosWrapper]. build the graph failed [{0}]".format(self.uri))
            return None



    @staticmethod
    def get_map_vocabulary(graph_name, vocabulary_class_uri=DEFAULT_VOCABULARY_CLASS):
        '''
        get the list of catalogs in the the triple stores
        :return:
        '''
        ts_host = config.get(MDR_HOST_NAME)
        ts_host_auth = config.get(MDR_HOST_NAME_AUTHENTICATED)
        try:
            tsch = TripleStoreCRUDHelpers(ts_host, ts_host_auth)
            list_uris_vocabulary = tsch.get_list_resources_by_class(graph_name, vocabulary_class_uri)
            map_vocabulary = {}
            for uri_vocabulary in list_uris_vocabulary:
                vocabulary = ConceptSchemeSchemaSkosWrapper(uri_vocabulary,graph_name)
                vocabulary.get_description_from_ts()
                map_vocabulary[uri_vocabulary] = vocabulary
            return map_vocabulary

        except BaseException as e:
            log.error("Can not get the list of vocabulary")


class CorporateBodyWrapper(ConceptSchemaSkosWrapper):
    p.implements(ISchemaWrapper)

    SCHEMA_TYPE=CorporateBody

    def __init__(self, uri, graph_name,
                 data_dict=None):
        super(CorporateBodyWrapper, self).__init__(uri, graph_name,data_dict)
        self.schema = CorporateBody(uri, graph_name)
        self.ttl_as_in_ts = ""
        self.cache_id = "CorporateBody_description_{0}".format(uri)
        if data_dict:
            self.__dict__.update(data_dict)
        pass
        self.__final_description_dict = dict()  # type: dict[str,dict[str,ResourceValue|SchemaGeneric]]

