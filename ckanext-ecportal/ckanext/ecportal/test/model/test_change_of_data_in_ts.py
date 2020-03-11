# -*- coding: utf-8 -*-
# Copyright (C) 2018  Publications Office of the European Union

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>
import unittest
from pylons import config
import ckanext.ecportal.lib.ui_util as ui_util
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_identifier_schema import IdentifierSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
import ckanext.ecportal.lib.uri_util as uri_util


IDENTIFIER_LIST = ["%2525255B%2525255D",
"10.0299/EIGE/1",
"10.2899/PUBL/1",
"10.2899/EEA/1",
"10.2899/097099112095097109098/7",
"%5B%5D",
"http://data.europa.eu/88u/blanknode#__N9f46becedd6e4a91acf7d57778a50acc",
"10.2899/acp_amb/5",
"10.1109/5.771073",
"%255B%255D",
"%25255B%25255D",
"10.2905/944f6d9b-2fbf-422e-ae3e-4b3aa391ed48"]

class Test_Data_changes(unittest.TestCase):

    def setUp(self):
        config['virtuoso.host.name'] = 'http://10.2.1.33:8890/sparql'
        config['virtuoso.host.name.auth'] = 'http://10.2.1.33:8890/sparql-auth'

    def test_data_change_in_ts(self):

        ds = DatasetDcatApOp('http://data.europa.eu/88u/dataset/efsa-botanical-compendium')
        ds.get_description_from_ts()

        ds.schema.identifier_adms.get('0').uri = '10.5281/zenodo.1212387'
        result =ds.save_to_ts()

        self.assertTrue(result)

    def test_change_DOI_structure(self):
        result = False
        for id in IDENTIFIER_LIST:
            schema = IdentifierSchemaDcatApOp(id)
            schema.get_description_from_ts()

            if schema.notation_skos.get('0', ResourceValue('')).value_or_uri == "http://publications.europa.eu/resource/authority/notation-type/DOI":
                doi = schema.uri

                schema.notation_skos['0'] = ResourceValue(doi, datatype ="http://publications.europa.eu/resource/authority/notation-type/DOI")
                result = schema.save_to_ts()
                print "change {0} result {1}".format(id, result)

        self.assertTrue(result)

