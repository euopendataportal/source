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


from doi.facade.doi_facade import DOIFacade
from doi.configuration.doi_configuration import DOIConfiguration


class DOIFacadeTest(unittest.TestCase):

    # Set up test configuration
    _TEST_CONFIG = DOIConfiguration()
    _TEST_CONFIG.doi_prefix = 'prefix'
    _TEST_CONFIG.doi_db_connection_string = ''
    _TEST_CONFIG.email_host = 'ms1.cube-lux.lan'
    _TEST_CONFIG.email_port = 25
    _TEST_CONFIG.email_is_authenticated = False
    _TEST_CONFIG.email_username = ''
    _TEST_CONFIG.email_password = ''
    _TEST_CONFIG.report_log_directory = '/tmp'
    _TEST_CONFIG.report_sender_email = 'OP.Project-ODP@arhs-cube.Com'
    _TEST_CONFIG.report_receiver_email = 'test-mail@arhs-cube.Com'
    _TEST_CONFIG.submission_doi_ra_url = 'https://ra.publications.europa.eu/servlet/ws/doidata'
    _TEST_CONFIG.submission_doi_ra_user = 'user'
    _TEST_CONFIG.submission_doi_ra_password = 'password'
    _TEST_CONFIG.citation_formats = {
        "json": {
            "name": "JSON",
            "format": "application/vnd.citationstyles.csl+json",
            "extension": "json"
        }
    }
    _TEST_CONFIG.citation_resolver = 'https://citation.crosscite.org/format'
    _TEST_CONFIG.citation_file_resolver = 'https://data.datacite.org/'
    _TEST_CONFIG.citation_style = 'harvard-cite-them-right'

    _TEST_PROVIDER = 'odp'
    _TEST_DOI = 'test/doi-1'

    _doi_manager = DOIFacade(_TEST_CONFIG)

    def test_generate_doi(self):
        generated_poi = self._doi_manager.generate_doi(self._TEST_PROVIDER)
        self.assertNotEquals(None, generated_poi)
        self.assertNotEquals('', generated_poi)

    def test_register_doi(self):
        self._doi_manager.register_doi(DOIFacadeTest._TEST_DOI, {})


if __name__ == '__main__':
    unittest.main()
