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
from doi.generator.doi_generator import DOIGenerator
from doi.generator.doi_generator import DOI
from doi.controllers.doi_controller import DOISController
from doi.storage.doi_storage_sqlalchemy import DOIStorageSQLAlchemy


class DOIGeneratorTest(unittest.TestCase):

    _TEST_CONFIG = DOIConfiguration()
    _TEST_CONFIG.doi_prefix = 'test.generator'
    _TEST_CONFIG.doi_db_connection_string = 'postgresql://ecodp:password@127.0.0.1/ecodp'

    _STORAGE = DOIStorageSQLAlchemy(_TEST_CONFIG.doi_db_connection_string)
    _doi_controller = DOISController(storage=_STORAGE)
    _doi_generator = DOIGenerator(_doi_controller, _TEST_CONFIG.doi_prefix)
    _data = {
        'providers': ['jrc', 'com', 'acp-eu_jpa', 'none', 'ahah'],
        'uris': ['uri/test/aaa', 'uri/test/2', 'uri/test/catalog/888', '99d9-azfz4-vn55gn', 'test.uri', 'test.with.custom.suffix']
    }

    # Delete old values
    _doi_controller.remove_all_doi(prefix=_TEST_CONFIG.doi_prefix)

    def test_doi_incrementation_per_provider(self):
        provider_a = DOIGeneratorTest._data['providers'][0]
        provider_b = DOIGeneratorTest._data['providers'][1]
        provider_a_first_doi = DOIGeneratorTest._doi_generator.generate(provider_a)
        provider_b_first_doi = DOIGeneratorTest._doi_generator.generate(provider_b)

        i = 1
        while i < 5:
            doi = DOIGeneratorTest._doi_generator.generate(provider_a)
            self.assertEquals(int(provider_a_first_doi.get_suffix_element()) + i, int(doi.get_suffix_element()))
            i += 1

        j = 1
        while j < 5:
            doi = DOIGeneratorTest._doi_generator.generate(provider_b)
            self.assertEquals(int(provider_b_first_doi.get_suffix_element()) + j, int(doi.get_suffix_element()))
            j += 1

        while i < 10:
            doi = DOIGeneratorTest._doi_generator.generate(provider_a)
            self.assertEquals(int(provider_a_first_doi.get_suffix_element()) + i, int(doi.get_suffix_element()))
            i += 1

        while j < 10:
            doi = DOIGeneratorTest._doi_generator.generate(provider_b)
            self.assertEquals(int(provider_b_first_doi.get_suffix_element()) + j, int(doi.get_suffix_element()))
            j += 1

    def test_doi_format(self):
        provider = DOIGeneratorTest._data['providers'][2]
        doi = DOIGeneratorTest._doi_generator.generate(provider)
        self.assertEquals(DOIGeneratorTest._TEST_CONFIG.doi_prefix, doi.get_prefix())
        self.assertEquals(provider, doi.get_suffix_provider())

    def test_doi_persistence(self):
        provider = DOIGeneratorTest._data['providers'][2]
        uri = DOIGeneratorTest._data['uris'][3]
        DOIGeneratorTest._doi_controller.remove_association_by_uri(uri)

        doi_first_generation = DOIGeneratorTest._doi_generator.generate(provider, uri)
        doi_second_generation = DOIGeneratorTest._doi_generator.generate(provider, uri)
        self.assertEquals(doi_first_generation, doi_second_generation)

    def test_doi_assign_suffix(self):
        provider = DOIGeneratorTest._data['providers'][4]
        uri = DOIGeneratorTest._data['uris'][2]
        DOIGeneratorTest._doi_controller.remove_association_by_uri(uri)

        doi = DOI(DOIGeneratorTest._TEST_CONFIG.doi_prefix, provider, "5")
        DOIGeneratorTest._doi_controller.set_doi_association(doi, uri)

        doi_second_generation = DOIGeneratorTest._doi_generator.generate(provider, uri)
        self.assertEquals(doi, doi_second_generation)

    def test_doi_uniqueness_exception(self):
        provider = DOIGeneratorTest._data['providers'][3]
        uri = DOIGeneratorTest._data['uris'][4]

        doi_first_generation = DOIGeneratorTest._doi_generator.generate(provider)
        value = str(int(doi_first_generation.get_suffix_element()) + 1)

        DOIGeneratorTest._doi_controller.remove_association_by_uri(uri)

        doi = DOI(DOIGeneratorTest._TEST_CONFIG.doi_prefix, provider, value)
        DOIGeneratorTest._doi_controller.set_doi_association(doi, uri)

        self.assertRaises(Exception, DOIGeneratorTest._doi_generator.generate, provider=provider)

    def test_doi_generation_with_custom_suffix(self):
        provider = DOIGeneratorTest._data['providers'][3]
        suffix = "TEST_SUFFIX"
        uri = DOIGeneratorTest._data['uris'][5]

        DOIGeneratorTest._doi_controller.remove_association_by_uri(uri)

        doi = DOIGeneratorTest._doi_generator.generate(provider, suffix=suffix)

        DOIGeneratorTest._doi_controller.set_doi_association(doi, uri)

        self.assertEquals(doi.get_suffix_element(), suffix)
        self.assertRaises(Exception, DOIGeneratorTest._doi_generator.generate, provider=provider, suffix=suffix)


if __name__ == '__main__':
    unittest.main()
