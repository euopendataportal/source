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

from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
from ckanext.ecportal.test.configuration.configuration_constants import *
import pickle
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_helpers import TripleStoreIngestionHelpers as tsih
from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME, DCATAPOP_INGESTION_DATASET
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers as tsch

from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp


import ckanext.ecportal.lib.controlled_vocabulary_util as controlled_vocabulary_util
import ckanext.ecportal.model.common_constants

vsci = tsih()
vsc = tsch()
import json


class TestDatasetDcatApOp(TestWithVirtuosoConfiguration):

    def setUp(self):
        # sparql_query = """
        #
        #            drop silent graph <dcatapop-public-test>
        #            create silent graph <dcatapop-public-test>
        #
        #            drop silent graph <dcatapop-private-test>
        #            create silent graph <dcatapop-private-test>
        #
        #            """
        # vsc.execute_update_query(sparql_query)
        #
        # base_path = TEST_DATA_PATH + "/datasets/"
        #
        # with open(base_path + "dataset1.rdf") as f:
        #     file_content = f.read()
        #     vsci.ingest_graph_from_string(DCATAPOP_PUBLIC_GRAPH_NAME, file_content)
        # with open(base_path + "dataset2.rdf") as f:
        #     file_content = f.read()
        #     vsci.ingest_graph_from_string(DCATAPOP_PUBLIC_GRAPH_NAME, file_content)
        # with open(base_path + "dataset_private.rdf") as f:
        #     file_content = f.read()
        #     vsci.ingest_graph_from_string(DCATAPOP_PRIVATE_GRAPH_NAME, file_content)
        pass

    def test_save_to_ts_new(self):
        dataset = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory")
        dataset.get_description_from_ts()
        r = dataset.save_to_ts()



        self.assertTrue(r)

        pass


    def test_get_description_from_ts(self):
        ds1 = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        ds2 = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V3")
        ds_private = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V4",
                                     privacy_state="private", graph_name=DCATAPOP_PRIVATE_GRAPH_NAME)

        desc1 = ds1.get_description_from_ts()
        desc2 = ds2.get_description_from_ts()
        desc_private = ds_private.get_description_from_ts()

        ckan_name1 = ds1.schema.ckanName_dcatapop['0'].value_or_uri
        ckan_name2 = ds2.schema.ckanName_dcatapop['0'].value_or_uri
        ckan_name_private = ds_private.schema.ckanName_dcatapop['0'].value_or_uri

        self.assertTrue(
            ckan_name1 == "dgt-translation-memory-V1-2" and ckan_name_private == "dgt-translation-memory-V4",
            "TestDataSet: CkanName is not correct")

        keyword_ds1 = ds1.schema.keyword_dcat['0'].value_or_uri;
        len_keyword_ds2 = ds2.schema.keyword_dcat.__len__()
        self.assertTrue(keyword_ds1 == "translation" and len_keyword_ds2 == 4,
                        "TestDataSet: Structure of keyword error ")

        self.assertTrue(ds1.get_telephone_numbers() == {'0': u'tel:086631722'})

    def test_save_to_ts(self):
        ds1 = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds1.get_description_from_ts():
            ds1.privacy_state = "public"
            ds1.schema.ckanName_dcatapop['0'].value_or_uri = "NEW CKAN NAME"
            ds1.schema.ckanName_dcatapop['1'] = ResourceValue("Second CKAN NAME")
            # ckan_name_new = ds1.schema.ckanName_dcatapop['1'] = ResourceValue("another ckan Name")
            ds1.schema.contactPoint_dcat['0'].hasTelephone_vcard['0'].hasValue_vcard['0'].uri = "TEL:213232323"
            ds1.save_to_ts()

            ds1after = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
            ds1after.get_description_from_ts()

            ckan_name_new = ds1after.schema.ckanName_dcatapop['0'].value_or_uri
            lenc = len(ds1after.schema.ckanName_dcatapop)
            msg = "Expected name {0}, New value {1}. Expected length {2}, Get {3}"
            self.assertTrue(ckan_name_new == "NEW CKAN NAME" and lenc == 2,
                            msg.format("NEW CKAN NAME", ckan_name_new, 2, lenc))
            # check if the generation of uris from memeber name workds in the case of DASH and DOT
            self.assertTrue("organisation-name" in ds1after.ttl_as_in_ts, "generation of uri from member failed")

        ds_new = DatasetDcatApOp("http://newdcatap.com")
        ds_new.schema.ckanName_dcatapop['0'] = ResourceValue("ckan Name new")
        ds_new.save_to_ts()

        ds_new_from_ts = DatasetDcatApOp("http://newdcatap.com")
        ds_new_from_ts.get_description_from_ts()

        self.assertTrue(ds_new_from_ts.schema.ckanName_dcatapop['0'].value_or_uri == ds_new.schema.ckanName_dcatapop['0'].value_or_uri, "New dataset is not saved")

    def test_convert_to_graph(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        ds.get_description_from_ts()
        gs_before = ds.build_the_graph()
        ttl_as_in_ts = gs_before.serialize(format="nt")

        ds.schema.ckanName_dcatapop['0'].value_or_uri = "NEW CKAN NAME"
        ds.schema.ckanName_dcatapop['1'] = ResourceValue("NEW CKAN NAME", 'fr')

        ds.schema.description_dcterms = {}  # ['0'].value_or_uri = "NEW DESCRIPTION"
        gs_after = ds.build_the_graph()
        ttl_convert = gs_after.serialize(format="nt")
        contain = "NEW CKAN NAME" in ttl_convert
        contain_removed_desc = "<http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2> <http://purl.org/dc/terms/description>" in ttl_convert
        self.assertTrue(contain, "Convertion of the graph faild")
        self.assertFalse(contain_removed_desc, "removed element still in the dataset, build graph failed ")

    def test_create_ds(self):
        ds1 = DatasetDcatApOp("t1")
        ds2 = DatasetDcatApOp("t2")

        ds1.schema.description_dcterms['5'] = ResourceValue("rien ds 111")
        ds2.schema.description_dcterms['5'] = ResourceValue("rien ds 222")
        ds1.schema.ckanName_dcatapop['6'] = ResourceValue("ckan name ds1")
        ds1.schema.description_dcterms['4'] = ResourceValue("rien 111")
        ds2.schema.ckanName_dcatapop['6'] = ResourceValue("ckan name ds2")

        self.assertNotEqual(ds1.schema.description_dcterms['5'].value_or_uri,
                            ds2.schema.description_dcterms['5'].value_or_uri, "ddd")
        self.assertNotEqual(len(ds1.schema.description_dcterms), len(ds2.schema.description_dcterms))


    def test_serialize_dataset(self):  # TODO
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        desc = ds.get_description_from_ts()
        if desc:
            phone_source = ds.schema.contactPoint_dcat['0'].hasTelephone_vcard['0'].hasValue_vcard['0'].uri

            redis_ds = pickle.dumps(ds)
            ds2 = pickle.loads(redis_ds)
            phone = ds2.schema.contactPoint_dcat['0'].hasTelephone_vcard['0'].hasValue_vcard['0'].uri

            self.assertEqual(phone_source, phone, "Test serialize dataset: Phone numbers "
                                                  "should be equal ({0}) ({1})".format(phone_source, phone))

            ds.schema.contactPoint_dcat['0'].hasTelephone_vcard['0'].hasValue_vcard['0'].uri = "123456"
            phone_new = ds.schema.contactPoint_dcat['0'].hasTelephone_vcard['0'].hasValue_vcard['0'].uri

            self.assertNotEqual(phone, phone_new, "Test serialize dataset: Phone numbers "
                                                  "should be different ({0}) ({1})".format(phone_new, phone))

    def test_validate(self):  # TODO finish the test
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            # compare lengths of the report and the validation rules
            # report = ds.schema.validate_schema()

            dataset_validation_report = ds.validate_dataset()
            self.assertEqual(len(dataset_validation_report), 4, "Size of the report incorrect")

    def test_delete_from_ts(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            ds.get_description_from_ts()
            ds.delete_from_ts()
            ds.get_description_from_ts()
            count_ttl_lines = len(ds.ttl_as_in_ts.splitlines(2))
            self.assertTrue(count_ttl_lines == 2, "Delete dataset from ts failed")

    def test_create_multi_lang_full_text(self):  # TODO finish it
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            mega_field = ds.create_multi_lang_full_text()
            # TODO add an assertion
            pass

    def test_export_to_json(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V3")
        if ds.get_description_from_ts():
            json_dict = {}
            json_string = ds.get_dataset_as_json()

            pass
            # todo add assert

    def test_generate_list_properties(self):
        dict_prop = DatasetDcatApOp('').schema.__dict__  # type: dict[str,str]
        list_mapping = {}
        for prop in dict_prop.keys():
            # remove the name space

            list_mapping[prop] = prop

        pass

    def test_get_dataset_as_rdfxml(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V3")
        if ds.get_description_from_ts():
            rdf_xml = ds.get_dataset_as_rdfxml()
            tag = "<dcatapop:ckanName>dgt-translation-memory-V3</dcatapop:ckanName>"
            ns = 'xmlns:dcatapop="http://data.europa.eu/88u/ontology/dcatapop#"'
            self.assertTrue(tag in rdf_xml)
            self.assertTrue(ns in rdf_xml)
            pass

    def test_empty_resourcevalue(self):
        res = ResourceValue('')
        re2 = ResourceValue(None)
        self.assertEqual(res.value_or_uri, '')
        self.assertEqual(re2.value_or_uri, '')

    def test_create_statement_with_literal(self):
        res = ResourceValue(None)
        from ckanext.ecportal.model.utils_convertor import ConvertorFactory
        stm = ConvertorFactory.create_statement_with_literal("<o1>", "<p1>", res.value_or_uri)
        pass

    def test_register_doi(self):
        '''
        integration test for doi registration
        :return:
        '''
        import pickle
        from doi.configuration.doi_configuration import DOIConfiguration
        file_path = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/datasets/doi-test1.pickle"

        # Set up test configuration
        _TEST_CONFIG = DOIConfiguration()
        _TEST_CONFIG.doi_prefix = '10.2899'
        _TEST_CONFIG.doi_db_connection_string = 'postgresql://ecodp:password@127.0.0.1/ecodp'
        _TEST_CONFIG.email_host = 'ms1.cube-lux.lan'
        _TEST_CONFIG.email_port = 25
        _TEST_CONFIG.email_is_authenticated = False
        _TEST_CONFIG.email_username = ''
        _TEST_CONFIG.email_password = ''
        _TEST_CONFIG.report_log_directory = '/tmp'
        _TEST_CONFIG.report_sender_email = 'younes.djaghloul@arhs-cube.com'
        _TEST_CONFIG.report_receiver_email = 'alexandre.beaumont@arhs-cube.Com'
        _TEST_CONFIG.submission_doi_ra_url = 'https://ra-publications-dev.medra.org/servlet/ws/doidata'
        _TEST_CONFIG.submission_doi_ra_user = 'MOUGEOT'
        _TEST_CONFIG.submission_doi_ra_password = 'D0OPWBNN'
        _TEST_CONFIG.submission_doi_sender_email = 'alexandre.beaumont@arhs-cube.com'
        _TEST_CONFIG.submission_doi_from_company = 'Publications Office'
        _TEST_CONFIG.submission_doi_to_company = 'OP'

        # Get dataset from pickle file
        with open(file_path, "rb") as ds_file:
            ds = pickle.load(ds_file)  # type: DatasetDcatApOp

        # Get dataset by URI from triplestore
        # ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/the-community-fishing-fleet-register")
        # ds.get_description_from_ts()

        from doi.facade.doi_facade import DOIFacade
        facade_doi_test = DOIFacade(_TEST_CONFIG)
        # Update the dataset with the new genearted DOI

        doi_str = facade_doi_test.generate_doi("PUBL", uri=ds.dataset_uri)
        from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric
        identifier = SchemaGeneric(doi_str)
        identifier.type_rdf = {"0":SchemaGeneric("http:testdoi")}
        ds.schema.identifier_adms = {'0': identifier}
        doi_dict = ds.build_DOI_dict()
        facade_doi_test.register_doi(doi_str, doi_dict)

        pass
    def test_update_dataset(self):

        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset"
                             "/european-structural-investment-funds-esif-2014-2020-finance-implementation-details")
        ds.get_description_from_ts()
        ds.save_to_ts()

    def test_get_revisions(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset"
                             "/european-structural-investment-funds-esif-2014-2020-finance-implementation-details")
        ds.get_description_from_ts()
        list_of_revisions =ds.get_list_revisions_ordred(2)
        pass
        # ds.save_to_ts()


        pass
