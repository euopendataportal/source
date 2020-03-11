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
import sys
import time

from ckanext.ecportal.migration import datasets_migration_manager
from ckanext.ecportal.migration.datasets_migration_manager import ControlledVocabulary
from ckanext.ecportal.migration.migration_constants import DATASET_URI_PREFIX
from ckanext.ecportal.migration.postgresql.dto.postgresql_dtos import Package
from ckanext.ecportal.migration.postgresql.helpers import postgresql_helper
from ckanext.ecportal.migration.postgresql.helpers.postgresql_helper import find_any_in_database
from ckanext.ecportal.model.common_constants import DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.test.configuration.configuration_constants import TEST_CONFIG_FILE_PATH
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration

CORDISH2020PROJECTS_PACKAGE_ID = "be33a8b8-4298-4257-93bc-085d289be6d0"

DGT_TRANSLATION_PACKAGE_ID = "7de8a996-9765-47da-af80-fcb575e596ab"

TED_PACKAGE_ID = "cdd61a23-eb87-4e06-808c-ed4bd69d2247"

ECB_WEB_SERVICE_PACKAGE_ID = "74e543ee-8fae-4a14-8b24-e03e2c74f577"

CONNECT_SPARQL_ENDPOINT_ID = "866a95cf-c6ad-4624-bdb9-e53ad80255d1"

OP_VIP_DATASETS = ['b07ecd46-d298-4a51-bfb4-0c11d4625134',
                   'e33c79b9-a549-4f47-8a8c-617a1183540e',
                   'c501a114-8b53-462d-aa28-2b9ff68fa5f8',
                   'bfaeb715-171e-4050-a3ca-f27e04ebd34b',
                   '67f1306d-dade-4820-a732-f6019e5a299a',
                   '8abe51cd-4314-4d5a-8303-a6ec5d9d9f12',
                   '45a6f9bf-9819-4881-befa-f79e000e0dc6']

log = logging.getLogger(__file__)
log.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
log.addHandler(stream_handler)


class TestMigrateAllPackages(TestWithVirtuosoConfiguration):
    # def test_migrate_all_packages_to_virtuoso(self):
    #     datasets_migration_manager.migrate_all_packages_to_virtuoso(config_file_path=TEST_CONFIG_FILE_PATH)

    def test_migrate_OP_VIP_datasets(self):
        OP_VIP_DATASETS =[]
        # OP_VIP_DATASETS.append('a572e5ec-0e81-42df-9dde-aad55a50bd44')
        #OP_VIP_DATASETS.append('db715fd8-0970-48bb-a1f4-6cb2bb10b36e')
        # OP_VIP_DATASETS.append('ed21b53a-e5ff-4077-8191-a4f107ebde6f')
        # OP_VIP_DATASETS.append('b941f99a-57da-4576-a544-4b8811acc327')
        # OP_VIP_DATASETS.append('150c8ae3-9d1f-4971-b23b-2129469abbb3') ea731c1b-422b-4b3c-a399-c400302a6c8b
        #OP_VIP_DATASETS.append('309e9d59-1c9c-4c79-8394-72bfd8dc7200')
        #OP_VIP_DATASETS.append('9a2ef9a0-b50e-448d-996d-577e892148e2')
        #OP_VIP_DATASETS.append('68c15f0f-c77b-42c0-b411-16fbce223932')
        # OP_VIP_DATASETS.append('54dd2284-52e8-4131-8b9c-3eebb1d88b38')
        #OP_VIP_DATASETS.append('e62c401b-e8d8-44c7-a758-abb78c2f62e6')
        #OP_VIP_DATASETS.append('9e8c7096-553d-40ac-9a74-4f01d552d583')
        OP_VIP_DATASETS.append('f3daf58c-3ab1-4fb9-8f68-33faf3f73625')
        packages_to_migrate = []
        for dataset in OP_VIP_DATASETS:
            condition = Package.id == dataset
            package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]
            packages_to_migrate.append(package)

        controlled_vocabulary = ControlledVocabulary()
        for package in packages_to_migrate:
            datasets_migration_manager.migrate_package_to_virtuoso(config_file_path=TEST_CONFIG_FILE_PATH,
                                                                   package=package,
                                                                   controlled_vocabulary=controlled_vocabulary)



    def test_migrate_3_most_viewed_packages_to_virtuoso(self):
        packages_to_migrate = []

        condition = Package.id == TED_PACKAGE_ID
        ted_package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]
        condition = Package.id == DGT_TRANSLATION_PACKAGE_ID
        dgt_translation_package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]
        condition = Package.id == CORDISH2020PROJECTS_PACKAGE_ID
        cordisH2020projects_package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]

        packages_to_migrate.append(ted_package)
        packages_to_migrate.append(dgt_translation_package)
        packages_to_migrate.append(cordisH2020projects_package)

        controlled_vocabulary = ControlledVocabulary()

        for package in packages_to_migrate:
            datasets_migration_manager.migrate_package_to_virtuoso(config_file_path=TEST_CONFIG_FILE_PATH,
                                                                   package=package,
                                                                   controlled_vocabulary=controlled_vocabulary)

        dataset = DatasetDcatApOp(DATASET_URI_PREFIX + "ted-1")
        result = dataset.get_description_from_ts()
        assert result is True
        dataset = DatasetDcatApOp(DATASET_URI_PREFIX + "cordisH2020projects")
        result = dataset.get_description_from_ts()
        assert result is True
        dataset = DatasetDcatApOp(DATASET_URI_PREFIX + "dgt-translation-memory")
        result = dataset.get_description_from_ts()
        assert result is True

    def test_migrate_100_packages_to_virtuoso(self):
        start = time.time()

        controlled_vocabulary = ControlledVocabulary()

        packages_to_migrate = postgresql_helper.get_all_active_packages(
            TEST_CONFIG_FILE_PATH)[:100]  # type:  list[Package]

        for package in packages_to_migrate:
            datasets_migration_manager.migrate_package_to_virtuoso(config_file_path=TEST_CONFIG_FILE_PATH,
                                                                   package=package,
                                                                   controlled_vocabulary=controlled_vocabulary)

        duration = time.time() - start
        log.info(duration)

    def test_migrate_most_viewed_package_to_virtuoso(self):
        controlled_vocabulary = ControlledVocabulary()

        condition = Package.id == TED_PACKAGE_ID
        ted_package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]

        datasets_migration_manager.migrate_package_to_virtuoso(config_file_path=TEST_CONFIG_FILE_PATH,
                                                               package=ted_package,
                                                               controlled_vocabulary=controlled_vocabulary)

        dataset = DatasetDcatApOp(DATASET_URI_PREFIX + "ted-1")
        result = dataset.get_description_from_ts()
        assert result is True

    def test_migrate_dataset_in_group(self):
        condition = Package.id == ECB_WEB_SERVICE_PACKAGE_ID
        ecb_web_service_package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]

        controlled_vocabulary = ControlledVocabulary()

        datasets_migration_manager.migrate_package_to_virtuoso(config_file_path=TEST_CONFIG_FILE_PATH,
                                                               package=ecb_web_service_package,
                                                               controlled_vocabulary=controlled_vocabulary)
        dataset = DatasetDcatApOp(DATASET_URI_PREFIX + "ecb-web-service", graph_name=DCATAPOP_PRIVATE_GRAPH_NAME)
        result = dataset.get_description_from_ts()
        assert result is True

    def test_migrate_dataset_in_multiple_groups(self):
        condition = Package.id == CONNECT_SPARQL_ENDPOINT_ID
        ecb_web_service_package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]
        controlled_vocabulary = ControlledVocabulary()

        datasets_migration_manager.migrate_package_to_virtuoso(config_file_path=TEST_CONFIG_FILE_PATH,
                                                               package=ecb_web_service_package,
                                                               controlled_vocabulary=controlled_vocabulary)
        dataset = DatasetDcatApOp(DATASET_URI_PREFIX + "connect-sparql-endpoint",
                                  graph_name=DCATAPOP_PRIVATE_GRAPH_NAME)
        result = dataset.get_description_from_ts()
        assert result is True

    def test_migrate_delta(self):
        datasets_migration_manager.migrate_delta(TEST_CONFIG_FILE_PATH)
