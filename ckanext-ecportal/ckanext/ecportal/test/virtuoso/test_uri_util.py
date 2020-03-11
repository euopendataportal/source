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

from pylons import config

import ckanext.ecportal.lib.uri_util as uri_util
from ckanext.ecportal.model.schemas.dcatapop_dataset_schema import DatasetSchemaDcatApOp

DEFAULT_URI = "uri"


class TestUriUtil(unittest.TestCase):
    def setUp(self):
        self._original_config = config.copy()
        config['ckan.ecodp.uri_prefix'] = 'http://data.europa.eu/88u'

    def test_name_creation_from_title(self):
        name = uri_util.create_name_from_title('Test Title')
        self.assertEqual(name, 'Test-Title')

    def test_name_creation_from_unicode_title(self):
        name = uri_util.create_name_from_title('Test Title©Unicode §')
        self.assertEqual(name, 'Test-TitleUnicode')

    def test_is_uri_valid(self):
        invalide_uri = "http://arhs.com error"
        valide_uri = "http://arhs.com"
        self.assertTrue(uri_util.is_uri_valid(valide_uri))
        self.assertFalse(uri_util.is_uri_valid(invalide_uri))

