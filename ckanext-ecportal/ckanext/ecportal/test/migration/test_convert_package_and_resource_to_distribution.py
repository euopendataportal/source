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

from datetime import date

from ckanext.ecportal.migration import database_to_ontology_converter
from ckanext.ecportal.migration.postgresql.dto.postgresql_dtos import Package, Resource
from ckanext.ecportal.migration.postgresql.helpers.postgresql_helper import find_any_in_database
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp, DCATAPOP_PUBLIC_GRAPH_NAME, \
    DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.test.configuration.configuration_constants import TEST_CONFIG_FILE_PATH
from ckanext.ecportal.test.migration.controlled_vocabulary import ControlledVocabulary
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration


class TestConvertPackageAndResourceToDistribution(TestWithVirtuosoConfiguration):
    def test_convert_package_and_resource_to_distribution(self):
        package = Package()
        package.license_id = 'http://data.europa.eu/euodp/kos/licence/EuropeanCommission'

        resource = Resource()
        resource.resource_type = 'http://data.europa.eu/euodp/kos/documentation-type/MainDocumentation'
        resource.description = 'Download dataset in TSV format'
        resource.format = 'application/x-gzip'
        resource.created = '2017-06-20 08:24:55'
        resource.name = 'ESMS metadata (Euro-SDMX Metadata structure) SDMX'
        resource.last_modified = ''
        controlled_vocabulary = ControlledVocabulary()
        database_to_ontology_converter.convert_resource_to_distribution(
            TEST_CONFIG_FILE_PATH,
            resource=resource,
            file_types=controlled_vocabulary.controlled_file_types,
            status=controlled_vocabulary.controlled_status.itervalues().next,
            distribution_types=controlled_vocabulary.controlled_distribution_types)

    # Unit test to verify migration will be done correctly.
    # Use the database directly to assure migrated data are coherent
    def test_convert_package_to_dataset(self):
        condition = Package.id == "cdd61a23-eb87-4e06-808c-ed4bd69d2247"
        package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]

        controlled_vocabulary = ControlledVocabulary()

        dataset = database_to_ontology_converter. \
            convert_package_to_dataset(package, controlled_vocabulary, TEST_CONFIG_FILE_PATH)  # type:  DatasetDcatApOp

        assert dataset is not None
        assert dataset.schema is not None
        assert dataset.schema_catalog_record is not None
        assert dataset.schema.graph_name is DCATAPOP_PUBLIC_GRAPH_NAME

        dataset.save_to_ts()

    def test_convert_package_private_to_dataset(self):
        condition = Package.id == "cdd61a23-eb87-4e06-808c-ed4bd69d2247"
        package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]
        package.private = True

        controlled_vocabulary = ControlledVocabulary()

        dataset = database_to_ontology_converter. \
            convert_package_to_dataset(package, controlled_vocabulary, TEST_CONFIG_FILE_PATH)  # type:  DatasetDcatApOp

        assert dataset is not None
        assert dataset.schema is not None
        assert dataset.schema.graph_name is DCATAPOP_PRIVATE_GRAPH_NAME

        dataset.save_to_ts()

    def test_get_description(self):
        dataset = DatasetDcatApOp("http://data.europa.eu/euodp/en/data/dataset/S2121_86_3_453_ENG")
        r = dataset.get_description_from_ts()

    def test_big_dataset(self):
        condition = Package.id == "ad49841e-b4f1-4efc-8b1c-f100364f1563"
        package = find_any_in_database(TEST_CONFIG_FILE_PATH, condition, Package)[0]

        controlled_vocabulary = ControlledVocabulary()

        dataset = database_to_ontology_converter. \
            convert_package_to_dataset(package, controlled_vocabulary, TEST_CONFIG_FILE_PATH)  # type:  DatasetDcatApOp

        assert dataset is not None
        assert dataset.schema is not None
        assert dataset.schema_catalog_record is not None
        assert dataset.schema.graph_name is DCATAPOP_PUBLIC_GRAPH_NAME

        dataset.save_to_ts()


def create_package(self):
    # Manual creation of a package
    package = Package()
    package.creator_user_id = u'75d0190a-2f12-40ed-a863-b5bf30990d14'
    package.id = u'cdd61a23-eb87-4e06-808c-ed4bd69d2247'
    package.license_id = u'http://data.europa.eu/euodp/kos/licence/EuropeanCommission'
    package.metadata_modified = date.today()
    package.name = u'ted-1'
    package.notes = u'The European Union together with its Member States is the world\'s largest'
    package.owner_org = u'dbda9968-cb1e-47c3-b115-245a057e4d4a'
    package.private = False
    package.revision_id = u'9f663b6c-3467-4c33-baa1-f2e65dbe5cf1'
    package.state = u'active'
    package.title = u'Special Eurobarometer 453: Humanitarian aid'
    package.type = u'dataset'
    package.url = u'http://ted.europa.eu/TED/main/HomePage.do'
    package.version = u'v1.00'
