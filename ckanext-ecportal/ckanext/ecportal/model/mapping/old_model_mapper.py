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
from ckanext.ecportal.forms import ECPortalDatasetForm
import json as json
import logging
from ckanext.ecportal.model.schemas.dcatapop_period_of_time_schema import PeriodOfTimeSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.model.schemas.dcatapop_category_schema import TemporalGranularitySchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import FrequencySchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_checksum_schema import ChecksumSchemaDcatApOp

import ckanext.ecportal.lib.ui_util as util
import ckanext.ecportal.lib.groups_util as group_util


log = logging.getLogger(__name__)

def package_show_schema(dataset):
    '''

    :param DatasetDcatApOp dataset:
    :return:
    '''

    #form = ECPortalDatasetForm()
    schema = establish_package_mapping(dataset)
    #json_object = json.dumps(schema)
    return schema


def __schema_keys(schema_dict):

    result_list = {}

    for field, value in schema_dict.items():

        if isinstance(value, dict):
            result_list[field] = __schema_keys(value)
        else:
            result_list[field] = ''

    return result_list

def establish_package_mapping(dataset):
    '''

    :param DatasetDcatApOp dataset:
    :return:
    '''
    schema = {
            "maintainer": None,
            "author": None,
            "relationships_as_object": [],
            "tag_string": None,
            "temporal_coverage_to": dataset.schema.temporal_dcterms.get('0', PeriodOfTimeSchemaDcatApOp('')).endDate_schema.get('0', ResourceValue('')).value_or_uri,
            "private": True if dataset.privacy_state == 'private' else False,
            "maintainer_email": None,
            "num_tags": None,
            "id": dataset.dataset_uri,
            "metadata_created": dataset.schema_catalog_record.issued_dcterms.get('0', ResourceValue('')).value_or_uri,
            "modified_date": dataset.schema.modified_dcterms.get('0', ResourceValue('')).value_or_uri,
            "capacity": dataset.privacy_state,
            "metadata_modified": dataset.schema_catalog_record.modified_dcterms.get('0', ResourceValue('')).value_or_uri,
            "temporal_granularity": dataset.schema.temporalGranularity_dcatapop.get('0',TemporalGranularitySchemaDcatApOp('')).uri,
            "author_email": None,
            "isopen": True,
            "type_of_dataset": [ type.uri for type in dataset.schema.type_dcterms.values()],
            "relationships_as_subject": [],
            "state": None,
            "version": dataset.schema.versionInfo_owl.get('0',ResourceValue('')).value_or_uri,
            "concepts_eurovoc": [ type.uri for type in dataset.schema.subject_dcterms.values()],
            "license_id": None,
            "type": "dataset",
            "status": "http://data.europa.eu/euodp/kos/dataset-status/Completed",
            "num_resources": len(dataset.schema.topic_foaf.values()) + len(dataset.schema.distribution_dcat.values()),
            "keywords": util._get_translated_term_from_dcat_object(dataset.schema, 'keyword_dcat', 'en'),
            "rdf": None,
            "views_total": dataset.schema_catalog_record.numberOfViews_dcatapop.get('0',ResourceValue('')).value_or_uri,
            "temporal_coverage_from": dataset.schema.temporal_dcterms.get('0', PeriodOfTimeSchemaDcatApOp('')).startDate_schema.get('0', ResourceValue('')).value_or_uri,
            "tracking_summary": dataset.schema_catalog_record.numberOfViews_dcatapop.get('0',ResourceValue('')).value_or_uri,
            "creator_user_id": None,
            "interoperability_level": None,
            "license_title": None,
            "revision_timestamp": None,
            "organization": util._get_organization_translation_from_database(dataset.schema, "publisher_dcterms", 'en'),
            "name": dataset.schema.ckanName_dcatapop.get('0', ResourceValue('')).value_or_uri,
            "language": [ds_lang.uri for ds_lang in dataset.schema.language_dcterms.values()],
            "alternative_title": util._get_translated_term_from_dcat_object(dataset.schema, 'alternative_dcterms', 'en'),
            "accrual_periodicity": dataset.schema.accrualPeriodicity_dcterms.get('0',FrequencySchemaDcatApOp('')).uri,
            "description": util._get_translated_term_from_dcat_object(dataset.schema, 'description_dcterms', 'en'),
            "owner_org": group_util.get_group_by_name(dataset.schema.publisher_dcterms['0'].uri.split('/')[-1].lower()).id,
            "geographical_coverage": [geo_cov.uri for geo_cov in dataset.schema.spatial_dcterms.values()],
            "license_url": "http://data.europa.eu/euodp/kos/licence/EuropeanCommission",
            "title": util._get_translated_term_from_dcat_object(dataset.schema, 'title_dcterms', 'en'),
            "revision_id": None,
            "identifier": next((value.value_or_uri for value in dataset.schema.identifier_dcterms.values()),''),
            "version_description": util._get_translated_term_from_dcat_object(dataset.schema, 'versionNotes_adms', 'en'),
            "release_date": dataset.schema.issued_dcterms.get('0', ResourceValue('')).value_or_uri,

        }
    # schema.update(util._transform_contact_point_to_ui_schema(dataset.get_schema_contact_point(), 'en'))
    resources = []
    for distribution in dataset.schema.distribution_dcat.values(): #type: DistributionSchemaDcatApOp
        resources.append(establish_resource_schema_from_distribution(distribution))

    for doc in dataset.schema.page_foaf.values(): #type: DocumentSchemaDcatApOp
        resources.append(establish_resource_schema_from_documentation(doc))

    schema["resources"] = resources


    if hasattr(dataset.schema, "landingPage_dcat") and dataset.schema.landingPage_dcat:
            landing_page = dataset.schema.landingPage_dcat.get('0')
            if hasattr(landing_page, "url_schema") and dataset.schema.landingPage_dcat:
                try:
                    schema['url'] = landing_page.url_schema.get('0').value_or_uri
                except Exception as e:
                    log.warning('old model mapper landing page url_schema wrong type {0}'.format(dataset.dataset_uri))
                    schema['url'] = landing_page.url_schema.get('0', SchemaGeneric('')).uri
    else:
            schema['url'] = dataset.schema.landingPage_dcat.get('0', ResourceValue('')).value_or_uri



    tmp_list = []
    for value in dataset.schema.extensionValue_dcatapop.values():
        tmp_list.append({'key': value.title_dcterms.get('0', ResourceValue('')).value_or_uri, 'value': value.dataExtensionValue_dcatapop.get('0', ResourceValue('')).value_or_uri})
    for value in dataset.schema.extensionLiteral_dcatapop.values():
        tmp_list.append({'key': value.title_dcterms.get('0', ResourceValue('')).value_or_uri, 'value': value.dataExtensionLiteral_dcatapop.get('0', ResourceValue('')).value_or_uri})
    schema['extras'] = tmp_list

    #CKAN groups = { "name": grp.name}
    #themes = { "title": theme_uri}
    groups = [ {"name": group.uri} for group in dataset.schema.datasetGroup_dcatapop.values()] or []
    groups.extend([ {"title": theme.uri} for theme in dataset.schema.theme_dcat.values()])
    schema["groups"] = groups

    return schema


def establish_resource_schema_from_distribution(distribution):
    '''

    :param DistributionSchemaDcatApOp resource:
    :return:
    '''
    schema = {
                "datastore_active": False,
                "id": distribution.uri,
                "size": distribution.byteSize_dcat.get('0', ResourceValue('')).value_or_uri,
                "state": distribution.status_adms.get('0', SchemaGeneric('')).uri,
                "hash": distribution.checksum_spdx.get('0', ChecksumSchemaDcatApOp('')).checksumValue_spdx.get('0', ResourceValue('')).value_or_uri,
                "description": util._get_translated_term_from_dcat_object(distribution, 'description_dcterms', 'en'),
                "format": distribution.format_dcterms.get('0', SchemaGeneric('')).uri,
                "tracking_summary": None,
                "last_modified": distribution.modified_dcterms.get('0',ResourceValue('')).value_or_uri,
                "download_total_resource": distribution.numberOfDownloads_dcatapop.get('0', ResourceValue('')).value_or_uri,
                "url_type": None,
                "mimetype": None,
                "name": util._get_translated_term_from_dcat_object(distribution, 'title_dcterms', 'en'),
                "created": distribution.issued_dcterms.get('0',ResourceValue('')).value_or_uri,
                "url": next((value.uri for value in distribution.accessURL_dcat.values()),''),
                "iframe_code": distribution.iframe_dcatapop.get('0', ResourceValue('')).value_or_uri,
                "mimetype_inner": "",
                "position": None,
                "resource_type": distribution.type_dcterms.get('0', SchemaGeneric('')).uri
            }

    return schema

def establish_resource_schema_from_documentation(doc):
    '''

    :param DocumentSchemaDcatApOp resource:
    :return:
    '''
    schema = {
                "datastore_active": False,
                "id": doc.uri,
                "size": None,
                "state": None,
                "hash": "",
                "description": util._get_translated_term_from_dcat_object(doc, 'description_dcterms', 'en'),
                "format": doc.format_dcterms.get('0', SchemaGeneric('')).uri,
                "tracking_summary": None,
                "last_modified": None,
                "download_total_resource": None,
                "url_type": None,
                "mimetype": None,
                "name": util._get_translated_term_from_dcat_object(doc, 'title_dcterms', 'en'),
                "created": None,
                "url": next((value.value_or_uri for value in doc.url_schema.values()), ''),
                "iframe_code": None,
                "mimetype_inner": None,
                "position": None,
                "resource_type": doc.type_dcterms.get('0', SchemaGeneric('')).uri
            }

    return schema