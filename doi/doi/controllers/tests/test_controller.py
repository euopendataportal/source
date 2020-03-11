# -*- coding: utf-8 -*-
# Copyright (C) 2018  ARhS-CUBE

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


import unittest

from doi.configuration.doi_configuration import DOIConfiguration
from doi.controllers.doi_controller import DOISController
from doi.domain.doi_object import DOI
from doi.storage.doi_storage_sqlalchemy import DOIStorageSQLAlchemy


class DOIControllerTest(unittest.TestCase):

    _TEST_CONFIG = DOIConfiguration()
    _TEST_CONFIG.doi_prefix = 'test.controller'
    _TEST_CONFIG.doi_db_connection_string = 'postgresql://ecodp:password@127.0.0.1/ecodp'

    _CITATION_DEFAULT_FORMAT = 'text/x-bibliography'
    _CITATION_DEFAULT_STYLE = 'harvard-cite-them-right'
    _CITATION_DEFAULT_LANGUAGE = 'en-GB'

    _STORAGE = DOIStorageSQLAlchemy(_TEST_CONFIG.doi_db_connection_string)
    _doi_controller = DOISController(storage=_STORAGE)
    _DOI_TEST_EXISTING = '10.5284/1015681'
    _DOI_TEST_NOT_FOUND = '10.5284/98989898'
    _CITATION_TEST = 'Archaeological Project Services. (1995). Excavation of a Romano-British Cemetery at the water treatment plant, Saltersford, Grantham, Lincolnshire. Archaeology Data Service. https://doi.org/10.5284/1015681'

    def test_get_citation(self):
        citation = DOIControllerTest._doi_controller.get_citation(DOIControllerTest._DOI_TEST_EXISTING,
                                                                  DOIControllerTest._CITATION_DEFAULT_FORMAT,
                                                                  DOIControllerTest._CITATION_DEFAULT_STYLE,
                                                                  DOIControllerTest._CITATION_DEFAULT_LANGUAGE)
        self.assertEqual(citation, DOIControllerTest._CITATION_TEST)
        self.assertRaises(Exception, DOIControllerTest._doi_controller.get_citation, DOIControllerTest._DOI_TEST_NOT_FOUND)

    def test_doi_create_custom_suffix(self):
        provider = 'arhs'
        suffix = "TEST_CUSTOM"

        doi = DOI(DOIControllerTest._TEST_CONFIG.doi_prefix, provider, suffix)
        DOIControllerTest._doi_controller.remove_all_doi(prefix=DOIControllerTest._TEST_CONFIG.doi_prefix, provider=provider, value=suffix)

        DOIControllerTest._doi_controller.set_doi_association(doi)

        self.assertTrue(DOIControllerTest._doi_controller.doi_exists(doi))

    def test_doi_assign_to_custom_suffix(self):
        provider = 'arhs'
        suffix = "TEST_CUSTOM"
        uri = 'URI.for.tests'

        DOIControllerTest._doi_controller.remove_association_by_uri(uri)

        doi = DOI(DOIControllerTest._TEST_CONFIG.doi_prefix, provider, suffix)
        if not DOIControllerTest._doi_controller.doi_exists(doi):
            DOIControllerTest._doi_controller.set_doi_association(doi)

        DOIControllerTest._doi_controller.set_doi_association(doi, uri)

        self.assertEqual(uri, DOIControllerTest._doi_controller.get_uri_by_doi(doi))

    def test_doi_custom_suffix_format(self):
        provider = 'arhs'
        suffixes_valid = ['test_1', '01.025', 'doi-valid', '(ok)', 'Normal']
        suffixes_invalid = ['#test2', 'f/f/f', 'test_with_$', '&aaa', '!?+bbb', '_.-;)(', ';k;', 'super test']

        for suffix in suffixes_valid:
            doi = DOI(DOIControllerTest._TEST_CONFIG.doi_prefix, provider, suffix)
            self.assertTrue(doi is not None)
            self.assertEqual(doi.get_suffix_element(), suffix)

        for suffix in suffixes_invalid:
            self.assertRaises(Exception, DOI, DOIControllerTest._TEST_CONFIG.doi_prefix, provider, suffix)
