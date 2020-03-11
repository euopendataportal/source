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
from doi.storage.doi_storage_sqlalchemy import DOIStorageSQLAlchemy
from doi.domain.doi_object import DOI


class DOIStorageTest(unittest.TestCase):

    _TEST_CONFIG = DOIConfiguration()
    _TEST_CONFIG.doi_prefix = 'test.storage'
    _TEST_CONFIG.doi_db_connection_string = 'postgresql://ecodp:password@127.0.0.1/ecodp'

    _storage = DOIStorageSQLAlchemy(_TEST_CONFIG.doi_db_connection_string)

    _data = {
        'providers': ['provider_1', 'abc', 'publisher-test', 'group'],
        'uris': ['uri/storage/test/aaa', 'uri/storage/test/bbb', 'uri/storage/test/catalog/0', 'aff8s-84z4s-5s41d4']
    }

    # Delete old values
    _storage.delete_all(prefix=_TEST_CONFIG.doi_prefix)

    def test_insert(self):
        prefix = DOIStorageTest._TEST_CONFIG.doi_prefix
        provider = DOIStorageTest._data['providers'][0]
        value = "8"
        doi1 = DOI(prefix, provider, value)

        # Do not exist at this moment
        self.assertEquals(None, DOIStorageTest._storage.find_one(prefix=prefix, provider=provider, value=value))

        # Insert the new DOI
        DOIStorageTest._storage.save(doi1)

        # Exist at this moment and could be the same as provided
        self.assertEquals(doi1, DOIStorageTest._storage.find_one(prefix=prefix, provider=provider, value=value))

    def test_update(self):
        prefix = DOIStorageTest._TEST_CONFIG.doi_prefix
        provider = DOIStorageTest._data['providers'][1]
        value = "10"
        uri = DOIStorageTest._data['uris'][3]
        doi1 = DOI(prefix, provider, value, None)

        # Insert a new DOI
        DOIStorageTest._storage.save(doi1)

        # Exist at this moment and could be the same as provided
        self.assertEquals(doi1, DOIStorageTest._storage.find_one(prefix=prefix, provider=provider, value=value))

        # Update the DOI
        doi1.set_uri(uri)
        DOIStorageTest._storage.save(doi1)

        # Exist at this moment and could be the same as provided
        self.assertEquals(doi1, DOIStorageTest._storage.find_one(uri=uri))

    def test_next_doi(self):
        prefix = DOIStorageTest._TEST_CONFIG.doi_prefix
        provider = DOIStorageTest._data['providers'][2]

        initial_len = len(DOIStorageTest._storage.find(provider=provider))

        # Create 3 new DOIs
        doi1 = DOIStorageTest._storage.next_doi(prefix, provider)
        doi2 = DOIStorageTest._storage.next_doi(prefix, provider)
        doi3 = DOIStorageTest._storage.next_doi(prefix, provider)

        self.assertTrue(int(doi1.get_suffix_element()) < int(doi2.get_suffix_element()) < int(doi3.get_suffix_element()))
        self.assertEquals(initial_len+3, len(DOIStorageTest._storage.find(provider=provider)))

    def test_delete_doi(self):
        prefix = DOIStorageTest._TEST_CONFIG.doi_prefix
        provider = DOIStorageTest._data['providers'][0]

        # Create one new DOI
        created_doi = DOIStorageTest._storage.next_doi(prefix, provider)

        self.assertEquals(created_doi, DOIStorageTest._storage.find_one(prefix=created_doi.get_prefix(), provider=created_doi.get_suffix_provider(), value=created_doi.get_suffix_element()))

        # Delete the created DOI
        DOIStorageTest._storage.delete(prefix=created_doi.get_prefix(), provider=created_doi.get_suffix_provider(), value=created_doi.get_suffix_element())

        self.assertEquals(None, DOIStorageTest._storage.find_one(prefix=created_doi.get_prefix(), provider=created_doi.get_suffix_provider(), value=created_doi.get_suffix_element()))

    def test_get_all_doi(self):
        prefix = DOIStorageTest._TEST_CONFIG.doi_prefix
        provider = DOIStorageTest._data['providers'][3]

        dois = [
            DOI(prefix, provider, "6"),
            DOI(prefix, provider, "8"),
            DOI(prefix, provider, "9"),
            DOI(prefix, provider, "10"),
            DOI(prefix, provider, "11")
        ]

        # Save all new DOI
        for doi in dois:
            DOIStorageTest._storage.save(doi)

        # Get all DOI from the same provider
        entries = DOIStorageTest._storage.find(prefix=prefix, provider=provider)

        self.assertTrue(all(elem in entries for elem in dois))
        self.assertFalse(DOI(prefix, 'vec', "6") in entries)
        self.assertFalse(DOI('--', provider, "6") in entries)
