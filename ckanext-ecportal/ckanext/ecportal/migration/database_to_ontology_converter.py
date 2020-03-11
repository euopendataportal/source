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
from operator import and_

import ckan.model as model

import re

import ckanext.ecportal.lib.uri_util as uri_util
from ckanext.ecportal.configuration.configuration_constants import CONFIGURATION_FILE_PATH
from ckanext.ecportal.lib.controlled_vocabulary_util import COM_REUSE
from ckanext.ecportal.lib.uri_util import new_distribution_uri, new_documentation_uri, create_blank_node_replacement_uri
from ckanext.ecportal.migration.datasets_migration_manager import ControlledVocabulary
from ckanext.ecportal.migration.error.migration_error import MigrationError
from ckanext.ecportal.migration.migration_constants import VOC_LANGUAGE_ID, VOC_GEO_COVERAGE, VOC_DATASET_TYPE, \
    VOC_CONCEPTS_EUROVOC, VOC_STATUS, MAIN_DOCUMENTATION, RELATED_DOCUMENTATION, \
    WEB_RELATED_DOCUMENTATION, \
    CONTACT_NAME, CONTACT_EMAIL, CONTACT_TELEPHONE, \
    CONTACT_ADDRESS, CONTACT_WEBPAGE, ACTIVE_STATE, EIT, DATA_SOURCE, CLC, KIC, MODIFIED_DATE, THIS_IS_EXTRA_FIELD, \
    ANALYST_IN_EXTRA_FIELD, SOURCE, EVALUATION_DATE, RELEASE_DATE, CITATION, METADATA_LANGUAGE, IDENTIFIER, \
    ALTERNATIVE_TITLE, TEMPORAL_COVERAGE_FROM, ACCRUAL_PERIODICITY, ORGANIZATION, GROUP, EUROVOC_DOMAIN, \
    DATASET_URI_PREFIX, TEMPORAL_COVERAGE_TO
from ckanext.ecportal.migration.postgresql.dto.postgresql_dtos import Package, PackageExtra, PackageTag, Tag, \
    ResourceGroup, Resource, Member, TermTranslation
from ckanext.ecportal.migration.postgresql.helpers.postgresql_helper import find_any_in_database, \
    get_metadata_created_timestamp
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp, DCATAPOP_PUBLIC_GRAPH_NAME, \
    DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.model.schemas import *
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.multilingual.languages_constants import LanguagesConstants
from ckanext.ecportal.virtuoso import PRIVACY_STATE_PRIVATE
from ckanext.ecportal.virtuoso.data_type_constants import CONCEPT, DATE_TIME, ADDRESS, DOCUMENT, WORK, VOICE
from rdflib import XSD
from ckanext.ecportal.migration.mappig_file_formats import mapping_file_formats_manual


log = logging.getLogger("paster")


class DatabaseToOntologyConverter:
    def __init__(self):
        pass

    configuration_file = CONFIGURATION_FILE_PATH


def convert_package_to_dataset(package=Package(), controlled_vocabulary=ControlledVocabulary(),
                               configuration_file=CONFIGURATION_FILE_PATH):
    package_extra_list = \
        retrieve_package_extra_list_from_postgres(configuration_file, package)  # type: list[PackageExtra]

    tag_list = retrieve_tag_list_from_postgres(configuration_file, package)

    resource_list = retrieve_resource_list(configuration_file, package)

    dataset_uri = DATASET_URI_PREFIX + package.name
    dataset = DatasetDcatApOp(dataset_uri)

    dataset.graph_name = DCATAPOP_PUBLIC_GRAPH_NAME
    if package.private:
        dataset.graph_name = DCATAPOP_PRIVATE_GRAPH_NAME
        dataset.privacy_state = PRIVACY_STATE_PRIVATE

    dataset_schema = DatasetSchemaDcatApOp(dataset_uri,
                                           graph_name=dataset.graph_name)  # 1...1
    #dataset_schema.identifier_adms['0'] = SchemaGeneric(dataset_uri)
    dataset.schema_catalog_record = set_catalog_record(package, package_extra_list, dataset_schema)

    dataset_schema.versionInfo_owl['0'] = ResourceValue(package.version)

    #dataset_schema.isPartOfCatalog_dcatapop['0'] = CatalogSchemaDcatApOp(uri_util.new_cataloge_uri_from_title())

    set_landing_page(dataset_schema, package)

    set_package_titles(configuration_file, dataset_schema, package)  # 0...n
    set_package_descriptions(configuration_file, dataset_schema, package)  # 0...n

    dataset_schema.ckanName_dcatapop['0'] = ResourceValue(package.name)  # 1...1

    dataset_schema.modified_dcterms['0'] = ResourceValue(str(package.metadata_modified))

    groups = retrieve_groups(configuration_file, package)
    # To process only once the groups, multiple set are done once.
    set_publisher_and_theme_and_group(dataset_schema, groups, controlled_vocabulary.controlled_publishers)  # 0...1
    if not dataset_schema.publisher_dcterms.get('0', None):
        owner = model.Group.get(package.owner_org)
        if owner:
            dataset_schema.publisher_dcterms['0'] = AgentSchemaDcatApOp('http://publications.europa.eu/resource/authority/corporate-body/{0}'.format(owner.name.upper()), graph_name=dataset_schema.graph_name)
        else:
            log.warn('Dataset {0} has no publisher'.format(dataset_schema.uri))
            #raise MigrationError(message='Dataset {0} has no publisher'.format(dataset_schema.uri))

    for package_extra in package_extra_list:
        if package_extra.value:
            if package_extra.key == ACCRUAL_PERIODICITY:
                set_accrual_periodicity(dataset_schema, package_extra,
                                        controlled_vocabulary.controlled_frequencies)  # 0...1
            elif package_extra.key == TEMPORAL_COVERAGE_FROM:
                set_temporal(dataset_schema, package_extra)  # 0...1
            elif package_extra.key == TEMPORAL_COVERAGE_TO:
                set_temporal_to(dataset_schema, package_extra)  # 0...1
            elif package_extra.key == ALTERNATIVE_TITLE:
                set_alternative_titles(configuration_file, dataset_schema, package_extra)  # 0...n
            elif package_extra.key == IDENTIFIER:
                set_identifier(dataset_schema, package_extra)  # 0...n
            elif package_extra.key == METADATA_LANGUAGE:
                pass
            elif package_extra.key == CITATION:
                pass
            elif package_extra.key == RELEASE_DATE:
                #dataset_schema.issued_dcterms['0'] = ResourceValue(value_or_uri=str(package_extra.value),
                #                                         datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)  # 0...1
                pass
            elif package_extra.key == EVALUATION_DATE:
                pass
            elif package_extra.key == SOURCE:
                pass
            elif package_extra.key == ANALYST_IN_EXTRA_FIELD:
                pass
            elif package_extra.key == THIS_IS_EXTRA_FIELD:
                pass
            elif package_extra.key == MODIFIED_DATE:
                pass
            elif package_extra.key == KIC:
                pass
            elif package_extra.key == CLC:
                pass
            elif package_extra.key == DATA_SOURCE:
                pass
            elif package_extra.key == EIT:
                pass
            elif package_extra.key == 'version_description':
                set_version_note(dataset_schema, package_extra)

    controlled_status = ""
    for tag in tag_list:  # type: Tag
        if tag.name:
            if not tag.vocabulary_id:  # where voc = /
                set_keyword(dataset_schema, tag, configuration_file)  # 0...n
            elif tag.vocabulary_id == VOC_LANGUAGE_ID:  # where voc = language
                set_language(dataset_schema, tag, controlled_vocabulary.controlled_languages)  # 0...n
            elif tag.vocabulary_id == VOC_GEO_COVERAGE:  # where voc = geographical_coverage
                set_spatial(dataset_schema, tag, controlled_vocabulary.controlled_country)  # 0...n
            elif tag.vocabulary_id == VOC_DATASET_TYPE:  # where voc = dataset_type
                set_dataset_type(dataset_schema, tag)  # 0...1
            elif tag.vocabulary_id == VOC_CONCEPTS_EUROVOC:  # where voc = concepts_eurovoc
                set_subject(dataset_schema, tag)  # 0...1
            elif tag.vocabulary_id == VOC_STATUS:  # where voc = status
                package_status = tag.name  # 0...1
                if package_status:
                    package_status_upper_case = package_status.split('/')[-1].upper()
                    if package_status_upper_case == 'UNDERDEVELOPMENT':
                        package_status_upper_case = 'DEVELOP'
                    controlled_status = next(
                        uri for uri, value in controlled_vocabulary.controlled_status.iteritems() if
                        value == package_status_upper_case)

                    # TODO no property for that in new ontology
                    # elif tag.vocabulary_id == '0311e5a2-c6a0-49c7-84cc-1ceec129fd7c':  # where voc = interoperability_level

    # TODO verify this field
    dataset_schema.issued_dcterms['0'] = ResourceValue(str(get_metadata_created_timestamp(package.id)),
                                                       datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)  # 0...1

    for resource in resource_list:
        type = resource.resource_type or resource.extras
        if MAIN_DOCUMENTATION in type \
                or RELATED_DOCUMENTATION in type \
                or WEB_RELATED_DOCUMENTATION in type:
            set_document(configuration_file,
                         dataset_schema,
                         resource,
                         controlled_vocabulary.controlled_file_types,
                         controlled_vocabulary.controlled_documentation_types)  # 0...n
        else:
            set_distribution(configuration_file,
                             dataset_schema,
                             resource,
                             controlled_status,
                             controlled_vocabulary.controlled_file_types,
                             controlled_vocabulary.controlled_distribution_types)

    set_contact_point(dataset_schema, package_extra_list)

    dataset.schema = dataset_schema

    return dataset


def set_contact_point(dataset_schema, package_extra_list):
    kind = convert_package_extra_to_kind(dataset_schema, package_extra_list)  # 0...n
    dataset_schema.contactPoint_dcat['0'] = kind


def set_landing_page(dataset_schema, package):
    document_schema = DocumentSchemaDcatApOp(uri_util.create_uri_for_schema(DocumentSchemaDcatApOp),
                                             graph_name=dataset_schema.graph_name)
    document_schema.url_schema['0'] = ResourceValue(package.url)
    document_schema.topic_foaf['0'] = SchemaGeneric(dataset_schema.uri)
    document_schema.title_dcterms['0'] = ResourceValue("title_" + package.url, lang='en')
    document_schema.type_dcterms['0'] = SchemaGeneric("default_type_dcterms")
    dataset_schema.landingPage_dcat[str(len(dataset_schema.landingPage_dcat))] = document_schema


def retrieve_groups(configuration_file, package):
    condition = and_(Member.table_id == package.id, Member.table_name == "package")
    members = find_any_in_database(configuration_file, condition, Member)  # type: list[Member]
    groups = remove_deleted_and_duplicated_groups(members)
    return groups


def set_identifier(dataset_schema, package_extra):
    dataset_schema.identifier_dcterms['0'] = ResourceValue(package_extra.value)


def retrieve_resource_list(configuration_file=CONFIGURATION_FILE_PATH, package=Package()):
    resource_list = []
    resource_group_list = retrieve_resource_group_list_from_postgres(configuration_file,
                                                                     package)  # type: list[ResourceGroup]
    for resource_group in resource_group_list:
        resource_list = resource_list + \
                        (retrieve_resource_from_postgres(configuration_file, resource_group))
    return resource_list


def retrieve_resource_from_postgres(configuration_file=CONFIGURATION_FILE_PATH, resource_group=ResourceGroup()):
    condition =  and_(Resource.resource_group_id == resource_group.id,Resource.state == ACTIVE_STATE)
    return find_any_in_database(configuration_file, condition, Resource)


def retrieve_resource_group_list_from_postgres(configuration_file=CONFIGURATION_FILE_PATH, package=Package()):
    condition = ResourceGroup.package_id == package.id
    return find_any_in_database(configuration_file, condition, ResourceGroup)


def retrieve_tag_list_from_postgres(configuration_file=CONFIGURATION_FILE_PATH, package=Package()):
    tag_list = []
    package_tag_list = retrieve_package_tag_list(configuration_file, package)  # type: list[PackageTag]
    for package_tag in package_tag_list:
        if package_tag.state == ACTIVE_STATE:
            tag_list.append(package_tag.tag)
    return tag_list


def retrieve_tag_from_postgres(configuration_file=CONFIGURATION_FILE_PATH, package_tag=PackageTag()):
    condition = Tag.id = package_tag.tag_id
    return find_any_in_database(configuration_file, condition, Tag)


def retrieve_package_tag_list(configuration_file=CONFIGURATION_FILE_PATH, package=Package()):
    # type: (str, Package()) -> list[PackageTag]
    condition = PackageTag.package_id == package.id
    return find_any_in_database(configuration_file, condition, PackageTag)


def retrieve_package_extra_list_from_postgres(configuration_file=CONFIGURATION_FILE_PATH, package=Package()):
    # type: (str, Package()) -> list[PackageExtra]
    condition = PackageExtra.package_id == package.id
    return find_any_in_database(configuration_file, condition, PackageExtra)


def set_document(configuration_file=CONFIGURATION_FILE_PATH, dataset_schema=None,
                 resource=Resource, file_types=dict, documentation_types=dict):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    uri_prefix = 'http://data.europa.eu/88u'
    uri = '{0}/document/{1}'.format(uri_prefix, resource.id)

    document = DocumentSchemaDcatApOp(uri)
    type = resource.resource_type or resource.extras
    type_uri = ''
    if MAIN_DOCUMENTATION in type:
        type_uri = 'http://publications.europa.eu/resource/authority/documentation-type/DOCUMENTATION_MAIN'
    elif RELATED_DOCUMENTATION in type:
        type_uri = 'http://publications.europa.eu/resource/authority/documentation-type/DOCUMENTATION_RELATED'
    elif WEB_RELATED_DOCUMENTATION in type:
        type_uri = 'http://publications.europa.eu/resource/authority/documentation-type/WEBPAGE_RELATED'
    else:
        type_uri = type
        log.warn('nor mapping for type {0}'.format(type_uri))

    if type_uri:
        document.type_dcterms['0'] = SchemaGeneric(type_uri, default_type={'0': SchemaGeneric(DOCUMENTATIONTYPE_DCATAPOP)})
    else:
        log.warn('Could not map type {2} for documentation {1} of ds {0}'.format(document.uri, dataset_schema.uri, type_uri))

    file_type = ''
    if resource.format:
        tmp_format = resource.format
        if '/' in tmp_format:
            tmp_format = tmp_format.split('/')[-1]

        file_type = next((key for key, value in file_types.iteritems() if tmp_format == key.split('/')[-1].lower()), None)
        if not file_type:
            file_type = mapping_file_formats_manual.get(resource.format,resource.format)
        if file_type == resource.format:
            log.warn('No mapping for format {0} of documentation {1} in ds {2}'.format(file_type, document.uri, dataset_schema.uri))

    if file_type:
        document.format_dcterms['0'] = MediaTypeOrExtentSchemaDcatApOp(file_type,
                                                                   graph_name=dataset_schema.graph_name)
    else:
        log.warn('No format for document {0} of ds {1}'.format(document.uri,dataset_schema.uri))

    if resource.url:
        document.url_schema['0'] = ResourceValue(resource.url)
        # document = DocumentSchemaDcatApOp(uri_util.create_uri_for_schema(DocumentSchemaDcatApOp))
        # document.url_schema[str(len(document.url_schema))] = ResourceValue(landing_page)
        document.topic_foaf['0'] = SchemaGeneric(dataset_schema.uri)
        # document.title_dcterms['0'] = ResourceValue("title_" + landing_page, lang='en')
        # document.type_dcterms['0'] = SchemaGeneric("default_type_dcterms")

    set_document_descriptions(configuration_file, document, resource)

    length = str(len(dataset_schema.page_foaf))
    dataset_schema.page_foaf[length] = document


def set_document_descriptions(configuration_file=CONFIGURATION_FILE_PATH, document=None,
                              resource=Resource()):
    if not document:
        document = DocumentSchemaDcatApOp('')
    if resource.name:
        document.title_dcterms['0'] = ResourceValue(resource.name, LanguagesConstants.LANGUAGE_CODE_EN)
        name_condition = TermTranslation.term == resource.name
        titles = find_any_in_database(configuration_file, name_condition,
                                      TermTranslation)  # type: list[TermTranslation]
        for title in titles:
            length = str(len(document.title_dcterms))
            document.title_dcterms[length] = ResourceValue(title.term_translation, title.lang_code)

    if resource.description:
        document.description_dcterms['0'] = ResourceValue(resource.description, LanguagesConstants.LANGUAGE_CODE_EN)
        condition = TermTranslation.term == resource.description
        descriptions = find_any_in_database(configuration_file, condition,
                                            TermTranslation)  # type: list[TermTranslation]
        for description in descriptions:
            length = str(len(document.description_dcterms))
            document.description_dcterms[length] = ResourceValue(description.term_translation, description.lang_code)


def set_distribution(configuration_file=CONFIGURATION_FILE_PATH, dataset_schema=None,
                     resource=Resource(), status="", file_types=dict, distribution_types=dict):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    distribution = convert_resource_to_distribution(configuration_file, dataset_schema, resource,
                                                    file_types, status, distribution_types)
    length = str(len(dataset_schema.distribution_dcat))
    dataset_schema.distribution_dcat[length] = distribution


def set_subject(dataset_schema=None, tag=Tag()):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    subject = SchemaGeneric(tag.name)
    length = str(len(dataset_schema.subject_dcterms))
    dataset_schema.subject_dcterms[length] = subject


def set_dataset_type(dataset_schema=None, tag=Tag()):
    import ckanext.ecportal.model.utils_convertor as mapping
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    type = mapping.DATASET_TYPE_MAPPING.get(tag.name, '')
    if not type:
        log.warn('Could not map dataset type {0} of {1}'.format(tag.name, dataset_schema.uri))
        type = tag.name
    dataset_type = DatasetTypeSchemaDcatApOp(uri=type, graph_name=dataset_schema.graph_name)
    length = str(len(dataset_schema.type_dcterms))
    dataset_schema.type_dcterms[length] = dataset_type


def set_spatial(dataset_schema=None, tag=Tag(), controlled_countries=dict):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    location = tag.name
    if not controlled_countries.get(location):
        logging.warn(u"Migration:{1} location {0} is not in the controlled vocabulary countries-skos".format(location, dataset_schema.uri))
    spatial = LocationSchemaDcatApOp(uri=location, graph_name=dataset_schema.graph_name)
    length = str(len(dataset_schema.spatial_dcterms))
    dataset_schema.spatial_dcterms[length] = spatial


def set_language(dataset_schema=None, tag=Tag(), controlled_languages=dict):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    language = tag.name
    if not controlled_languages.get(language):
        logging.warn(u"Migration: {1} Language {0} is not in the controlled vocabulary languages-skos".format(language, dataset_schema.uri))
    linguistic_system = LinguisticSystemSchemaDcatApOp(language)
    length = str(len(dataset_schema.language_dcterms))
    dataset_schema.language_dcterms[length] = linguistic_system


def set_keyword(dataset_schema=None, tag=Tag(), configuration_file=CONFIGURATION_FILE_PATH):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    length = str(len(dataset_schema.keyword_dcat))
    condition = TermTranslation.term == tag.name
    keywords_translation = find_any_in_database(configuration_file, condition, TermTranslation)  # type: list[TermTranslation]
    length = str(len(dataset_schema.keyword_dcat))
    dataset_schema.keyword_dcat[length] = ResourceValue(value_or_uri=tag.name, lang='en')
    for keyword in keywords_translation:
        length = str(len(dataset_schema.keyword_dcat))
        dataset_schema.keyword_dcat[length] = ResourceValue(value_or_uri=keyword.term_translation, lang=keyword.lang_code)



def set_alternative_titles(configuration_file=CONFIGURATION_FILE_PATH, dataset_schema=None,
                           package_extra=PackageExtra()):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    dataset_schema.alternative_dcterms['0'] = ResourceValue(value_or_uri=package_extra.value,
                                                            lang=LanguagesConstants.LANGUAGE_CODE_EN)
    condition = TermTranslation.term == package_extra.value
    alternative_titles = \
        find_any_in_database(configuration_file, condition, TermTranslation)  # type: list[TermTranslation]
    for title in alternative_titles:
        length = str(len(dataset_schema.alternative_dcterms))
        dataset_schema.alternative_dcterms[length] = ResourceValue(value_or_uri=title.term_translation,
                                                                   lang=title.lang_code)


def set_temporal(dataset_schema=None, package_extra=PackageExtra()):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    length = str(len(dataset_schema.temporal_dcterms))
    period = dataset_schema.temporal_dcterms.get('0',None)
    if not period:
        period = PeriodOfTimeSchemaDcatApOp("period_of_time-" + str(create_blank_node_replacement_uri()),
                                        graph_name=dataset_schema.graph_name)
    period.startDate_schema['0'] = ResourceValue(package_extra.value,
                                                               datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)
    dataset_schema.temporal_dcterms['0'] = period

def set_temporal_to(dataset_schema=None, package_extra=PackageExtra()):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    length = str(len(dataset_schema.temporal_dcterms))
    period = dataset_schema.temporal_dcterms.get('0', None)
    if not period:
        period = PeriodOfTimeSchemaDcatApOp("period_of_time-" + str(create_blank_node_replacement_uri()),
                                            graph_name=dataset_schema.graph_name)
    period.endDate_schema['0'] = ResourceValue(package_extra.value,
                                                               datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)
    dataset_schema.temporal_dcterms['0'] = period

def set_accrual_periodicity(dataset_schema=None, package_extra=PackageExtra(), frequencies=dict):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    frequency_postgres = package_extra.value
    if frequency_postgres:
        uri = ''

        frequency = next((key for key, value in frequencies.iteritems() if value == frequency_postgres.upper()), None)
        if frequency:
            uri = frequency
        else:
            uri = frequency_postgres
            log.warn('Could not map accrual_periodicity to new MDR value for {0}'.format(dataset_schema.uri))
        accrual_periodicity = FrequencySchemaDcatApOp(uri, graph_name=dataset_schema.graph_name)
        dataset_schema.accrualPeriodicity_dcterms['0'] = accrual_periodicity


def set_publisher_and_theme_and_group(dataset_schema=None, groups=set,
                                      controlled_publishers=dict):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    for group in groups:
        controlled_publisher = retrieve_controlled_publisher(controlled_publishers, group)
        set_publisher(dataset_schema, group, controlled_publisher)  # 0...1
        set_group(dataset_schema, group)  # 0...n

    set_theme(dataset_schema, [group.title for group in groups if group.type == EUROVOC_DOMAIN ])  # 1...n


def retrieve_controlled_publisher(controlled_publishers, group):
    # controlled_publisher = controlled_publishers.get(group.name.upper())
    controlled_publisher = next(
        (uri for uri, value in controlled_publishers.iteritems() if value == group.name.upper()), None)
    return controlled_publisher


def set_group(dataset_schema, group):
    if group.name:
        if group.type == GROUP:
            group = DatasetGroupSchemaDcatApOp(group.name, graph_name=dataset_schema.graph_name)
            dataset_schema.datasetGroup_dcatapop[str(len(dataset_schema.datasetGroup_dcatapop))] = group


def set_publisher(dataset_schema, group, controlled_publisher):
    if group.name:
        if group.type == ORGANIZATION:
            if controlled_publisher:
                publisher = AgentSchemaDcatApOp(controlled_publisher, graph_name=dataset_schema.graph_name)
                dataset_schema.publisher_dcterms['0'] = publisher


def set_theme(dataset_schema, group):
    from ckanext.ecportal.model.utils_convertor import Dataset_Convertor
        # TODO : need to define this class + type organization is composed of elements with spaces, should we keep them?
    theme_set = Dataset_Convertor.convert_eurovoc_domains_list(group)

    for theme in theme_set:
        length = str(len(dataset_schema.theme_dcat))
        data_theme_schema = DataThemeSchemaDcatApOp(theme, graph_name=dataset_schema.graph_name)
        dataset_schema.theme_dcat[length] = data_theme_schema


def remove_deleted_and_duplicated_groups(members):
    group_list = set()
    for member in members:
        if member.state == ACTIVE_STATE:
            group = member.group
            if group.state == ACTIVE_STATE:
                group_list.add(group)
    return group_list


def set_package_descriptions(configuration_file=CONFIGURATION_FILE_PATH, dataset_schema=None,
                             package=Package()):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    description = package.notes or package.description
    dataset_schema.description_dcterms['0'] = ResourceValue(description, lang=LanguagesConstants.LANGUAGE_CODE_EN)
    condition = TermTranslation.term == u'{0}'.format(description)
    descriptions = find_any_in_database(configuration_file, condition, TermTranslation)  # type: list[TermTranslation]
    for description in descriptions:
        length = str(len(dataset_schema.description_dcterms))
        dataset_schema.description_dcterms[length] = ResourceValue(description.term_translation,
                                                                   lang=description.lang_code)


def set_package_titles(configuration_file=CONFIGURATION_FILE_PATH, dataset_schema=None,
                       package=Package()):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    if package.title:
        dataset_schema.title_dcterms['0'] = ResourceValue(package.title, lang=LanguagesConstants.LANGUAGE_CODE_EN)
        condition = TermTranslation.term == package.title
        titles = find_any_in_database(configuration_file, condition, TermTranslation)  # type: list[TermTranslation]
        for title in titles:
            if title.term_translation:
                length = str(len(dataset_schema.title_dcterms))
                dataset_schema.title_dcterms[length] = ResourceValue(title.term_translation, lang=title.lang_code)


def convert_resource_to_distribution(configuration_file=CONFIGURATION_FILE_PATH,
                                     dataset_schema=None,
                                     resource=Resource(),
                                     file_types=dict,
                                     status="",
                                     distribution_types=dict):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")
    uri_prefix = 'http://data.europa.eu/88u'
    uri = '{0}/distribution/{1}'.format(uri_prefix, resource.id)
    distribution = DistributionSchemaDcatApOp(uri)

    type = resource.resource_type or resource.extras
    distribution.accessURL_dcat['0'] = SchemaGeneric(resource.url)  # 1...1 for postgres
    uri = ''
    if 'Feed' in type:
        uri = 'http://publications.europa.eu/resource/authority/distribution-type/FEED_INFO'
    elif 'WebService' in type:
        uri = 'http://publications.europa.eu/resource/authority/distribution-type/WEB_SERVICE'
    elif 'Download' in type:
        uri = 'http://publications.europa.eu/resource/authority/distribution-type/DOWNLOADABLE_FILE'
    elif 'Visualization' in type:
        uri = 'http://publications.europa.eu/resource/authority/distribution-type/VISUALIZATION'
    elif 'file.upload' in type:
        uri = 'http://publications.europa.eu/resource/authority/distribution-type/DOWNLOADABLE_FILE'
    else:
        log.warn('Could not map type {1} of resource {0}'.format(distribution.uri, type))

    if uri:
        distribution.type_dcterms['0'] = SchemaGeneric(uri,
                                                       default_type={'0':SchemaGeneric(DISTRIBUTIONTYPE_DCATAPOP)})  # 1...1
    else:
        log.warn('Could not map type for distribution {0} of ds {1}'.format(distribution.uri,dataset_schema.uri))


    set_distribution_descriptions(configuration_file, distribution, resource)  # 0...n

    if resource.format:
        tmp_format = resource.format
        if '/' in tmp_format:
            tmp_format = tmp_format.split('/')[-1]

        file_type = next((key for key, value in file_types.iteritems() if tmp_format == key.split('/')[-1].lower()), None)
        if not file_type:
            file_type = mapping_file_formats_manual.get(resource.format, resource.format)
        if file_type == resource.format:
            log.warn('Could not map file format {1} of resource {0}'.format(distribution.uri, resource.format))

        media_or_extent = MediaTypeOrExtentSchemaDcatApOp(file_type,
                                                              graph_name=dataset_schema.graph_name)
        distribution.format_dcterms['0'] = media_or_extent  # 0...1

    license = LicenseDocumentDcatApOp(uri=COM_REUSE, graph_name=dataset_schema.graph_name)
    distribution.license_dcterms['0'] = license  # 0...1

    if resource.created:
        distribution.issued_dcterms['0'] = ResourceValue(value_or_uri=str(resource.created),
                                                         datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)  # 0...1
    set_distribution_titles(configuration_file, distribution, resource)  # 0...n
    if resource.last_modified:
        distribution.modified_dcterms['0'] = ResourceValue(value_or_uri=str(resource.last_modified),
                                                           datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)  # 0...1

    distribution.downloadURL_dcat['0'] = SchemaGeneric(resource_uri=resource.url)

    if resource.description:
        distribution.description_dcterms['0'] = ResourceValue(resource.description,
                                                          lang=LanguagesConstants.LANGUAGE_CODE_EN)
    if status:
        distribution.status_adms['0'] = SchemaGeneric(status,
                                                      default_type= {'0': SchemaGeneric(
                                                          NAMESPACE_DCATAPOP.skos + CONCEPT)})  # 0...1

    if resource.resource_count:
        distribution.numberOfDownloads_dcatapop['0'] = ResourceValue(resource.resource_count, datatype=XSD.integer)
    return distribution


def set_distribution_descriptions(configuration_file=CONFIGURATION_FILE_PATH, distribution=None,
                                  resource=Resource()):
    if not distribution:
        distribution = DistributionSchemaDcatApOp('')
    if resource.description:
        distribution.description_dcterms['0'] = ResourceValue(resource.description or '',
                                                              LanguagesConstants.LANGUAGE_CODE_EN)
        condition = TermTranslation.term == resource.description
        descriptions = find_any_in_database(configuration_file, condition,
                                            TermTranslation)  # type: list[TermTranslation]
        for description in descriptions:
            length = str(len(distribution.description_dcterms))
            distribution.description_dcterms[length] = ResourceValue(description.term_translation,
                                                                     description.lang_code)


def set_distribution_titles(configuration_file=CONFIGURATION_FILE_PATH, distribution=None,
                            resource=Resource()):
    if not distribution:
        distribution = DistributionSchemaDcatApOp('')
    if resource.name:
        distribution.title_dcterms['0'] = ResourceValue(resource.name or '', LanguagesConstants.LANGUAGE_CODE_EN)
        condition = TermTranslation.term == resource.name
        titles = find_any_in_database(configuration_file, condition, TermTranslation)  # type: list[TermTranslation]
        for title in titles:
            length = str(len(distribution.title_dcterms))
            distribution.title_dcterms[length] = ResourceValue(title.term_translation, title.lang_code)


def convert_package_extra_to_kind(dataset_schema=None, package_extra_list=[PackageExtra]):
    if not dataset_schema:
        dataset_schema = DatasetSchemaDcatApOp("")

    if not package_extra_list:
        return

    kind = KindSchemaDcatApOp(uri_util.create_uri_for_schema(KindSchemaDcatApOp),
                              graph_name=dataset_schema.graph_name)

    for package_extra in package_extra_list:
        if package_extra.value:
            if package_extra.key == CONTACT_NAME:
                length = str(len(kind.organisationDASHname_vcard))
                kind.organisationDASHname_vcard[length] = ResourceValue(package_extra.value)
            elif package_extra.key == CONTACT_EMAIL:
                length = str(len(kind.hasEmail_vcard))
                kind.hasEmail_vcard[length] = SchemaGeneric(package_extra.value, graph_name=dataset_schema.graph_name)
            elif package_extra.key == CONTACT_TELEPHONE:
                telephone_number = re.sub('[^+\/0-9]', '', package_extra.value)
                if telephone_number != package_extra.value:
                    logging.info(u"Migration: {2} telephone number migrated from {0} to {1}".format(package_extra.value,
                                                                                    telephone_number, dataset_schema.uri))
                if telephone_number:
                    #remove space
                    telephone_number = telephone_number.replace(' ','')
                    telephone = TelephoneSchemaDcatApOp(
                        "telephone-" + package_extra_list[0].id + str(create_blank_node_replacement_uri()),
                        graph_name=dataset_schema.graph_name)
                    length_value = str(len(telephone.hasValue_vcard))
                    telephone.hasValue_vcard[length_value] = SchemaGeneric(
                        telephone_number,
                        graph_name=dataset_schema.graph_name)
                    telephone.type_rdf['0'] = NAMESPACE_DCATAPOP.vcard + VOICE
                    telephone.type_rdf['1'] = NAMESPACE_DCATAPOP.vcard + WORK
                    length_telephone = str(len(kind.hasTelephone_vcard))
                    kind.hasTelephone_vcard[length_telephone] = telephone
            elif package_extra.key == CONTACT_ADDRESS:
                # TODO: The address could be parses but the data are not formatted correctly.
                address = AddressSchemaDcatApOp(uri_util.create_uri_for_schema(AddressSchemaDcatApOp),
                    graph_name=dataset_schema.graph_name)
                length = str(len(address.streetDASHaddress_vcard))
                address.streetDASHaddress_vcard[length] = ResourceValue(package_extra.value,
                                                                        datatype=NAMESPACE_DCATAPOP.vcard + ADDRESS)
                address.postalDASHcode_vcard = ""
                address.locality_vcard = ""
                address.countryDASHname_vcard = ""
                length_address = str(len(kind.hasAddress_vcard))
                kind.hasAddress_vcard[length_address] = address
            elif package_extra.key == CONTACT_WEBPAGE:
                document = DocumentSchemaDcatApOp(new_documentation_uri(), graph_name=dataset_schema.graph_name)
                document.url_schema['0'] = ResourceValue(package_extra.value,
                                                         datatype=NAMESPACE_DCATAPOP.foaf + DOCUMENT)
                document.topic_foaf['0'] = SchemaGeneric(dataset_schema.uri)
                document.title_dcterms['0'] = ResourceValue("title_" + document.uri, lang='en')
                document.type_dcterms['0'] = SchemaGeneric("default_type_dcterms")
                length = str(len(kind.homePage_foaf))
                kind.homePage_foaf[length] = document

    return kind


def set_catalog_record(package, package_extra_list, dataset_schema):
    uri = uri_util.new_catalog_record_uri()
    schema_catalog_record = CatalogRecordSchemaDcatApOp(uri)
    schema_catalog_record.primaryTopic_foaf['0'] = dataset_schema

    schema_catalog_record.modified_dcterms['0'] = ResourceValue(str(package.metadata_modified),
                                                                datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)  # 0...1

    ts = get_metadata_created_timestamp(package.id)
    schema_catalog_record.issued_dcterms['0'] = ResourceValue(str(ts),
                                                              datatype=NAMESPACE_DCATAPOP.xsd + DATE_TIME)  # 0...1

    count = 0
    for value in [row.value for row in package_extra_list if row.key == 'metadata_language']:
        if value:
            schema_catalog_record.language_dcterms['{0}'.format(count)] = LinguisticSystemSchemaDcatApOp(value)

    tracking = model.TrackingSummary.get_for_package(dataset_schema.uri)

    if tracking:
        schema_catalog_record.numberOfViews_dcatapop['0'] = ResourceValue(tracking['total'], datatype=XSD.integer)

    return schema_catalog_record


def  set_version_note(dataset_schema, package_extra):
    dataset_schema.versionNotes_adms['0'] = ResourceValue(package_extra.value)