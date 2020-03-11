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

from doi.configuration.doi_configuration import DOIConfiguration
import pylons.config as config
import ujson

CKAN_PATH = config.get("ckan_path", '/opt/ckan')

CONFIGURATION_FILE_PATH = config.get("__file__", CKAN_PATH + '/conf/ecportal.ini')
CONFIGURATION_CITATION_STYLES_FILE_PATH = config.get("ckan.doi.citation_styles_config", CKAN_PATH + '/config/citation_styles.json')

CKAN_ECODP_URI_PREFIX = 'ckan.ecodp.uri_prefix'

VIRTUOSO_HOST_NAME = 'virtuoso.host.name'
VIRTUOSO_USER_NAME = 'virtuoso.user.name'
MDR_HOST_NAME = 'mdr.host.name'
MDR_HOST_NAME_AUTHENTICATED = 'mdr.host.name.auth'
MDR_USER_NAME = 'mdr.user.name'

DOI_CONFIG = DOIConfiguration()
DOI_CONFIG.doi_prefix = config.get("ckan.doi.prefix")
DOI_CONFIG.doi_db_connection_string = config.get("sqlalchemy.url")
DOI_CONFIG.email_host = config.get("ckan.doi.email_host")
DOI_CONFIG.email_port = config.get("ckan.doi.email_port")
DOI_CONFIG.report_sender_email = config.get("ckan.doi.report_sender_email")
DOI_CONFIG.report_receiver_email = config.get("ckan.doi.report_receiver_email")
DOI_CONFIG.report_log_directory = config.get("ckan.doi.report_log_directory")
DOI_CONFIG.submission_doi_ra_url = config.get("ckan.doi.submission_doi_ra_url")
DOI_CONFIG.submission_doi_ra_user = config.get("ckan.doi.submission_doi_ra_user")
DOI_CONFIG.submission_doi_ra_password = config.get("ckan.doi.submission_doi_ra_password")
DOI_CONFIG.submission_doi_sender_email = config.get("ckan.doi.submission_doi_sender_email")
DOI_CONFIG.submission_doi_from_company = config.get("ckan.doi.submission_doi_from_company")
DOI_CONFIG.submission_doi_to_company = config.get("ckan.doi.submission_doi_to_company")
DOI_CONFIG.citation_resolver = config.get("ckan.doi.citation_resolver")
DOI_CONFIG.citation_file_resolver = config.get("ckan.doi.citation_file_resolver")
DOI_CONFIG.citation_style = config.get("ckan.doi.citation_style", 'harvard-cite-them-right')

DATASET_URI_PREFIX = config.get(CKAN_ECODP_URI_PREFIX, 'http://data.europa.eu/88u') + '/dataset'

try:
    with open(CONFIGURATION_CITATION_STYLES_FILE_PATH, "r") as entry:
        DOI_CONFIG.citation_formats = ujson.load(entry)
except IOError as e:
    # _log.error("Configuration file \"citation_styles.json\" is missing.")
    DOI_CONFIG.citation_formats = {}
