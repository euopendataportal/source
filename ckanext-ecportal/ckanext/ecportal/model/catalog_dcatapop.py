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
import logging
import pickle

from pylons import config
from rdflib import Graph
from rdflib import XSD

import ckan.plugins as p
import ckanext.ecportal.helpers as ckan_helper
import ckanext.ecportal.lib.cache.redis_cache as redis_cache
import ckanext.ecportal.lib.uri_util as uri_util
from ckanext.ecportal.lib import controlled_vocabulary_util
from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.model.schema_wrapper_interface import ISchemaWrapper
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP, DatasetSchemaDcatApOp, CatalogSchemaDcatApOp, DocumentSchemaDcatApOp, RightsStatementSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_identifier_schema import IdentifierSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
import traceback

CATALOG_CLASS_URI = NAMESPACE_DCATAPOP.dcat + "Catalog"

log = logging.getLogger(__file__)


logging.basicConfig(level=logging.DEBUG)


class CatalogDcatApOp(object):
    p.implements(ISchemaWrapper)

    def __init__(self, catalog_uri, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME,
                 data_dict=None):
        self.catalog_uri = catalog_uri
        self.graph_name = graph_name
        self.schema = CatalogSchemaDcatApOp(catalog_uri, graph_name)
        self.ttl_as_in_ts = ""
        self.cache_id = "catalog_description_{0}".format(catalog_uri)
        if data_dict:
            self.__dict__.update(data_dict)
        pass
        self.__final_description_dict = dict()  # type: dict[str,dict[str,ResourceValue|SchemaGeneric]]

    def get_description_from_ts(self):
        """
        get the catalog from triples store

        :rtype Boolean:
        """
        try:
            # initialization of the schemas
            self.schema = CatalogSchemaDcatApOp(self.catalog_uri, self.graph_name)
            desc_ds = self.schema.get_description_from_ts()
            if desc_ds is None:
                return None
            if len(desc_ds) == 0:
                return False
            self.__final_description_dict = desc_ds

            # save the content of the Catalog as a graph. To be used when updating the Catalog in the triples store
            self.ttl_as_in_ts = self.build_the_graph().serialize(format="nt")
            log.info("[Catalog]. Get description from Triples stores successful [{0}]".format(self.catalog_uri))
            return True
        except BaseException as e:
            log.error("[Catalog]. Get description from Triples stores failed [uri: {0}]".format(
                self.catalog_uri))
            log.error(traceback.print_exc(e))
            return None

    def get_catalog_description(self):
        try:
            active_cache = config.get('ckan.cache.active', 'false')
            catalog = None  # type: CatalogDcatApOp

            if active_cache == 'true':
                # get the ds from cache
                catalog_string = redis_cache.get_from_cache(self.cache_id, pool=redis_cache.MISC_POOL)
                if catalog_string:
                    catalog = pickle.loads(catalog_string)
                    log.info('Load catalog from cache: {0}'.format(self.cache_id))

            if active_cache != 'true' or catalog is None:
                self.get_description_from_ts()
                redis_cache.flush_all_from_db(redis_cache.MISC_POOL)
                redis_cache.set_value_in_cache(self.cache_id, pickle.dumps(self), 864000, pool=redis_cache.MISC_POOL)
            return catalog
        except BaseException as e:
            log.error("[Catalog]. Get Catalog description failed for {0}".format(self.catalog_uri))
            log.error(traceback.print_exc(e))
            return None

    def save_to_ts(self):
        """
            To insert or update the description of the Catalog in the TS.
            all the existing description in TS will be removed.
        :rtype: Boolean
        """
        try:
            tsch = TripleStoreCRUDHelpers()
            source_graph = self.graph_name
            target_graph_to_save = DCATAPOP_PUBLIC_GRAPH_NAME

            ttl_ds_from_ts = self.ttl_as_in_ts
            ttl_ds_last_version = self.build_the_graph().serialize(format="nt")
            r = tsch.execute_update_without_condition(source_graph, target_graph_to_save, ttl_ds_from_ts,
                                                      ttl_ds_last_version)
            log.info("[Catalog]. Save catalog successful [{0}]".format(self.catalog_uri))
            self.ttl_as_in_ts = ttl_ds_last_version
            active_cache = config.get('ckan.cache.active', 'false')
            if active_cache == 'true':
                redis_cache.set_value_in_cache(self.cache_id, pickle.dumps(self), 864000, pool=redis_cache.MISC_POOL)

            return r
        except BaseException as e:
            log.error("[Catalog]. Save catalog failed [{0}]".format(self.catalog_uri ))
            log.error(traceback.print_exc(e))
            return False

    def delete_from_ts(self):
        """
        To delete the Catalog from the TS
        :rtype: Boolean
        """
        try:
            tsch = TripleStoreCRUDHelpers()
            source_graph = self.graph_name
            ttl_ds_from_ts = self.ttl_as_in_ts
            status = tsch.execute_delete_ttl(source_graph, ttl_ds_from_ts)

            if status:
                # initialization of the schemas
                self.schema = CatalogSchemaDcatApOp(self.catalog_uri, self.graph_name)
                self.ttl_as_in_ts = ""
                active_cache = config.get('ckan.cache.active', 'false')
                if active_cache == 'true':
                    redis_cache.delete_value_from_cache(self.cache_id)
                log.info("[Catalog]. [delete Catalog from ts] successful [uri: {0}]".format(self.catalog_uri))

                return True
            else:
                log.info("[Catalog]. [delete Catalog from ts] failed [uri: {0}]. [Message from TS: {1}]".format(
                    self.catalog_uri, tsch.get_virtuoso_query_return()))
                return False

        except BaseException as e:
            log.error("[Catalog]. [delete Catalog from ts] failed. [uri: {0}]".format(self.catalog_uri))
            log.error(traceback.print_exc(e))
            return None

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
            log.error("[Catalog]. build the graph failed [{0}]".format(self.catalog_uri))
            return None

    def add_dataset(self, dataset):
        '''

        :param DatasetSchemaDcatApOp\str dataset:
        :return:
        '''
        if isinstance(dataset, str):
            dataset = DatasetSchemaDcatApOp(dataset)

        if not dataset in self.schema.dataset_dcat.values():
            index = len(self.schema.dataset_dcat.keys())
            self.schema.dataset_dcat['{0}'.format(index)] = dataset
            self.save_to_ts()
            return True

        return False

    def remove_dataset(self, dataset):
        '''

        :param DatasetSchemaDcatApOp|str dataset:
        :return:
        '''
        if isinstance(dataset, str):
            dataset = DatasetSchemaDcatApOp(dataset)
        new_ds_dict = {}
        index = 0
        for value in self.schema.dataset_dcat.values():
            if dataset != value:
                new_ds_dict['{0}'.format(index)] = value
                index += 1

        self.schema.dataset_dcat = new_ds_dict
        self.save_to_ts()

        return True

    @staticmethod
    def get_list_catalogs():
        '''
        get the list of catalogs in the the triple stores
        :return:
        '''
        try:
            tsch = TripleStoreCRUDHelpers()
            list_uris_catalogs = tsch.get_list_resources_by_class(DCATAPOP_PUBLIC_GRAPH_NAME, CATALOG_CLASS_URI)
            list_catalogs = {}
            for uri_catalog in list_uris_catalogs:
                catalog = CatalogDcatApOp(uri_catalog)
                catalog.get_description_from_ts()
                list_catalogs[uri_catalog] = catalog
            return list_catalogs

        except BaseException as e:
            log.error("Can not get the list of catalogs")


    @staticmethod
    def get_ui_list_catalogs(lang):
        list_catalogs = CatalogDcatApOp.get_list_catalogs()
        catalogs = []
        for catalog in list_catalogs.values():  # type: CatalogDcatApOp
            name = catalog.catalog_uri.split('/')[-1]
            from ckanext.ecportal.lib.ui_util import _get_translated_term_from_dcat_object
            display_name = _get_translated_term_from_dcat_object(catalog.schema, 'title_dcterms', lang)
            description = _get_translated_term_from_dcat_object(catalog.schema, 'description_dcterms', lang)
            catalog_ui = {'name': name, 'display_name': display_name, 'description': description, 'uri': catalog.catalog_uri}
            catalogs.append(catalog_ui)
        return catalogs

    def set_home_page(self, data_dict):

        try:
            home_pages = data_dict.get('home_page')
            if home_pages:
                for home_page in home_pages.split(" "):
                    if home_page:
                        home_page_length = str(len(self.schema.homepage_foaf))
                        document = DocumentSchemaDcatApOp(uri_util.create_uri_for_schema(DocumentSchemaDcatApOp))
                        document.url_schema[str(len(document.url_schema))] = ResourceValue(home_page)
                        # TODO add correct default values for the three properties
                        document.topic_foaf['0'] = SchemaGeneric("default_topic_foaf")
                        document.title_dcterms['0'] = ResourceValue("title_" + home_page)
                        document.type_dcterms['0'] = SchemaGeneric("default_type_dcterms")

                        self.schema.homepage_foaf[home_page_length] = document
        except BaseException as e:
            log.error("Failed to set home page to catalog {0}".format(self.schema.uri))

    def set_rights(self, data_dict):
        try:
            rights = data_dict.get('rights')
            if rights:
                rs = RightsStatementSchemaDcatApOp(uri_util.new_rightstatement_uri())
                rs.label_rdfs['0'] = ResourceValue(rights)
                self.schema.rights_dcterms['0'] = rs
        except BaseException as e:
            log.error("Failed to set rights to catalog {0}".format(self.schema.uri))

    def set_spatial(self, data_dict):
        try:
            from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LocationSchemaDcatApOp
            spatials = data_dict.get('catalog_geographical_coverage')
            if spatials:
                for location in spatials:
                    if location:
                        spatial_length = str(len(self.schema.spatial_dcterms))
                        self.schema.spatial_dcterms[spatial_length] = LocationSchemaDcatApOp(location)
        except BaseException as e:
            log.error("Failed to set spatial to catalog {0}".format(self.schema.uri))

    def build_DOI_dict(self):
        '''
        Generate the dict that will be used by the DOI package
        :return dict:
        '''

        try:
            catalog_dict = self.schema.build_DOI_dict_from_catalog_schema()
            # convert to DOI dict
            log.info("build the DOI dict successful for catalog {0} ".format(self.catalog_uri))
            return catalog_dict
        except BaseException as e:
            log.error("build the DOI dict failed for catalog {0} ".format(self.catalog_uri))

    def set_doi(self, doi):
        """
        Set a DOI for this catalogue.
        :param str doi: The DOI to set.
        """
        if doi:
            update_doi = True
            catalog = CatalogDcatApOp(self.schema.uri)
            catalog.get_description_from_ts()
            for dois in catalog.schema.identifier_adms.values():
                if hasattr(dois, 'notation_skos'):
                    if dois.notation_skos.get("0").value_or_uri == controlled_vocabulary_util.DOI_URI:
                        update_doi = False
                        self.schema.identifier_adms['0'] = dois
                        break

            if update_doi:
                org = ckan_helper.get_organization({"name": "publ"})
                identifier = IdentifierSchemaDcatApOp(uri_util.create_uri_for_schema(IdentifierSchemaDcatApOp))
                identifier.notation_skos = {"0": ResourceValue(doi, datatype=controlled_vocabulary_util.DOI_URI)}
                identifier.issued_dcterms = {"0": ResourceValue(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), datatype=XSD.date)}
                identifier.schemeAgency_adms = {"0": ResourceValue(org[1])}

                identifier_adms_length = len(self.schema.identifier_adms)
                self.schema.identifier_adms[str(identifier_adms_length)] = identifier

    def has_doi_identifier(self):
        """
        Check if this catalogue has a DOI.
        :return: True if this catalogue contains a DOI, else False.
        """
        for identifiers in self.schema.identifier_adms.values():
            if hasattr(identifiers, 'notation_skos'):
                if identifiers.notation_skos.get("0").value_or_uri == controlled_vocabulary_util.DOI_URI:
                    return True
        return False
