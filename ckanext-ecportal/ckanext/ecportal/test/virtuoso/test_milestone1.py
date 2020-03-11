# -*- coding: utf-8 -*-
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

from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
from ckanext.ecportal.model.common_constants import DCATAPOP_PRIVATE_GRAPH_NAME, DCATAPOP_PUBLIC_GRAPH_NAME
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
from ckanext.ecportal.multilingual.languages_constants import LanguagesConstants
from ckanext.ecportal.virtuoso.basic_queries_constants import RESET_TRIPLE_STORES, SELECT_ALL_DCATAPOP_PUBLIC, \
    SELECT_ALL_DCATAPOP_PRIVATE
from ckanext.ecportal.virtuoso.graph_related_constants import PRIVACY_STATE_PRIVATE, PRIVACY_STATE_PUBLIC
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers as tsch
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_helpers import TripleStoreIngestionHelpers

TRANSLATION_MEMORY_V_4 = "http://data.europa.eu/88u/dataset/dgt-translation-memory-V4"

TRANSLATION_MEMORY_V_3 = "http://data.europa.eu/88u/dataset/dgt-translation-memory-V3"

TRANSLATION_MEMORY_V_1_2 = "http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2"

logging.basicConfig(level=logging.DEBUG)


class TestMilestone1(TestWithVirtuosoConfiguration):
    def setUp(self):
        global tripleStoreIngestionHelpers
        tripleStoreIngestionHelpers = TripleStoreIngestionHelpers()
        global crud_helper
        crud_helper = tsch()
        #crud_helper.execute_update_query(RESET_TRIPLE_STORES)
        logging.info("Setup of data done")



    def test_clean_up_virtuoso(self):
        # crud_helper.execute_update_query(RESET_TRIPLE_STORES)
        logging.info("Cleaning data done")

    def test_ingestion_files(self):
        crud_helper.execute_update_query(RESET_TRIPLE_STORES)
        base_path = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/datasets/"
        with open(base_path + "dataset1.rdf") as f:
            file_content = f.read()
            tripleStoreIngestionHelpers.ingest_graph_from_string(DCATAPOP_PUBLIC_GRAPH_NAME, file_content)
        with open(base_path + "dataset2.rdf") as f:
            file_content = f.read()
            tripleStoreIngestionHelpers.ingest_graph_from_string(DCATAPOP_PUBLIC_GRAPH_NAME, file_content)
        with open(base_path + "dataset_private.rdf") as f:
            file_content = f.read()
            tripleStoreIngestionHelpers.ingest_graph_from_string(DCATAPOP_PRIVATE_GRAPH_NAME, file_content)

        # TODO use more explicit variables
        lstm_private = crud_helper.execute_select_query_auth(SELECT_ALL_DCATAPOP_PRIVATE)
        assert lstm_private is not None
        lstm_public = crud_helper.execute_select_query_auth(SELECT_ALL_DCATAPOP_PUBLIC)
        assert lstm_public is not None

    def test_get_description_from_ts(self):
        self.test_ingestion_files()
        dataset_1 = DatasetDcatApOp(TRANSLATION_MEMORY_V_1_2)
        dataset_2 = DatasetDcatApOp(TRANSLATION_MEMORY_V_3)
        private_dataset = DatasetDcatApOp(TRANSLATION_MEMORY_V_4,
                                          privacy_state=PRIVACY_STATE_PRIVATE,
                                          graph_name=DCATAPOP_PRIVATE_GRAPH_NAME)

        description_dataset_1 = dataset_1.get_description_from_ts()
        assert description_dataset_1 is True
        description_dataset_2 = dataset_2.get_description_from_ts()
        assert description_dataset_2 is True
        private_dataset_description = private_dataset.get_description_from_ts()  # type: DatasetDcatApOp
        assert private_dataset_description is not None
        assert private_dataset_description.schema.graph_name is DCATAPOP_PRIVATE_GRAPH_NAME

        ckan_name_dataset_1 = dataset_1.schema.ckanName_dcatapop['0'].value_or_uri
        assert ckan_name_dataset_1 is not None
        ckan_name_dataset_2 = dataset_2.schema.ckanName_dcatapop['0'].value_or_uri
        assert ckan_name_dataset_2 is not None
        ckan_name_private_dataset = private_dataset.schema.ckanName_dcatapop['0'].value_or_uri
        assert ckan_name_private_dataset is not None
        keywords_dataset_1 = dataset_1.schema.keyword_dcat

        # should log instead of print.
        print "Dataset: " + TRANSLATION_MEMORY_V_1_2
        print "CkanName is : {0} ".format(ckan_name_dataset_1)
        print "keywords are :".format()
        for k, rv in keywords_dataset_1.iteritems():
            print "language '{0}' has the value '{1}'".format(rv.lang, rv.value_or_uri)

    def test_edit_save_to_ts(self):
        self.test_get_description_from_ts()
        dataset = DatasetDcatApOp(TRANSLATION_MEMORY_V_1_2)
        if dataset.get_description_from_ts():
            dataset.privacy_state = PRIVACY_STATE_PUBLIC
            dataset.schema.ckanName_dcatapop['0'].value_or_uri = "NEW CKAN NAME"
            dataset.schema.keyword_dcat[LanguagesConstants.LANGUAGE_CODE_FR] = \
                ResourceValue(u'la réussite', lang=LanguagesConstants.LANGUAGE_CODE_FR)
            dataset.schema.keyword_dcat[LanguagesConstants.LANGUAGE_CODE_EL] = \
                ResourceValue(u'επιτυχία', lang=LanguagesConstants.LANGUAGE_CODE_EL)
            dataset.schema.contactPoint_dcat['0'].hasTelephone_vcard['0'].hasValue_vcard['0'].uri = "TEL:213232323"
            if dataset.save_to_ts():
                print " Save done"
            ds1after = DatasetDcatApOp(TRANSLATION_MEMORY_V_1_2)
            ds1after.get_description_from_ts()
            pass

    def test_save_as_public(self):
        ds_private = DatasetDcatApOp(TRANSLATION_MEMORY_V_4,
                                     privacy_state=PRIVACY_STATE_PRIVATE,
                                     graph_name=DCATAPOP_PRIVATE_GRAPH_NAME)
        ds_private.privacy_state = PRIVACY_STATE_PUBLIC
        ds_private.get_description_from_ts()
        ds_private.save_to_ts()

    def test_remove_ds(self):
        ds = DatasetDcatApOp('http://data.europa.eu/88u/dataset/NikosTagTest_1342')
        ds.get_description_from_ts()
        result = ds.delete_from_ts()
        self.assertTrue(result)
