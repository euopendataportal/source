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
from unittest import TestCase
import os
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
#    contact: <https://publications.europa.eu/en/web/about-us/contact>
from ckanext.ecportal.change_uris.mapping_component import MappingESTAT, MappingURIS

RESOURCE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/resources"
CSV_FILE_PATH = RESOURCE_PATH+"/csv_test.csv"
class TestMappingESTAT(TestWithVirtuosoConfiguration):

    def test_build_mapping_from_csv(self):
        '''
        Test the extraction from csv
        :return: 
        '''

        mapping = MappingESTAT(CSV_FILE_PATH,'update',RESOURCE_PATH,'COMP')
        mapping.build_mapping_from_csv()

        self.assertEqual(len(mapping.get_list_of_mappings()),2)
        self.assertEqual(mapping.get_mapping_by_old_uri("https://ec.europa.eu/jrc/en/language-technologies/dgt-transl"
                                                        "ation-memory").new_uri,"https://ec.europa.eu/jrc/en/language-technologies/dgt-translation-memory_new")
        pass
        # self.fail()

    def test_update_estat_datasets(self):
        mapping_estat = MappingESTAT(CSV_FILE_PATH)
        mapping_estat.build_mapping_from_csv()
        mapping_estat.update_estat_datasets()
        pass




