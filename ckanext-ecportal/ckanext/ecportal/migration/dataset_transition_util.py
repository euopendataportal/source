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

import datetime
import logging

import ckanext.ecportal.lib.controlled_vocabulary_util as controlled_voc

import ckan.lib.navl.dictization_functions
import ckan.logic as logic

import ckanext.ecportal.lib.uri_util as uri_util
import ckanext.ecportal.lib.ingestion.ingestion_package as ingestion
import ckanext.ecportal.lib.dataset_util as dataset_util

from rdflib import XSD
from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric, ResourceValue
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP, CatalogRecordSchemaDcatApOp, DataThemeSchemaDcatApOp, \
    DatasetSchemaDcatApOp, DistributionSchemaDcatApOp, DocumentSchemaDcatApOp, FrequencySchemaDcatApOp, \
    ProvenanceStatementSchemaDcatApOp, StandardSchemaDcatApOp, DatasetGroupSchemaDcatApOp
from ckanext.ecportal.model.utils_convertor import Dataset_Convertor
import ckanext.ecportal.lib.controlled_vocabulary_util as controlled_vocabulary_util

from ckanext.ecportal.configuration.configuration_constants import DOI_CONFIG
from doi.facade.doi_facade import DOIFacade

MAIN_DOCUMENTATION = 'http://publications.europa.eu/resource/authority/documentation-type/DOCUMENTATION_MAIN'

RELATED_DOCUMENTATION = 'http://publications.europa.eu/resource/authority/documentation-type/DOCUMENTATION_RELATED'

WEB_RELATED_DOCUMENTATION = 'http://publications.europa.eu/resource/authority/documentation-type/WEBPAGE_RELATED'

WebService = 'http://publications.europa.eu/resource/authority/distribution-type/WEB_SERVICE'

Download = 'http://publications.europa.eu/resource/authority/distribution-type/DOWNLOADABLE_FILE'

Visualization = 'http://publications.europa.eu/resource/authority/distribution-type/VISUALIZATION'

lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin

_DOI_GENERATION_KEY = 'generate-doi'

_DOI_STRATEGY_SEQUENCE = 'SEQUENCE'

_DOI_STRATEGY_DCT_IDENTIFIER = 'DCTIDENTIFIER'

_DOI_FACADE = DOIFacade(DOI_CONFIG)

_LOGGER = logging.getLogger('dataset_transition_util')


def create_dataset_schema_for_package_dict(data_dict):
    name = data_dict.get('name')
    uri = uri_util.new_dataset_uri_from_name(name)

    dataset = DatasetDcatApOp(uri)

    # Catalog Record
    catalogRecord = CatalogRecordSchemaDcatApOp(uri_util.new_catalog_record_uri())
    date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    catalogRecord.issued_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
    catalogRecord.modified_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
    catalogRecord.primaryTopic_foaf['0'] = SchemaGeneric(dataset.schema.uri)

    dataset.schema_catalog_record = catalogRecord

    generated_dataset = __dataset_old_model_transformation(dataset, data_dict, dataset.schema)

    # Generate DOI if requested
    if _DOI_GENERATION_KEY in data_dict:
        doi = generate_doi_for_dataset(dataset, data_dict[_DOI_GENERATION_KEY])
        generated_dataset.set_doi(doi)

    return generated_dataset


def update_dataset_for_package_dict(dataset, data_dict):
    """

    :param DatasetDcatApOp dataset:
    :param data_dict:
    :return:
    """
    date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    dataset.schema_catalog_record.modified_dcterms = {}
    dataset.schema_catalog_record.modified_dcterms['0'] = ResourceValue(date, datatype=XSD.datetime)
    dataset.schema_catalog_record.numberOfViews_dcatapop = {'0': max(dataset.schema_catalog_record.numberOfViews_dcatapop.values() or  [ResourceValue("0")], key=lambda x: int(x.value_or_uri))}
    old_dataset = dataset.schema #needed for keeping the resource ids
    dataset.schema = DatasetSchemaDcatApOp(dataset.dataset_uri)

    return __dataset_old_model_transformation(dataset, data_dict, old_dataset)


def generate_doi_for_dataset(dataset, doi_generation_strategy):
    """
    Generate a doi for a dataset.
    :param DatasetDcatApOp dataset: The dataset.
    :param string doi_generation_strategy: One of the following strategies to be used for DOI generation:
                                           - SEQUENCE: generate the next DOI in the generation sequence.
                                           - DCTIDENTIFIER: generate a DOI based on the dctIdentifier value.
    :return: The generated doi
    """
    publishers = controlled_voc.retrieve_all_publishers()
    publisher = next((publisher for publisher, uri in publishers.items() if uri == dataset.schema.publisher_dcterms['0'].uri), None)

    generated_doi = None
    if doi_generation_strategy == _DOI_STRATEGY_SEQUENCE:
        generated_doi = _DOI_FACADE.generate_doi(str(publisher).lower(), dataset.schema.uri)
    elif doi_generation_strategy == _DOI_STRATEGY_DCT_IDENTIFIER:
        if len(dataset.schema.identifier_dcterms.keys()) == 0:
            error_message = 'No DCT identifier found in dataset for DOi generation'
            _LOGGER.error(error_message)
            raise BaseException(error_message)
        generated_doi = _DOI_FACADE.generate_doi(str(publisher).lower(), dataset.schema.uri, dataset.schema.identifier_dcterms['0'].value_or_uri)
    else:
        error_message = 'Unknown DOI generation strategy %s'.format(doi_generation_strategy)
        _LOGGER.error(error_message)
        raise BaseException(error_message)

    _DOI_FACADE.register_doi(generated_doi, dataset.build_DOI_dict())

    return generated_doi


def __dataset_old_model_transformation(dataset, data_dict, old_dataset=None):
    '''

    update the dataset object with the dict that contains the descriptin according to the old model.
    It maight be the dict of the old model description
    :param DatasetDcatApOp dataset:
    :param dict data_dict:
    :param DatasetSchemaDcatApOp old_dataset:
    :return:
    '''
    doi = None
    if old_dataset:
        for identifier in old_dataset.identifier_adms.values():
            if hasattr(identifier, "notation_skos"):
                notation = next((notation for notation in identifier.notation_skos.values() if notation.datatype == controlled_vocabulary_util.DOI_URI or notation.datatype.lower() == 'http://purl.org/spar/datacite/doi'.lower()),None) #type: ResourceValue
                if notation:
                    doi = identifier
                    break

    # Transform the old values to new ones
    from ckanext.ecportal.migration.old_model_values_to_new_model_convertor import OldModelValuesToNewModelConvertor
    transformer_old_values = OldModelValuesToNewModelConvertor(data_dict)
    data_dict = transformer_old_values.full_transformation_of_dict()

    convertor = Dataset_Convertor()
    data_dict['landing_page'] = data_dict.pop('url', '')
    data_dict['frequency'] = data_dict.pop('accrual_periodicity', '')
    data_dict['version_notes'] = data_dict.pop('accrual_description', '')
    if not data_dict.get('name', None):
        data_dict['name'] = dataset.dataset_uri.split('/')[-1]
    if not data_dict.has_key("title"):
        data_dict["title"] = data_dict.get("name","No title")

    # Privacy state
    dataset.privacy_state = __privacy_state_for_package_dict(data_dict)

    dataset.set_name(data_dict)
    dataset.set_alternative_titles(convertor, data_dict)
    dataset.set_descriptions(convertor, data_dict)
    dataset.set_title(convertor, data_dict)
    dataset.set_temporal_coverage(convertor, data_dict)
    dataset.set_keyword_string(convertor, data_dict)
    dataset.set_identifier(data_dict)
    dataset.set_type_dataset(convertor, data_dict)
    dataset_util.set_publisher_to_dataset_from_dict(dataset, data_dict)
    dataset.set_geographical_coverage(convertor, data_dict)
    dataset.set_contact(convertor, data_dict)
    dataset.set_language(convertor, data_dict)
    dataset.set_landing_page(data_dict)
    dataset.set_frequency(data_dict)
    dataset.set_version(data_dict)
    dataset.set_version_notes(convertor, data_dict)
    dataset.set_release_date(data_dict)
    dataset.set_modified_date(data_dict)
    dataset.set_creator(data_dict)
    dataset.set_is_part_of_Catalog(data_dict)

    index = len(dataset.schema.subject_dcterms.keys())
    for eurovoc_concept in data_dict.get('concepts_eurovoc', []):
        dataset.schema.subject_dcterms['{0}'.format(index)] = SchemaGeneric(eurovoc_concept)
        index += 1

    resource_list = data_dict.get('resources', [])

    groups = [group.get('name') for group in data_dict.get('groups', []) if group.get('name', '')]
    theme_set = [theme['title'] for theme in data_dict.get('groups', []) if theme.get('title', '')]

    if groups:
        groups = ingestion.get_groups_from_database_by_title(groups)

    for group in groups:
        # CKAN groups:
        index = len(dataset.schema.datasetGroup_dcatapop.keys())
        dataset.schema.datasetGroup_dcatapop['{0}'.format(index)] = DatasetGroupSchemaDcatApOp(group['name'], graph_name=dataset.graph_name)

    for theme in theme_set:
        length = str(len(dataset.schema.theme_dcat))
        data_theme_schema = DataThemeSchemaDcatApOp(theme, graph_name=dataset.schema.graph_name)
        dataset.schema.theme_dcat[length] = data_theme_schema

    distrib = []
    documentation = []
    for resource in resource_list:
        type = resource.get('resource_type', '')

        if type in [MAIN_DOCUMENTATION, RELATED_DOCUMENTATION, WEB_RELATED_DOCUMENTATION]:
            resource['title'] = resource.pop('name', 'Default_Title') or 'Default_Title'
            # resource['resource_type'] = type
            documentation.append(resource)
        else:
            # resource['resource_type'] = type
            resource['access_url'] = resource.pop('url', '')
            resource['title'] = resource.pop('name', 'Default_Title') or 'Default_Title'
            resource['release_date'] = resource.pop('created', '')
            resource['modification_date'] = resource.pop('last_modified', '')
            resource['licence'] = 'http://publications.europa.eu/resource/authority/licence/COM_REUSE'
            distrib.append(resource)

    if distrib:
        dataset.schema.distribution_dcat = convertor.convert_resources_distribution(distrib, old_dataset)
    if documentation:
        dataset.schema.page_foaf = convertor.convert_resources_page(documentation, old_dataset, dataset_uri=dataset.dataset_uri)

    if doi:
        #lemon_contexts = controlled_vocabulary_util.retrieve_all_notation_skos()
        #lemon_context_type = lemon_contexts.get(controlled_vocabulary_util.DOI_URI, {}).get('exactMatch', '')
        doi.notation_skos = {"0": ResourceValue(doi.notation_skos.get('0').value_or_uri, datatype=controlled_vocabulary_util.DOI_URI), "1": ResourceValue(doi.notation_skos.get('0').value_or_uri, datatype='http://purl.org/spar/datacite/doi')}
        dataset.schema.identifier_adms[str(len(dataset.schema.identifier_adms.values()))] = doi


    # Generate DOI if requested
    if _DOI_GENERATION_KEY in data_dict and not doi:
        doi_value = generate_doi_for_dataset(dataset, data_dict[_DOI_GENERATION_KEY])
        dataset.set_doi(doi_value)

    return dataset


def data_transformation_of_old_model_dataset(old_model_dict):
    '''
    convert the old model values exiting in the dataset of the old model to to a new mapped values.
    :param old_model_dict: # type: dict
    :return:
    '''
    transformed_dict = {}

    # convert the eurovoc values

    return transformed_dict


def __privacy_state_for_package_dict(data_dict):
    private = data_dict.get('private', None)
    capacity = data_dict.get('capacity', None)

    def __validate_private_property(property_value):
        return str(property_value).lower() in 'true, false'

    def __validate_capacity_property(property_value):
        return str(property_value).lower() in 'private, draft, public, published'

    if __validate_private_property(private):
        if str(private).lower() == 'true':
            return DCATAPOP_PRIVATE_DATASET
        if str(private).lower() == 'false':
            return DCATAPOP_PUBLIC_DATASET
    elif private is not None:
        raise logic.ValidationError("'private' property can only be 'true' or 'false': '{0}' is not supported".format(private))
    else:
        if __validate_capacity_property(capacity):
            if capacity.lower() in 'private, draft':
                return DCATAPOP_PRIVATE_DATASET
            if capacity.lower() in 'public, published':
                return DCATAPOP_PUBLIC_DATASET
        elif capacity is not None:
            raise logic.ValidationError("'capacity' property can only be 'private', 'draft', 'public' or 'published': '{0}' is not supported".format(capacity))

    return DCATAPOP_PUBLIC_DATASET
