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
from doi.mapper.mapping_value_service import MappingValue
from doi.exceptions.doi_mapper_exception import DOIMapperException

#    contact: <https://publications.europa.eu/en/web/about-us/contact>
class TestMappingValue(TestCase):
    def test_mapping_from_odp_publisher_id_to_doi_publisher_numerical_id(self):
        mapper = MappingValue()
        publisher_odp_id = "abcefghijklmnopqrstuvwxyz1234567890-/*+_"
        expected_conversion = "097098099101102103104105106107108109110111112113114115116117118119120121122049050051052053054055056057048045047042043095"
        conversion = MappingValue.mapping_from_odp_publisher_id_to_doi_publisher_numerical_id(publisher_odp_id)

        self.assertEqual(conversion,expected_conversion, "The mapping is incorrect")
        self.assertRaises(DOIMapperException,mapper.mapping_from_odp_publisher_id_to_doi_publisher_numerical_id,112)


    def test_mapping_from_doi_publisher_numerical_id_to_odp_publisher_id(self):
        mapper = MappingValue()
        expected_conversion = "abcefghijklmnopqrstuvwxyz1234567890-/*+_"
        publisher_doi_id = "097098099101102103104105106107108109110111112113114115116117118119120121122049050051052053054055056057048045047042043095"
        conversion = MappingValue.mapping_from_doi_publisher_numerical_id_to_odp_publisher_id(publisher_doi_id)
        self.assertEqual(conversion, expected_conversion, "The mapping is incorrect")
        self.assertRaises(DOIMapperException,mapper.mapping_from_doi_publisher_numerical_id_to_odp_publisher_id, "00")



