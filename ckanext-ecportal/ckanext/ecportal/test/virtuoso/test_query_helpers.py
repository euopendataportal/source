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
from ckanext.ecportal.virtuoso.utils_triplestore_query_helpers import TripleStoreQueryHelpers

tsqh = None


class TestQueryHelpers(TestWithVirtuosoConfiguration):
    def test_get_uri_datasets(self):
        tsqh = TripleStoreQueryHelpers()
        list_of_datasets = tsqh.get_uri_datasets()
        self.assertTrue(len(list_of_datasets)>0)

    def test_get_resources_datasets(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_resources_of_datasets()
        self.assertTrue(len(list_resources)>1)
        pass

    def test_get_resource_formats(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_resource_formats()
        self.assertTrue(len(list_resources)>1)

    def test_get_dataset_ids_with_issued_date(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_dataset_ids_with_issued_date()
        self.assertTrue(len(list_resources)>1)

    def test_get_revision_ids_with_issued_date(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_revision_ids_with_issued_date()
        self.assertTrue(len(list_resources)>1)

    def test_get_revision_count_for_datastet(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_revision_count_for_datastet()
        self.assertTrue(len(list_resources)>1)

    def test_get_top_groups(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_top_groups()
        self.assertTrue(len(list_resources)>1)

    def test_get_top_keywords(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_top_keywords()
        self.assertTrue(len(list_resources)>1)

    def test_get_themes(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_top_themes()
        self.assertTrue(len(list_resources)>1)

    def test_get_themes(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_top_languages()
        self.assertTrue(len(list_resources)>1)

    def test_get_themes(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_top_countries()
        self.assertTrue(len(list_resources)>1)

    def test_get_themes(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_top_subjects()
        self.assertTrue(len(list_resources)>1)


    def test_is_ckanName_unique(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.is_ckanName_unique('S2081_84_4_444_ENG')
        self.assertFalse(list_resources)


    def test_is_ckanName_unique(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.is_ckanName_unique('simple-test-name-unique')
        self.assertTrue(list_resources)

    def test_get_all_keywords(self):
        tsqh = TripleStoreQueryHelpers()
        list_resources = tsqh.get_all_keywords()
        self.assertTrue(list_resources)
