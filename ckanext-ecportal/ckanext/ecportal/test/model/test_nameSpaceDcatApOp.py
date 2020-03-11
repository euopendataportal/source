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

from unittest import TestCase
from ckanext.ecportal.model.schemas.dcatapop_namespace import NAMESPACE_DCATAPOP


class TestNameSpaceDcatApOp(TestCase):
    def test_get_namespace(self):
        ns = NAMESPACE_DCATAPOP.get_namespace("http://data.europa.eu/88u/ontology/dcatapop#")
        self.assertEqual(ns,"dcatapop")
        pass

    def test_get_prefix(self):
        prefix_dcatapop = NAMESPACE_DCATAPOP.get_prefix("dcatapop")
        self.assertEqual(prefix_dcatapop, "http://data.europa.eu/88u/ontology/dcatapop#")
        #second way
        prefix_dcatapop = getattr(NAMESPACE_DCATAPOP,'dcatapop')
        self.assertEqual(prefix_dcatapop, "http://data.europa.eu/88u/ontology/dcatapop#", "ERROR whene using gettattr")
        pass

    def test_get_direct_prefix(self):
        prefix_dcatapop = NAMESPACE_DCATAPOP.dcatapop
        self.assertEqual(prefix_dcatapop, "http://data.europa.eu/88u/ontology/dcatapop#")
        pass

    def test_generate_uri_from_member_name(self):
        member = "hasQualityAnnotation_dqv"
        uri = NAMESPACE_DCATAPOP.generate_uri_from_member_name(member)
        self.assertEqual(uri,"http://www.w3.org/ns/dqv#hasQualityAnnotation")


    def test_convert_invalid_character(self):
        member = "organisation-name_vcard"
        member2 = 'organisation.name_vcard'
        member3 = 'organi.sation-name_vcard'

        self.assertEqual(NAMESPACE_DCATAPOP.convert_character_to_text(member), 'organisationDASHname_vcard')
        self.assertEqual(NAMESPACE_DCATAPOP.convert_character_to_text(member2), 'organisationDOTname_vcard')
        self.assertEqual(NAMESPACE_DCATAPOP.convert_character_to_text(member3), 'organiDOTsationDASHname_vcard')

        text_member = 'organisationDASHname_vcard'
        text_member2 = 'organisationDOTname_vcard'
        text_member3 = 'organiDOTsationDASHname_vcard'

        self.assertEqual(NAMESPACE_DCATAPOP.convert_text_to_character(text_member), 'organisation-name_vcard')
        self.assertEqual(NAMESPACE_DCATAPOP.convert_text_to_character(text_member2), 'organisation.name_vcard')
        self.assertEqual(NAMESPACE_DCATAPOP.convert_text_to_character(text_member3), 'organi.sation-name_vcard')