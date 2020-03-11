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

log = logging.getLogger(__file__)

dict_dataset_reference = {
    'name': 'ckanName_dcatapop',
    'title': 'title_dcterms',
    # 'author' : '',
    'description': 'description_dcterms',
}

# dict_resource_reference = {
#
# }

# dict_catalog_record_reference = {
# }


# {'id': obj.schema.uri.split('/')[-1],
#             'organization': obj.schema.publisher_dcterms['0'].uri.split('/')[-1].lower(),
#             'name': _get_translated_term_from_dcat_object(obj.schema, 'ckanName_dcatapop', language),
#             'alternative_title': _get_translated_term_from_dcat_object(obj.schema, 'alternative_dcterms', language),
#             'landing_page': obj.schema.landingPage_dcat['0'].uri,
#             'title': _get_translated_term_from_dcat_object(obj.schema, 'title_dcterms', language),
#             'description': _get_translated_term_from_dcat_object(obj.schema, 'description_dcterms', language),
#             #'identifier': _get_translated_term_from_dcat_object(obj.schema.identifier_adms.get('0',SchemaGeneric()).notation_scos, language),
#             'identifier': _get_translated_term_from_dcat_object(obj.schema, 'identifier_dcterms', language),
#             'eurovoc_domains': [{'title':'retrive','uri':'retrive'}, {'title':'from','uri':'from'},{'title': 'theme','uri':'theme'},{'title': 'and','uri':'and'},{'title':'get','uri':'get'},{'title':'from','uri':'from'},{'title':'controlled vocabulary','uri':'controlled vocabulary'}],
#             'concepts_eurovoc':[{'name':'retrive','uri':'','display_name':'retrive'}, {'name':'from','uri':'','display_name':'from'},{'name': 'theme','uri':'','display_name':'theme'},{'name': 'and','uri':'','display_name':'and'},{'name':'get','uri':'','display_name':'get'},{'name':'from','uri':'','display_name':'from'},{'name':'controlled vocabulary','uri':'','display_name':'controlled vocabulary'}],
#             'keywords': _get_translated_term_from_dcat_object(obj.schema, 'keyword_dcat', language),
#             'type_of_dataset': _get_translated_term_from_dcat_object(obj.schema, 'type_dcterms', language),#uri value! multivalue
#             'release_date': _get_translated_term_from_dcat_object(obj.schema, 'issued_dcterms', language),
#             'modified_date': _get_translated_term_from_dcat_object(obj.schema, 'modified_dcterms', language),
#             'accrual_periodicity': _get_translated_term_from_dcat_object(obj.schema, 'accrualPeriodicity_dcterms', language),#uri value!
#             'temporal_coverage_from': _get_translated_term_from_dcat_object(obj.schema.temporal_dcterms['0'], 'startDate_schema', language),
#             'temporal_coverage_to': _get_translated_term_from_dcat_object(obj.schema.temporal_dcterms['0'], 'endDate_schema', language),
#             'temporal_granularity': _get_translated_term_from_dcat_object(obj.schema, 'temporalGranularity_dcatapop', language),#uri value!
#             'geographical_coverage': _get_translated_term_from_dcat_object(obj.schema, 'spatial_dcterms', language),#uri value! multivalue
#             'language': _get_translated_term_from_dcat_object(obj.schema, 'language_dcterms', language),#uri value! multivalue
#             'version_description': _get_translated_term_from_dcat_object(obj.schema, 'versionNotes_adms', language),
#             'contact_points': _transform_contact_point_to_ui_schema(obj.get_schema_contact_point(), language),
#             'tracking_summary': 1,
#             #'views_total': _get_translated_term_from_dcat_object(obj.schema., language),
#             'metadata_created': _get_translated_term_from_dcat_object(obj.schema_catalog_record, 'issued_dcterms', language),#catalog record value!
#             'metadata_modified': _get_translated_term_from_dcat_object(obj.schema_catalog_record, 'modified_dcterms', language),#catalog record value!
#             'resources': _transform_resources_to_ui_schema(obj.schema, 'distribution_dcat', language),
#             'status': _get_translated_term_from_dcat_object(obj.schema_catalog_record, 'status_adms', language)
#             }
#
#
#
#
# def serialize_dataset_dict_to_dataset_schema(package_dict):
#     '''
#
#     :param dict package_dict:
#     :return:
#     '''
#     if package_dict:
#         for key, value in package_dict.iteritems():
