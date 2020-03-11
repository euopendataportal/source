# -*- coding: utf-8 -*-
# Copyright (C) 2019  Publications Office of the European Union

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
from ckanext.ecportal.model.identifier_mapping import DatasetIdMapping


class TestDatasetIdMapper(unittest.TestCase):

    def setUp(self):
        config['sqlalchemy.url'] = 'postgresql://ecodp:password@10.2.0.113/ecodp'


    def test_get_mapped_id(self):
        mapping = DatasetIdMapping.by_internal_id('post_dtr_1')
        self.assertNotEqual(None, mapping)

