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


import unittest
import os, pickle, json

from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
from ckanext.ecportal.model.schema_validation.schema_validation import ValidationSchema, ValidationTypeResult
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration


from dcatapop_to_datacite_mapper.dcatapop_to_datacite_mapper import DCATAPOPToDataCiteMapper


class DCATAPOPToDataCiteMapperTest(TestWithVirtuosoConfiguration):

    _submission_doi_sender_email = 'alexandre.beaumont@arhs-cube.com'
    _submission_doi_from_company = 'Publications Office'
    _submission_doi_to_company = 'OP'

    _generate_mocked_datasets = False
    _mapper = DCATAPOPToDataCiteMapper(_submission_doi_sender_email, _submission_doi_from_company, _submission_doi_to_company)
    _RESOURCE_FOLDER = os.path.dirname(os.path.realpath(__file__)) + "/resources/"
    _ds_file_name = _RESOURCE_FOLDER + "doi-test1.pickle"
    _MOCK_DOI_DATASET = 'doi/jrc/123456'
    _MOCK_DOI_CATALOG = 'mock/doi-catalog'
    _MOCK_DATASET_DATA = {}
    _MOCK_CATALOG_DATA = {}  # TODO: add mock

    def setUp(self):
        '''
        Load the dataset from the pickle in _MOCK_DATASET_DATA.
        :return:
        '''

        def generate_pickled_dataset(activate = False):

            if activate:
                list_ds_vip = ["http://data.europa.eu/88u/dataset/doi-test1",
                               "http://data.europa.eu/88u/dataset/eurovoc",
                               "http://data.europa.eu/88u/dataset/dgt-translation-memory"
                                ]
                for ds_uri in list_ds_vip:
                    ds = DatasetDcatApOp(ds_uri)
                    ds.get_description_from_ts()
                    file_name = ds_uri.split("/")[-1] + ".pickle"
                    with open(self._RESOURCE_FOLDER+file_name, "w") as pickle_file:
                        pickle.dump(ds, pickle_file)

                    with open(self._RESOURCE_FOLDER + file_name+".json","w") as f:
                        json.dump(self._MOCK_DATASET_DATA, f)

        generate_pickled_dataset(self._generate_mocked_datasets)
        with open(self._ds_file_name, "rb") as ds_file:
            dataset = pickle.load(ds_file)  # type: DatasetDcatApOp
        self._MOCK_DATASET_DATA = dataset.build_DOI_dict()


        with open(self._ds_file_name+".json", "w") as f:
            content = json.dumps(self._MOCK_DATASET_DATA,ensure_ascii=False).encode("utf8")
            f.write(content)

        with open(self._ds_file_name+".json", "rb") as f:
           self._MOCK_DATASET_DATA = json.load(f)

    def test_generate_dataset_metadata(self):

        doi_xml_str = self._mapper.generate_dataset_metadata(self._MOCK_DOI_DATASET, self._MOCK_DATASET_DATA)
        assert doi_xml_str
        alternative = '<alternateIdentifier alternateIdentifierType="PURL">http://data.europa.eu/88u/dataset/doi-test1</alternateIdentifier>'
        self.assertTrue(doi_xml_str.find(alternative) != -1)

        import lxml.etree as ET
        from StringIO import StringIO

        f = StringIO(doi_xml_str)
        tree = ET.parse(f)
        list_language = []
        # ns = {"xmlns":"http://datacite.org/schema/kernel-4"}
        # root_ressource = tree.xpath("//xmlns:DOIData/xmlns:Metadata/xmlns:resource", namespaces = ns)[0]
        # for language in root_ressource.findall('language'):
        #     list_language.append(language.text)
        #a = set(list_language)==set(['en','fr'])
        # self.assertEqual(set(list_language),set(['en','fr']),"The genrated xml is not correct")

    def test_generate_catalog_metadata(self):
        uri = 'http://data.europa.eu/88u/catalog/my-first-catalogue'
        catalog = CatalogDcatApOp(uri)
        catalog.get_description_from_ts()

        file_name = uri.split("/")[-1] + ".pickle"
        with open(self._RESOURCE_FOLDER+file_name, "w") as pickle_file:
            pickle.dump(catalog, pickle_file)

        with open(self._RESOURCE_FOLDER + file_name+".json", "w") as f:
            json.dump(self._MOCK_DATASET_DATA, f)



    def test_register_doi_from_dataset(self):
        pass







if __name__ == '__main__':
    unittest.main()
