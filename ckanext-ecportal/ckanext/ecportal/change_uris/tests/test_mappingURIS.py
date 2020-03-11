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
from ckanext.ecportal.change_uris.mapping_component import MappingURIS
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration

_TEST_URI_DATASET = "http://data.europa.eu/88u/dataset/dgt-translation-memory"
_TEST_OLD_URI=""
_TEST_NEW_URI =""
_TEST_ACTION = "update"
class TestMappingURIS(TestWithVirtuosoConfiguration):
    def test_build_mapping_uri(self):

        mapping = MappingURIS()
        mapping.build_mapping_uri(_TEST_URI_DATASET,_TEST_OLD_URI,_TEST_NEW_URI,"PUBL")
        self.assertTrue(mapping.is_valid)



    def test_update_dataset_url(self):

        pass

    def test_validate_mapping(self):
        self.fail()

    def test_load_dataset(self):
        self.fail()
