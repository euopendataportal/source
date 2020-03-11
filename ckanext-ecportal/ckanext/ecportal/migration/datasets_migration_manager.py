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
import os
import ConfigParser

import ujson as json
import ckanext.ecportal.action.ecportal_validation as validation

from ckan.common import _

import ckan.lib.i18n as i18n
from pylons import config
from ckanext.ecportal.migration.error.migration_error import MigrationError
from ckanext.ecportal.migration.migration_constants import DATASET, DATASET_URI_PREFIX
from ckanext.ecportal.migration.postgresql.dto.postgresql_dtos import Package
from ckanext.ecportal.migration.postgresql.helpers import postgresql_helper
from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
from ckanext.ecportal.test.migration.controlled_vocabulary import ControlledVocabulary
from ckanext.ecportal.virtuoso.predicates_constants import TYPE_PREDICATE
from ckanext.ecportal.virtuoso.triplet import Triplet
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers, SUBJECT_WITH_SPACES
from ckanext.ecportal.model.schema_wrapper_interface import ISchemaWrapper

log = logging.getLogger("paster")



def migrate_all_packages_to_virtuoso(config_file_path):
    packages = postgresql_helper.get_all_active_packages(config_file_path)  # type:  list[Package]
    migrate_packages_to_virtuoso(config_file_path, packages)

def migrate_OP_VIP_datasets(test_config_file):
    packages_to_migrate = []
    OP_VIP_DATASETS = ['b07ecd46-d298-4a51-bfb4-0c11d4625134',
                        'e33c79b9-a549-4f47-8a8c-617a1183540e',
                        'c501a114-8b53-462d-aa28-2b9ff68fa5f8',
                        'bfaeb715-171e-4050-a3ca-f27e04ebd34b',
                        '67f1306d-dade-4820-a732-f6019e5a299a',
                        '8abe51cd-4314-4d5a-8303-a6ec5d9d9f12',
                        '45a6f9bf-9819-4881-befa-f79e000e0dc6']
    OP_VIP_DATASETS =[]
    # OP_VIP_DATASETS.append('a572e5ec-0e81-42df-9dde-aad55a50bd44')
    #OP_VIP_DATASETS.append('db715fd8-0970-48bb-a1f4-6cb2bb10b36e')
    # OP_VIP_DATASETS.append('ed21b53a-e5ff-4077-8191-a4f107ebde6f')
    # OP_VIP_DATASETS.append('b941f99a-57da-4576-a544-4b8811acc327')
    # OP_VIP_DATASETS.append('150c8ae3-9d1f-4971-b23b-2129469abbb3')
    #OP_VIP_DATASETS.append('309e9d59-1c9c-4c79-8394-72bfd8dc7200')
    #OP_VIP_DATASETS.append('9a2ef9a0-b50e-448d-996d-577e892148e2')
    #OP_VIP_DATASETS.append('68c15f0f-c77b-42c0-b411-16fbce223932')
    # OP_VIP_DATASETS.append('54dd2284-52e8-4131-8b9c-3eebb1d88b38')
    #OP_VIP_DATASETS.append('e62c401b-e8d8-44c7-a758-abb78c2f62e6')
    #OP_VIP_DATASETS.append('9e8c7096-553d-40ac-9a74-4f01d552d583')
    #OP_VIP_DATASETS.append('f3daf58c-3ab1-4fb9-8f68-33faf3f73625')
    #OP_VIP_DATASETS.append('ea731c1b-422b-4b3c-a399-c400302a6c8b')
    #OP_VIP_DATASETS.append('b7c7c8d3-bb3b-49d8-80ad-20d04d1200c4')
    #OP_VIP_DATASETS.append('7de8a996-9765-47da-af80-fcb575e596ab')
    #OP_VIP_DATASETS.append('7fe111d2-635a-4017-9c5d-8dd9dfe163b2') #Test DB!
    OP_VIP_DATASETS.append('9a2e72ab-e470-4c8e-80f7-8da2607d4125') #PZ DB!

    from ckanext.ecportal.migration.postgresql.helpers.postgresql_helper import find_any_in_database
    for dataset in OP_VIP_DATASETS:
        condition = Package.id == dataset
        package = find_any_in_database(test_config_file, condition, Package)[0]
        packages_to_migrate.append(package)

    controlled_vocabulary = ControlledVocabulary()
    for package in packages_to_migrate:
        migrate_package_to_virtuoso(config_file_path=test_config_file,
                                                               package=package,
                                                               controlled_vocabulary=controlled_vocabulary)


def migrate_with_package_name_to_virtuoso(config_file_path, package_name):
    condition = Package.name == package_name
    package = postgresql_helper.find_any_in_database(config_file_path, condition, Package)  # type: list[Package]
    migrate_packages_to_virtuoso(config_file_path, package)


def migrate_packages_to_virtuoso(config_file_path, packages):
    controlled_vocabulary = ControlledVocabulary()

    #create_odp_default_catalogue()

    count = 0
    for package in packages:
        try:
            migrate_package_to_virtuoso(config_file_path, package, controlled_vocabulary)
            count += 1
            log.info('Migrated {0} of {1}: {2}'.format(count, len(packages), package.name))
        except Exception as e:
            import traceback
            log.error('Migrated failed for {0}'.format(package.name))
            log.error(e.message)
            log.error(traceback.print_exc())


def migrate_package_to_virtuoso(config_file_path, package, controlled_vocabulary):
    import ckanext.ecportal.migration.database_to_ontology_converter as database_to_ontology_converter
    try:
        dataset = database_to_ontology_converter.convert_package_to_dataset(package, controlled_vocabulary,
                                                                            config_file_path)  # type: DatasetDcatApOp
    except BaseException as e:
        import traceback
        log.error(traceback.print_exc())
        raise MigrationError(message="error migrating dataset [{0}]".format(package.name))

    if dataset:
        #is_saved = dataset.save_to_ts()
        val_dataset, error = validation.validate_dacat_dataset(dataset)

        if error.get('fatal',None) or error.get('error',None):
            directory = '/home/ecodp/migration_errors'
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open('/home/ecodp/migration_errors/{0}'.format(dataset.dataset_uri.split('/')[-1]), 'w') as file:
                file.write(json.dumps(error))


        if dataset.privacy_state == 'public':
            write_to_public_graph(dataset)
        else:
            write_to_private_graph(dataset)



def migrate_delta(configuration_file_path):
    triplet_list = [Triplet(predicate=TYPE_PREDICATE, object=NAMESPACE_DCATAPOP.dcat + DATASET)]

    properties_values = TripleStoreCRUDHelpers().find_any_in_graphs_for_where_clauses([DCATAPOP_PUBLIC_GRAPH_NAME,
                                                                                       DCATAPOP_PRIVATE_GRAPH_NAME],
                                                                                      triplet_list,
                                                                                      result_clause=SUBJECT_WITH_SPACES)
    # Transform to only get a list of uri
    migrated_datasets = []
    for properties_value in properties_values:
        migrated_datasets.append(properties_value.get("s").get("value").split('/')[-1])

    condition = Package.state == "active"
    all_packages = postgresql_helper.find_any_in_database(config_file_path=configuration_file_path,
                                                          condition=condition, table=Package,
                                                          result_clause=[Package.name])
    # Transform to only get a list of uri
    all_packages_list = []
    for package in all_packages:
        all_packages_list.append(package.name)

    not_migrated_datasets_names = set(all_packages_list) - set(migrated_datasets)
    for not_migrated_dataset_name in not_migrated_datasets_names:
        dataset = DatasetDcatApOp(DATASET_URI_PREFIX + not_migrated_dataset_name)
        DatasetDcatApOp.delete_from_ts(dataset)
        migrate_with_package_name_to_virtuoso(configuration_file_path, not_migrated_dataset_name)

    return migrated_datasets




def create_odp_default_catalogue():

    cat = CatalogDcatApOp('')



    write_to_public_graph(cat)


def write_to_public_graph(schema_wrapper):
    '''

    :param ISchemaWrapper schema_wrapper:
    :return:
    '''
    with open('/home/ecodp/dcatapop_public.nt', 'a') as file:
                file.write(schema_wrapper.build_the_graph().serialize(format="nt"))



def write_to_private_graph(schema_wrapper):
    '''

    :param ISchemaWrapper schema_wrapper:
    :return:
    '''
    with open('/home/ecodp/dcatapop_private.nt', 'a') as file:
                file.write(schema_wrapper.build_the_graph().serialize(format="nt"))

