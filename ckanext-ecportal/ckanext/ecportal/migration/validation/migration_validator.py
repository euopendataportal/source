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
import dateutil

from operator import and_

from ckanext.ecportal.migration.error.migration_error import MigrationError
from ckanext.ecportal.migration.migration_constants import DATASET_URI_PREFIX, EUROVOC_DOMAIN, TEMPORAL_COVERAGE_FROM, \
    VOC_CONCEPTS_EUROVOC, ALTERNATIVE_TITLE
from ckanext.ecportal.migration.postgresql.dto.postgresql_dtos import Package, Tag, PackageTag, Member, Group, \
    PackageExtra
from ckanext.ecportal.migration.postgresql.helpers import postgresql_helper
from ckanext.ecportal.migration.postgresql.helpers.postgresql_helper import ACTIVE_STATE
from ckanext.ecportal.migration.validation import virtuoso_migration_validation_query_constants, \
    postgres_migration_validation_query_constants
from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
from ckanext.ecportal.model.schemas.dcatapop_dataset_schema import DatasetSchemaDcatApOp
from ckanext.ecportal.virtuoso.triplet import Triplet
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers, SUBJECT_WITH_SPACES, \
    SUBJECT, OBJECT, VIRTUOSO_SUBJECT_RETURN, VIRTUOSO_VALUE_KEY, VIRTUOSO_OBJECT_RETURN

from ckanext.ecportal.model.utils_convertor import EUROVOC_DOMAINS_MAPPING

log = logging.getLogger("paster")


def validate_migration(config_file_path=""):
    log.info('****************************')
    log.info('*START MIGRATION VALIDATING*')
    log.info('****************************')
    result = True

    triple_store_helper = TripleStoreCRUDHelpers()


    try:
        validate_number_datasets(config_file_path, triple_store_helper)
        log.info('Validate number of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False
    try:
        validate_number_datasets_per_publisher(config_file_path, triple_store_helper)
        log.info('Validate number of migrated datasets per publisher successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False
    try:
        validate_number_resources_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of migrated distributions per dataset successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False
    try:
        validate_number_documents_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of migrated documents successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False
    try:
        validate_number_datasets_eurovoc_domain(config_file_path, triple_store_helper)
        log.info('Validate number of dataset per eurovoc_domains successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False
    try:
        validate_datasets_per_group(config_file_path, triple_store_helper)
        log.info('Validate number of migrated groups per dataset successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False
    try:
        validate_eurovoc_concepts_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of migrated eurovoc_concepts per dataset successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_eurovoc_domains_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of migrated eurovoc_domains per dataset successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_keywords_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of migrated keywords per dataset successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_number_contact_point_elements_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of migrated contactpoint elements per dataset successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_number_names_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of names of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_number_main_titles_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of titles of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_translated_titles_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of title translations of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_descriptions_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of descriptions of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_translated_descriptions_per_dataset(config_file_path, triple_store_helper)
        log.info('Validate number of description translations of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_simple_dataset_field(config_file_path, DatasetSchemaDcatApOp, "", "name", "ckanName_dcatapop")
        log.info('Validate ckanName_dcatapop value of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_title_dcterms(config_file_path, DatasetSchemaDcatApOp, "", "title", "title_dcterms")
        log.info('Validate title_dcterms values of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_description_dcterms(config_file_path, DatasetSchemaDcatApOp, "", "notes", "description_dcterms")
        log.info('Validate description_dcterms values of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_simple_dataset_field(config_file_path, DatasetSchemaDcatApOp, "", "metadata_modified", "modified_dcterms")
        log.info('Validate modified_dcterms value of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_simple_dataset_field(config_file_path, DatasetSchemaDcatApOp, "", "url", "landingPage_dcat",
                                      "url_schema")
        log.info('Validate landingPage_dcat value of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_keywords(config_file_path)
        log.info('Validate keywords of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_themes(config_file_path)
        log.info('Validate themes of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_temporal_coverages(config_file_path)
        log.info('Validate temporal_coverages of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_subjects(config_file_path)
        log.info('Validate subject of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False

    try:
        validate_alternative_titles(config_file_path)
        log.info('Validate alternative titles of migrated datasets successfull')
    except MigrationError as e:
        log.error(e)
        result = False
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
        result = False




    log.info('****************************')
    log.info('*END MIGRATION VALIDATING*')
    log.info('****************************')

    return result



# def validate_alternative_titles(config_file_path):
#     condition = \
#         and_(
#             and_(
#                 Package.id == PackageExtra.package_id, PackageExtra.key == ALTERNATIVE_TITLE),
#             Package.state == ACTIVE_STATE
#         )
#     package_alternative_title_postgres_dict = {}
#     result = postgresql_helper.find_any_in_tables_database(config_file_path, condition, [], [Package.name, Tag.name])
#     for element in result:
#         package_name = DATASET_URI_PREFIX + element[0]
#         alternative_title = element[1]
#         package_alternative_title_postgres_dict[package_name] = alternative_title
#     package_alternative_title_virtuoso_dict = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "",
#                                                                                    "alternative_dcterms")
#     intersection = _filter_dicts(package_alternative_title_postgres_dict, package_alternative_title_virtuoso_dict)
#     if len(intersection) > 0:
#         for element in intersection:
#             log.warn(u'validate_alternative_titles {0}'.format(element))
#         raise MigrationError(
#             u"Not the same alternative_titles for datasets: differences between virtuoso and postgres : [{0}]".format(
#                 intersection))


def validate_alternative_titles(config_file_path):

    package_alternative_title_postgres_dict = {}
    result = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.DATASET_ALTERNATIVE_TITLES,
        config_file_path)
    for element in result:
        package_name = DATASET_URI_PREFIX + element[0]
        alternative_title = element[1]
        if package_alternative_title_postgres_dict.get(package_name):
            package_alternative_title_postgres_dict[package_name].add(alternative_title)
        else:
            package_alternative_title_postgres_dict[package_name] = set([alternative_title])
    package_alternative_title_virtuoso_dict = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "",
                                                                                   "alternative_dcterms")
    intersection = _filter_dicts(package_alternative_title_postgres_dict, package_alternative_title_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_alternative_titles {0}'.format(element))
        raise MigrationError(message=
            u"Not the same alternative_titles for datasets: differences between virtuoso and postgres : [{0}]".format(
                len(intersection)))


def validate_temporal_coverages(config_file_path):
    condition = \
        and_(
            and_(
                Package.id == PackageExtra.package_id, PackageExtra.key == TEMPORAL_COVERAGE_FROM),
            Package.state == ACTIVE_STATE
        )
    package_temporal_converage_postgres_dict = {}
    result = postgresql_helper.find_any_in_tables_database(config_file_path, condition, [],
                                                           [Package.name, PackageExtra.value], [Package.name])
    for element in result:
        package_name = DATASET_URI_PREFIX + element[0]
        only_year_temporal_coverage = element[1].split('-')[0]
        if package_temporal_converage_postgres_dict.get(package_name):
            package_temporal_converage_postgres_dict[package_name].add(only_year_temporal_coverage)
        else:
             package_temporal_converage_postgres_dict[package_name] = set([only_year_temporal_coverage])

    package_temporal_converage_virtuoso_dict = {}
    virtuoso_result = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "temporal_dcterms",
                                                           "startDate_schema")
    for package_name, temporal_coverage in virtuoso_result.items():
        only_year_temporal_coverage = next(iter(temporal_coverage)).split('-')[0]
        package_temporal_converage_virtuoso_dict[package_name] = set([only_year_temporal_coverage])


    intersection = _filter_sets(package_temporal_converage_postgres_dict, package_temporal_converage_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_temporal_coverages {0}'.format(element))
        raise MigrationError(message=
            u"Not the same temporal converage for datasets: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_keywords(config_file_path):
    condition = \
        and_(
            and_(
                and_(Package.id == PackageTag.package_id, Tag.vocabulary_id == None),
                PackageTag.state == ACTIVE_STATE),
            PackageTag.tag_id == Tag.id
        )
    package_keyword_postgres_dict = {}
    result = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.DATASET_TAGS_WITH_TRANSLATIONS,
        config_file_path)

    for element in result:
        package_name = DATASET_URI_PREFIX + element[0]
        keyword = element[1]
        if package_keyword_postgres_dict.get(package_name):
            package_keyword_postgres_dict[package_name].add(keyword)
            if element[2]:
                package_keyword_postgres_dict[package_name].add(element[2])
        else:
            package_keyword_postgres_dict[package_name] = set([keyword])
            if element[2]:
                package_keyword_postgres_dict[package_name].add(element[2])

    package_keyword_virtuoso_dict = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "keyword_dcat")
    intersection = _filter_sets(package_keyword_postgres_dict, package_keyword_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_keywords {0}'.format(element))
        raise MigrationError(message=
            u"Not the same keywords for datasets: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_subjects(config_file_path):
    condition = \
        and_( and_(
            and_(
                and_(Package.id == PackageTag.package_id, Tag.vocabulary_id == VOC_CONCEPTS_EUROVOC),
                PackageTag.state == ACTIVE_STATE),
            PackageTag.tag_id == Tag.id
        ), Package.state == 'active')
    package_subject_postgres_dict = {}
    result = postgresql_helper.find_any_in_tables_database(config_file_path, condition, [], [Package.name, Tag.name])

    for element in result:
        package_name = DATASET_URI_PREFIX + element[0]
        subject = element[1]
        if package_name in package_subject_postgres_dict.keys():
            package_subject_postgres_dict[package_name].add(subject)
        else:
            package_subject_postgres_dict[package_name] = set([subject])

    package_subject_virtuoso_dict = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "subject_dcterms")

    intersection = _filter_sets(package_subject_postgres_dict, package_subject_virtuoso_dict)

    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_subjects {0}'.format(element))
        raise MigrationError(message=
            u"Not the same subjects for datasets: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_themes(config_file_path):
    condition = \
        and_(
            and_(
                and_(
                    and_(
                        and_(
                            and_(
                                Package.id == Member.table_id, Member.table_name == 'package'),
                            Group.type == EUROVOC_DOMAIN),
                        Member.state == ACTIVE_STATE),
                    Group.state == ACTIVE_STATE),
                Package.state == ACTIVE_STATE),
            Member.group_id == Group.id
        )
    package_theme_postgres_dict = {}
    result = postgresql_helper.find_any_in_tables_database(config_file_path, condition, [],
                                                           [Package.name, Group.name])
    for element in result:
        package_name = DATASET_URI_PREFIX + element[0]
        theme = u'http://eurovoc.europa.eu/{0}'.format(element[1].split('_')[-1])
        if package_theme_postgres_dict.get(package_name):
            package_theme_postgres_dict[package_name].add(theme)
        else:
            package_theme_postgres_dict[package_name] = set([theme])

    package_keyword_virtuoso_dict = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "theme_dcat")
    #???
    intersection = _filter_sets(package_theme_postgres_dict, package_keyword_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_themes {0}'.format(element))
        raise MigrationError(message=
            u"Not the same themes for datasets: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_translated_descriptions_per_dataset(config_file_path, triple_store_helper):
    descriptions_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_TRANSLATED_DESCRIPTIONS_PER_DATASET)
    descriptions_per_dataset_virtuoso_dict = {}
    for descriptions_for_one_dataset in descriptions_per_dataset_virtuoso:
        dataset_name = descriptions_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(descriptions_for_one_dataset['number_descriptions']['value'])
        descriptions_per_dataset_virtuoso_dict[dataset_name] = count

    descriptions_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_TRANSLATED_DESCRIPTIONS_PER_DATASET,
        config_file_path)
    descriptions_per_dataset_postgres_dict = {}
    for descriptions_for_one_dataset in descriptions_per_dataset_postgres:
        dataset_name = descriptions_for_one_dataset[0]
        count = descriptions_for_one_dataset[1]
        descriptions_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(descriptions_per_dataset_postgres_dict, descriptions_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_translated_descriptions_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of translated descriptions per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_descriptions_per_dataset(config_file_path, triple_store_helper):
    descriptions_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_MAIN_DESCRIPTIONS_PER_DATASET)
    descriptions_per_dataset_virtuoso_dict = {}
    for descriptions_for_one_dataset in descriptions_per_dataset_virtuoso:
        dataset_name = descriptions_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(descriptions_for_one_dataset['number_descriptions']['value'])
        descriptions_per_dataset_virtuoso_dict[dataset_name] = count

    descriptions_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_MAIN_DESCRIPTIONS_PER_DATASET,
        config_file_path)
    descriptions_per_dataset_postgres_dict = {}
    for descriptions_for_one_dataset in descriptions_per_dataset_postgres:
        dataset_name = descriptions_for_one_dataset[0]
        count = descriptions_for_one_dataset[1]
        descriptions_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(descriptions_per_dataset_postgres_dict, descriptions_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_descriptions_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of main descriptions per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_translated_titles_per_dataset(config_file_path, triple_store_helper):
    titles_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_TRANSLATED_TITLES_PER_DATASET)
    titles_per_dataset_virtuoso_dict = {}
    for titles_for_one_dataset in titles_per_dataset_virtuoso:
        dataset_name = titles_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(titles_for_one_dataset['number_titles']['value'])
        titles_per_dataset_virtuoso_dict[dataset_name] = count

    titles_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_TRANSLATED_TITLES_PER_DATASET,
        config_file_path)
    titles_per_dataset_postgres_dict = {}
    for titles_for_one_dataset in titles_per_dataset_postgres:
        dataset_name = titles_for_one_dataset[0]
        count = titles_for_one_dataset[1]
        titles_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(titles_per_dataset_postgres_dict, titles_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_translated_titles_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of translated titles per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_number_main_titles_per_dataset(config_file_path, triple_store_helper):
    titles_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_MAIN_TITLES_PER_DATASET)
    titles_per_dataset_virtuoso_dict = {}
    for titles_for_one_dataset in titles_per_dataset_virtuoso:
        dataset_name = titles_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(titles_for_one_dataset['number_titles']['value'])
        titles_per_dataset_virtuoso_dict[dataset_name] = count

    titles_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_MAIN_TITLES_PER_DATASET,
        config_file_path)
    titles_per_dataset_postgres_dict = {}
    for titles_for_one_dataset in titles_per_dataset_postgres:
        dataset_name = titles_for_one_dataset[0]
        count = titles_for_one_dataset[1]
        titles_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(titles_per_dataset_postgres_dict, titles_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_number_main_titles_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of titles per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_number_names_per_dataset(config_file_path, triple_store_helper):
    names_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_NAMES_PER_DATASET)
    names_per_dataset_virtuoso_dict = {}
    for names_for_one_dataset in names_per_dataset_virtuoso:
        dataset_name = names_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(names_for_one_dataset['number_names']['value'])
        names_per_dataset_virtuoso_dict[dataset_name] = count

    names_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_NAMES_PER_DATASET, config_file_path)
    names_per_dataset_postgres_dict = {}
    for names_for_one_dataset in names_per_dataset_postgres:
        dataset_name = names_for_one_dataset[0]
        count = names_for_one_dataset[1]
        names_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(names_per_dataset_postgres_dict, names_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_number_names_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of names per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_number_contact_point_elements_per_dataset(config_file_path, triple_store_helper):
    contact_point_elements_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_CONTACT_POINT_ELEMENTS_PER_DATASET)
    contact_point_elements_per_dataset_virtuoso_dict = {}
    for contact_point_elements_for_one_dataset in contact_point_elements_per_dataset_virtuoso:
        dataset_name = contact_point_elements_for_one_dataset['dataset']['value'].split("/")[-1]
        count = long(contact_point_elements_for_one_dataset['number_contact_elements']['value'])
        contact_point_elements_per_dataset_virtuoso_dict[dataset_name] = count

    contact_point_elements_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_CONTACT_POINT_ELEMENTS_PER_DATASET, config_file_path)
    contact_point_elements_per_dataset_postgres_dict = {}
    for contact_point_elements_for_one_dataset in contact_point_elements_per_dataset_postgres:
        dataset_name = contact_point_elements_for_one_dataset[0]
        count = contact_point_elements_for_one_dataset[1]
        contact_point_elements_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(contact_point_elements_per_dataset_postgres_dict, contact_point_elements_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_number_contact_point_elements_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of contact point elements per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_keywords_per_dataset(config_file_path, triple_store_helper):
    keywords_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_KEYWORDS_PER_DATASET)
    keywords_per_dataset_virtuoso_dict = {}
    for keywords_for_one_dataset in keywords_per_dataset_virtuoso:
        dataset_name = keywords_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(keywords_for_one_dataset['number_keywords']['value'])
        keywords_per_dataset_virtuoso_dict[dataset_name] = count

    keywords_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_KEYWORDS_PER_DATASET, config_file_path)
    keywords_per_dataset_postgres_dict = {}
    for keywords_for_one_dataset in keywords_per_dataset_postgres:
        dataset_name = keywords_for_one_dataset[0]
        count = keywords_for_one_dataset[1]
        keywords_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(keywords_per_dataset_postgres_dict, keywords_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_keywords_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of keywords per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_eurovoc_domains_per_dataset(config_file_path, triple_store_helper):
    eurovoc_domains_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_EUROVOC_DOMAINS_PER_DATASET)
    eurovoc_domains_per_dataset_virtuoso_dict = {}
    for eurovoc_domain_for_one_dataset in eurovoc_domains_per_dataset_virtuoso:
        dataset_name = eurovoc_domain_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(eurovoc_domain_for_one_dataset['number_eurovoc_domains']['value'])
        eurovoc_domains_per_dataset_virtuoso_dict[dataset_name] = count


    mapping_validation = {}
    for domain, mapped_themes in EUROVOC_DOMAINS_MAPPING.items():

        for theme in mapped_themes:
            tmp_domains = mapping_validation.get(theme, [])
            tmp_domains.append(domain)
            mapping_validation[theme] = tmp_domains

    report = ''
    #compare theme by theme with list of domains to sum

    eurovoc_domains_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_EUROVOC_DOMAINS_PER_DATASET, config_file_path)
    eurovoc_domains_per_dataset_postgres_dict = {}
    for eurovoc_domains_for_one_dataset in eurovoc_domains_per_dataset_postgres:
        dataset_name = eurovoc_domains_for_one_dataset[0]
        count = eurovoc_domains_for_one_dataset[1]
        eurovoc_domains_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(eurovoc_domains_per_dataset_postgres_dict, eurovoc_domains_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_eurovoc_domains_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of eurovoc domains per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_eurovoc_concepts_per_dataset(config_file_path, triple_store_helper):
    eurovoc_concept_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_EUROVOC_CONCEPT_PER_DATASET)
    eurovoc_concept_per_dataset_virtuoso_dict = {}
    for eurovoc_concept_for_one_dataset in eurovoc_concept_per_dataset_virtuoso:
        dataset_name = eurovoc_concept_for_one_dataset['uri']['value'].split("/")[-1]
        count = long(eurovoc_concept_for_one_dataset['number_eurovoc_concepts']['value'])
        eurovoc_concept_per_dataset_virtuoso_dict[dataset_name] = count

    eurovoc_concept_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_EUROVOC_CONCEPT_PER_DATASET, config_file_path)

    eurovoc_concept_per_dataset_postgres_dict = {}
    for eurovoc_concept_for_one_dataset in eurovoc_concept_per_dataset_postgres:
        dataset_name = eurovoc_concept_for_one_dataset[0]
        count = eurovoc_concept_for_one_dataset[1]
        eurovoc_concept_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(eurovoc_concept_per_dataset_postgres_dict, eurovoc_concept_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_eurovoc_concepts_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of eurovoc concept per dataset: differences between virtuoso and postgres : [{0}]".
                format( len(intersection)))


def validate_datasets_per_group(config_file_path, triple_store_helper):
    datasets_per_group_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_DATASETS_PER_GROUP)
    datasets_per_group_virtuoso_dict = {}
    for datasets_for_one_group in datasets_per_group_virtuoso:
        group = datasets_for_one_group['group']['value'].split("/")[-1]
        count = long(datasets_for_one_group['number_datasets']['value'])
        datasets_per_group_virtuoso_dict[group] = count

    datasets_per_group_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_DATASETS_PER_GROUP,
        config_file_path)
    datasets_per_group_postgres_dict = {}
    for datasets_for_one_group in datasets_per_group_postgres:
        group = datasets_for_one_group[0]
        count = datasets_for_one_group[1]
        datasets_per_group_postgres_dict[group] = count

        # intersection = set(datasets_per_group_postgres_dict.items()) - set(datasets_per_group_virtuoso_dict.items())
        # if len(intersection) > 0:
        #     raise MigrationError(
        #         "Not the same number of datasets per group: differences between virtuoso and postgres : [{0}]".format(
        #             intersection))


def validate_number_datasets_eurovoc_domain(config_file_path, triple_store_helper):
    datasets_per_eurovoc_domain_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_DATASETS_PER_EUROVOC_DOMAIN)
    datasets_per_eurovoc_domain_virtuoso_dict = {}
    for datasets_for_one_eurovoc_domain in datasets_per_eurovoc_domain_virtuoso:
        eurovoc_domain = datasets_for_one_eurovoc_domain['eurovoc_domain']['value']
        count = long(datasets_for_one_eurovoc_domain['number_datasets']['value'])
        datasets_per_eurovoc_domain_virtuoso_dict[eurovoc_domain] = count

    mapping_validation = {}
    for domain, mapped_themes in EUROVOC_DOMAINS_MAPPING.items():

        for theme in mapped_themes:
            tmp_domains = mapping_validation.get(theme, [])
            tmp_domains.append(domain)
            mapping_validation[theme] = tmp_domains

    report = ''
    #compare theme by theme with list of domains to sum
    for theme, count in datasets_per_eurovoc_domain_virtuoso_dict.items():
        domains_list = mapping_validation.get(theme,'')

        datasets_per_eurovoc_domain_postgres = postgresql_helper.execute_query_with_param(
            postgres_migration_validation_query_constants.NUMBER_DATASETS_PER_EUROVOC_DOMAIN,
            config_file_path, domains_list)

        if datasets_per_eurovoc_domain_postgres != count:
            report += u"Not the same number of datasets per theme {0}: differences between virtuoso and postgres : [{1}] \n".format(theme, count - datasets_for_one_eurovoc_domain[0])

    if report:
        raise MigrationError(message=report)


def validate_number_documents_per_dataset(config_file_path, triple_store_helper):
    documents_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_DOCUMENTS_PER_DATASET)
    documents_per_dataset_virtuoso_dict = {}
    for documents_for_one_dataset in documents_per_dataset_virtuoso:
        dataset_name = documents_for_one_dataset['uri']['value'].split('/')[-1]
        count = long(documents_for_one_dataset['number_documents']['value'])
        documents_per_dataset_virtuoso_dict[dataset_name] = count

    documents_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_DOCUMENTS_PER_DATASET,
        config_file_path)
    documents_per_dataset_postgres_dict = {}
    for documents_for_one_dataset in documents_per_dataset_postgres:
        dataset_name = documents_for_one_dataset[0]
        count = documents_for_one_dataset[1]
        documents_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(documents_per_dataset_postgres_dict, documents_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_number_documents_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of documents per dataset: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_number_resources_per_dataset(config_file_path, triple_store_helper):
    resources_per_dataset_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_RESOURCES_PER_DATASET)
    resources_per_dataset_virtuoso_dict = {}
    for resources_for_one_dataset in resources_per_dataset_virtuoso:
        dataset_name = resources_for_one_dataset['uri']['value'].split('/')[-1]
        count = long(resources_for_one_dataset['number_resources']['value'])
        resources_per_dataset_virtuoso_dict[dataset_name] = count

    resources_per_dataset_postgres = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_RESOURCES_PER_DATASET,
        config_file_path)
    resources_per_dataset_postgres_dict = {}
    for resources_for_one_dataset in resources_per_dataset_postgres:
        dataset_name = resources_for_one_dataset[0]
        count = resources_for_one_dataset[1]
        resources_per_dataset_postgres_dict[dataset_name] = count

    intersection = _filter_dicts(resources_per_dataset_postgres_dict, resources_per_dataset_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_number_resources_per_dataset {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of distributions per dataset: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_number_datasets_per_publisher(config_file_path, triple_store_helper):
    datasets_per_publisher_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.NUMBER_DATASETS_PER_PUBLISHER)
    datasets_per_publisher_virtuoso_dict = {}
    for datasets_for_one_publisher in datasets_per_publisher_virtuoso:
        publisher = datasets_for_one_publisher['pub']['value'].split("/")[-1].upper()
        count = long(datasets_for_one_publisher['count']['value'])
        datasets_per_publisher_virtuoso_dict[publisher] = count

    datasets_per_publisher_postgresql = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.NUMBER_DATASETS_PER_PUBLISHER,
        config_file_path)
    datasets_per_publisher_postgres_dict = {}
    for datasets_for_one_publisher in datasets_per_publisher_postgresql:
        publisher = datasets_for_one_publisher[0].upper()
        count = datasets_for_one_publisher[1]
        datasets_per_publisher_postgres_dict[publisher] = count

    intersection = _filter_dicts(datasets_per_publisher_postgres_dict, datasets_per_publisher_virtuoso_dict)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_number_datasets_per_publisher {0}'.format(element))
        raise MigrationError(message=
            u"Not the same number of datasets per publisher: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_number_datasets(config_file_path, triple_store_helper):
    number_datasets_per_graph_virtuoso = triple_store_helper.execute_select_query_auth(
        virtuoso_migration_validation_query_constants.COUNT_ALL_DATASETS_QUERY)

    number_datasets_per_graph_postgresql = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.COUNT_ALL_DATASETS_QUERY,
        config_file_path)

    if number_datasets_per_graph_virtuoso is None:
        raise MigrationError(message="No dataset in virtuoso")
    if number_datasets_per_graph_postgresql is None:
        raise MigrationError(message="No dataset in postgresql")
    number_datasets_private_graph_virtuoso = long(
        number_datasets_per_graph_virtuoso[0]['number_private_datasets']['value'])
    number_datasets_private_graph_postgres = number_datasets_per_graph_postgresql[1][1]
    if number_datasets_private_graph_virtuoso != number_datasets_private_graph_postgres:
        raise MigrationError(message=
            u"Number of private datasets in virtuoso : [{0}] does not match the number in postgres: [{1}]".
                format(number_datasets_private_graph_virtuoso, number_datasets_private_graph_postgres))
    number_datasets_public_graph_virtuoso = long(
        number_datasets_per_graph_virtuoso[0]['number_public_datasets']['value'])
    number_datasets_public_graph_postgres = number_datasets_per_graph_postgresql[0][1]
    if number_datasets_public_graph_virtuoso != number_datasets_public_graph_postgres:
        raise MigrationError(message=
            u"Number of public datasets in virtuoso : [{0}] does not match the number in postgres : [{1}]".
                format(number_datasets_public_graph_virtuoso, number_datasets_public_graph_postgres))


def validate_dataset_name(config_file_path):
    dataset_name_virtuoso = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "ckanName_dcatapop")

    packages = postgresql_helper.find_any_in_database(config_file_path=config_file_path,
                                                      table=Package,
                                                      order_by_clause=[Package.name])
    package_dict = {}
    for package in packages:
        package_dict[DATASET_URI_PREFIX + package.name] = package.name

    intersection = _filter_dicts(package_dict, dataset_name_virtuoso)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_dataset_name {0}'.format(element))
        raise MigrationError(message=
            u"Not the same ckan name for datasets: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_dataset_main_title(config_file_path):
    dataset_name_virtuoso = find_in_virtuoso_for_variables_names(DatasetSchemaDcatApOp, "", "title_dcterms")
    packages = postgresql_helper.find_any_in_database(config_file_path=config_file_path,
                                                      table=Package,
                                                      order_by_clause=[Package.name])
    package_dict = {}
    for package in packages:
        package_dict[DATASET_URI_PREFIX + package.name] = package.title

    intersection = _filter_dicts(package_dict, dataset_name_virtuoso)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_dataset_main_title {0}'.format(element))
        raise MigrationError(message=
            u"Not the same main title for datasets: differences between virtuoso and postgres : [{0}]".format(
                 len(intersection)))


def validate_simple_dataset_field(config_file_path="", root_object=object, result_clause="", postgres_variable_name="",
                                  *variables_names_virtuoso):
    dataset_name_virtuoso = find_in_virtuoso_for_variables_names(root_object, result_clause, *variables_names_virtuoso)
    condition = Package.state == ACTIVE_STATE
    packages = postgresql_helper.find_any_in_database(config_file_path, condition, Package,
                                                      order_by_clause=[Package.name])
    package_dict = {}
    for package in packages:
        if package_dict.get(DATASET_URI_PREFIX + package.name):
            package_dict[DATASET_URI_PREFIX + package.name].add(getattr(package, postgres_variable_name))
        else:
            package_dict[DATASET_URI_PREFIX + package.name] = set([getattr(package, postgres_variable_name)])


    intersection = _filter_sets(package_dict, dataset_name_virtuoso)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_simple_dataset_field {1}: {0}'.format(element, variables_names_virtuoso))
        raise MigrationError(message=
            u"Error validating variable [{0}] for datasets: differences between virtuoso and postgres : [{1}]".format(
                variables_names_virtuoso[-1],  len(intersection)))



def validate_title_dcterms(config_file_path="", root_object=object, result_clause="", postgres_variable_name="",
                                  *variables_names_virtuoso):
    dataset_name_virtuoso = find_in_virtuoso_for_variables_names(root_object, result_clause, *variables_names_virtuoso)
    condition = Package.state == ACTIVE_STATE

    packages = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.DATASET_TITLE_WITH_TRANSLATIONS,
        config_file_path)

    package_dict = {}
    for package in packages:
        if package_dict.get(DATASET_URI_PREFIX + package.name):
            package_dict[DATASET_URI_PREFIX + package.name].add(package[1])
            if package[2]:
                package_dict[DATASET_URI_PREFIX + package.name].add(package[2])

        else:
            package_dict[DATASET_URI_PREFIX + package.name] = set([package[1]])
            if package[2]:
                package_dict[DATASET_URI_PREFIX + package.name].add(package[2])


    intersection = _filter_sets(package_dict, dataset_name_virtuoso)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_simple_dataset_field {1}: {0}'.format(element, variables_names_virtuoso))
        raise MigrationError(message=
            u"Error validating variable [{0}] for datasets: differences between virtuoso and postgres : [{1}]".format(
                variables_names_virtuoso[-1],  len(intersection)))


def validate_description_dcterms(config_file_path="", root_object=object, result_clause="", postgres_variable_name="",
                                  *variables_names_virtuoso):
    dataset_name_virtuoso = find_in_virtuoso_for_variables_names(root_object, result_clause, *variables_names_virtuoso)
    condition = Package.state == ACTIVE_STATE

    packages = postgresql_helper.execute_query(
        postgres_migration_validation_query_constants.DATASET_DESCRIPTION_WITH_TRANSLATIONS,
        config_file_path)

    package_dict = {}
    for package in packages:
        if package_dict.get(DATASET_URI_PREFIX + package.name):
            package_dict[DATASET_URI_PREFIX + package.name].add(package[1])
            #if package[2]:
            #    package_dict[DATASET_URI_PREFIX + package.name].add(package[2])

        else:
            package_dict[DATASET_URI_PREFIX + package.name] = set([package[1]])
           # if package[2]:
            #    package_dict[DATASET_URI_PREFIX + package.name].add(package[2])


    intersection = _filter_sets(package_dict, dataset_name_virtuoso)
    if len(intersection) > 0:
        for element in intersection:
            log.warn(u'validate_description_dcterms {1}: {0}'.format(element, variables_names_virtuoso))
        raise MigrationError(message=
            u"Error validating variable [{0}] for datasets: differences between virtuoso and postgres : [{1}]".format(
                variables_names_virtuoso[-1],  len(intersection)))



def find_in_virtuoso_for_variables_names(root_object, result_clause, *variables_names):
    triple_store_crud_helper = TripleStoreCRUDHelpers()
    triplets = []

    root_triplet = Triplet(subject=SUBJECT, object=root_object('').type_rdf['0'].uri)

    triplets.append(root_triplet)

    for idx, variable_name in enumerate(variables_names):
        splitted_variable = variable_name.split("_")
        name = splitted_variable[0]
        short_prefix = splitted_variable[1]
        prefix = getattr(NAMESPACE_DCATAPOP, short_prefix)
        predicate = prefix + name
        if idx < 1:
            triplet = Triplet(subject=SUBJECT, predicate=predicate, object=OBJECT + str(idx))
        else:
            triplet = Triplet(subject=OBJECT + str(idx - 1), predicate=predicate, object=OBJECT + str(idx))
        triplets.append(triplet)
    graphs = [DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME]

    if result_clause is None or result_clause == "":
        result_clause = SUBJECT_WITH_SPACES + OBJECT + str(idx) + " "

    result = triple_store_crud_helper.find_any_in_graphs_for_where_clauses(graph_names=graphs,
                                                                           triplet_list=triplets,
                                                                           result_clause=result_clause)

    ret = {}
    for element in result:
        dataset = element.get(VIRTUOSO_SUBJECT_RETURN).get(VIRTUOSO_VALUE_KEY)
        if 'modified_dcterms' in variables_names:
            value =  dateutil.parser.parse(element.get(VIRTUOSO_OBJECT_RETURN + str(idx)).get(VIRTUOSO_VALUE_KEY))
        else:
            value = element.get(VIRTUOSO_OBJECT_RETURN + str(idx)).get(VIRTUOSO_VALUE_KEY)

        if ret.get(dataset):

            ret[dataset].add(value)
        else:
            ret[dataset] = set([value])

    return ret


def _filter_dicts(dict_one, dict_two):
    '''

    :param dict dict_one:
    :param dict dict_two:
    :return:
    '''
    result = []
    for item in dict_one.items():
        if item[1] != dict_two.get(item[0]):
            result.append((item[0], item[1], dict_two.get(item[0])))

    return result
    #return [(value[0], value[1]) for value in dict_one.items() if value[1] != dict_two.get(value[0])]


def _filter_sets(dict_one, dict_two):
    intersection = []
    for key, value in dict_one.iteritems():
        if value != dict_two.get(key, set()):
            intersection.append((key, value, dict_two.get(key, set())))

    return intersection