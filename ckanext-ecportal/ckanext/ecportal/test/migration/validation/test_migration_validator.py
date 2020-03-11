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

import logging

from ckanext.ecportal.migration.error.migration_error import MigrationError
from ckanext.ecportal.migration.validation import migration_validator
from ckanext.ecportal.model.schemas.dcatapop_dataset_schema import DatasetSchemaDcatApOp
from ckanext.ecportal.test.configuration.configuration_constants import TEST_CONFIG_FILE_PATH
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration

log = logging.getLogger(__file__)


class TestMigrationValidator(TestWithVirtuosoConfiguration):
    def test_validate_migration(self):
        ret = migration_validator.validate_migration(TEST_CONFIG_FILE_PATH)
        assert ret is True

    def test_find_from_variables_names(self):
        ret = migration_validator.find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "page_foaf",
                                                                       "url_schema")
        assert len(ret) > 0

    def test_find_from_variables_main_title(self):
        ret = migration_validator.find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "title_dcterms")
        assert len(ret) > 0

    def test_validate_dataset_name(self):
        try:
            migration_validator.validate_dataset_name(TEST_CONFIG_FILE_PATH)
        except MigrationError as e:
            error = "Test failed: [{0}]".format(e.value)
            logging.warn(error)
            self.fail()

    def test_validate_dataset_field(self):
        try:
            migration_validator.validate_simple_dataset_field(TEST_CONFIG_FILE_PATH, DatasetSchemaDcatApOp, "", "title",
                                                              "title_dcterms")
        except MigrationError as e:
            error = "Test failed: [{0}]".format(e.value)
            logging.warn(error)
            self.fail()

    def test_validate_dataset_metadata_modified_field(self):
        try:
            migration_validator.validate_simple_dataset_field(TEST_CONFIG_FILE_PATH, DatasetSchemaDcatApOp, "",
                                                              "metadata_modified", "modified_dcterms")
        except MigrationError as e:
            error = "Test failed: [{0}]".format(e.value)
            logging.warn(error)
            self.fail()

    def test_validate_keywords(self):
        try:
            migration_validator.validate_keywords(TEST_CONFIG_FILE_PATH)
        except MigrationError as e:
            error = "Test failed: [{0}]".format(e.value)
            logging.warn(error)
            self.fail()

    def test_validate_themes(self):
        try:
            migration_validator.validate_themes(TEST_CONFIG_FILE_PATH)
        except MigrationError as e:
            error = "Test failed: [{0}]".format(e.value)
            logging.warn(error)
            self.fail()

    def test_validate_temporal(self):
        try:
            migration_validator.validate_temporal_coverages(TEST_CONFIG_FILE_PATH)
        except MigrationError as e:
            error = "Test failed: [{0}]".format(e.value)
            logging.warn(error)
            self.fail()

    def test_validate_alternative_title(self):
        try:
            migration_validator.validate_alternative_titles(TEST_CONFIG_FILE_PATH)
        except MigrationError as e:
            error = "Test failed: [{0}]".format(e.value)
            logging.warn(error)
            self.fail()
