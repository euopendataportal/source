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
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil, CorporateBodiesUtil


TEST_MDR = 'http://publications.europa.eu/resource/authority/data-theme'
THEME = 'http://publications.europa.eu/resource/authority/data-theme/TECH'

class TestControlledVocabularyUtil(unittest.TestCase):

    def setUp(self):
        config['virtuoso.host.name'] = 'http://10.2.0.121:8890/sparql'
        config['virtuoso.host.name.auth'] = 'http://10.2.0.121:8890/sparql-auth'

    def test_get_from_ts(self):
        mdr = ControlledVocabularyUtil(TEST_MDR)

        self.assertIsNotNone(mdr)


    def test_get_all_translations_for_mdr_item(self):

        mdr = ControlledVocabularyUtil(TEST_MDR)
        mdr_description = mdr.get_concept_description(THEME)

        all_transations = mdr.get_all_translations(THEME)
        self.assertEqual(all_transations.get('en', ''), 'Science and technology')


    def test_get_mdr_translation(self):
        mdr = ControlledVocabularyUtil(TEST_MDR)

        transations = mdr.get_translation_for_language(THEME, 'en')

        self.assertEqual(transations, 'Science and technology')


    def test_publisher_util(self):
        factory = ControlledVocabularyFactory()

        publisher = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.CORPORATE_BODY) #type: CorporateBodiesUtil
        children = publisher.get_first_level_publishers()

        self.assertIsNot(None, children, "List is None")


