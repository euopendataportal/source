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

TEST_MDR = 'http://publications.europa.eu/resource/authority/data-theme'
THEME = 'http://publications.europa.eu/resource/authority/data-theme/TECH'


class TestControlledVocabularyFactory(unittest.TestCase):

    def setUp(self):
        config['virtuoso.host.name'] = 'http://10.2.0.121:8890/sparql'
        config['virtuoso.host.name.auth'] = 'http://10.2.0.121:8890/sparql-auth'



    def test_mdr_factory(self):

        factory = ControlledVocabularyFactory()
        mdr_util = factory.get_controlled_vocabulary_util(factory.DATA_THEME)

        self.assertNotEqual(None, mdr_util,' Could not instanciate mdr_util')

    def test_mdr_factory_with_list(self):

        factory = ControlledVocabularyFactory()
        mdr_util = factory.get_controlled_vocabulary_util([factory.DATA_THEME, factory.LICENSE])

        self.assertNotEqual(None, mdr_util,' Could not instanciate mdr_util')

