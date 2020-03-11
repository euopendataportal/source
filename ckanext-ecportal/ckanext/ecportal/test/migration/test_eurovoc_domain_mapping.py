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
from ckanext.ecportal.model.utils_convertor import EUROVOC_DOMAINS_MAPPING

class TestEurovoc_Domain_Mapping(unittest.TestCase):
     def test_inverse_mapping(self):

        mapping_validation = {}
        for domain, mapped_themes in EUROVOC_DOMAINS_MAPPING.items():

            for theme in mapped_themes:
                tmp_domains = mapping_validation.get(theme, [])
                tmp_domains.append(domain)
                mapping_validation[theme] = tmp_domains
        self.assertTrue(len(mapping_validation)>1)