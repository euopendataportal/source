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

import pickle

from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric
from doi.configuration.doi_configuration import DOIConfiguration
from doi.facade.doi_facade import DOIFacade
from virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration


class TestCatalogDcatApOp(TestWithVirtuosoConfiguration):

    def test_register_doi(self):
        """
        integration test for doi registration
        :return:
        """
        file_path = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/catalogs/my-first-catalogue.pickle"

        # Set up test configuration
        _TEST_CONFIG = DOIConfiguration()
        _TEST_CONFIG.doi_prefix = '10.2899'
        _TEST_CONFIG.doi_db_connection_string = 'postgresql://ecodp:password@127.0.0.1/ecodp'
        _TEST_CONFIG.email_host = 'ms1.cube-lux.lan'
        _TEST_CONFIG.email_port = 25
        _TEST_CONFIG.email_is_authenticated = False
        _TEST_CONFIG.email_username = ''
        _TEST_CONFIG.email_password = ''
        _TEST_CONFIG.report_log_directory = '/tmp'
        _TEST_CONFIG.report_sender_email = 'younes.djaghloul@arhs-cube.com'
        _TEST_CONFIG.report_receiver_email = 'alexandre.beaumont@arhs-cube.Com'
        _TEST_CONFIG.submission_doi_ra_url = 'https://ra-publications-dev.medra.org/servlet/ws/doidata'
        _TEST_CONFIG.submission_doi_ra_user = 'MOUGEOT'
        _TEST_CONFIG.submission_doi_ra_password = 'D0OPWBNN'
        _TEST_CONFIG.submission_doi_sender_email = 'alexandre.beaumont@arhs-cube.com'
        _TEST_CONFIG.submission_doi_from_company = 'Publications Office'
        _TEST_CONFIG.submission_doi_to_company = 'OP'

        # Get catalogs from pickle file
        with open(file_path, "rb") as catalog_file:
            catalog = pickle.load(catalog_file)  # type: CatalogDcatApOp

        facade_doi_test = DOIFacade(_TEST_CONFIG)
        # Update the catalog with the new generated DOI

        doi_str = facade_doi_test.generate_doi("ODP", catalog.catalog_uri)
        catalog.schema.identifier_adms = {'0': SchemaGeneric(doi_str)}
        doi_dict = catalog.build_DOI_dict()
        facade_doi_test.register_doi(doi_str, doi_dict)
