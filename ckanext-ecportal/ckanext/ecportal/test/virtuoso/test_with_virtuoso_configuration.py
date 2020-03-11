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

from ConfigParser import ConfigParser
from unittest import TestCase

from pylons import config

from ckanext.ecportal.test.configuration.configuration_constants import VIRTUOSO_HOST_NAME, VIRTUOSO_CONFIG_FILE_PATH
from ckanext.ecportal.test.virtuoso.common_constants import VIRTUOSO_HOST_NAME_AUTHENTICATED

import logging, sys

parser = ConfigParser()
parser.read(
    VIRTUOSO_CONFIG_FILE_PATH)
parser_name = parser.get('config', 'parser.to.choose')

virtuoso_host_name = parser.get(parser_name, VIRTUOSO_HOST_NAME)
virtuoso_host_name_authenticated = parser.get(parser_name, VIRTUOSO_HOST_NAME_AUTHENTICATED)

config[VIRTUOSO_HOST_NAME] = virtuoso_host_name
config[VIRTUOSO_HOST_NAME_AUTHENTICATED] = virtuoso_host_name_authenticated
config["ckan.cache.active"] = "true"


class TestWithVirtuosoConfiguration(TestCase):
    def setUp(self):
        logging.basicConfig( stream=sys.stderr )
