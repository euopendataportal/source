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

import ckan.lib.navl.dictization_functions
import logging
import shutil
import requests

import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.lib.search.index as index
import ckanext.ecportal.lib.ingestion.ingestion_package as ingestion
import ckanext.ecportal.lib.ecodp_translations as ecodp_translations
import ckanext.ecportal.lib.ui_util as ui_util
import ckanext.ecportal.lib.uri_util  as uri_util

from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_helpers import TripleStoreIngestionHelpers

from solr import SolrException
from ckan.lib.search.common import make_connection, SearchError
from pylons import config
from ckan.common import _, json
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

indexer = index.PackageSearchIndex()
check_access = logic.check_access
render = base.render
abort = base.abort
redirect = base.redirect
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

log = logging.getLogger(__name__)

BASE_FILE_LOCATION = CKAN_PATH + '/ckan/var'




def ingest_package(context, ingestion_dict):
    result = True
    result_dict = {'created': [],
                   'updated': [],
                   'deleted': [],
                   'file_uploads': []}


    for package in ingestion_dict.get('dataset', [] ):
        uri = package.get('uri')
        tmp_context = context.copy()
        tmp_context['model'] = 'DCATAP'
        tmp_context['ignore_auth'] = True
        tmp_context['message'] = 'Manage Package: ingest object {0}'.format(uri)
        tmp_result = True
        new = True
        package['organization'] = ingestion_dict['manifest'][0]['publisher_uri']
        try:
            get_action('package_show')(tmp_context, {'uri': uri})
            new = False
        except logic.NotFound as e:
            log.debug('Dataset not found')
        try:
            if new:
                get_action('package_create')(tmp_context,package)
                ds = tmp_context['package']
                pkg = ui_util.transform_dcat_schema_to_form_schema(ds)
                result_dict['created'].append(pkg)
            else:
                get_action('package_update')(tmp_context,package)
                pkg = ui_util.transform_dcat_schema_to_form_schema(tmp_context['package'])
                result_dict['updated'].append(pkg)
        except ValidationError as e:
            errors = e.error_dict
            package['errors'] = errors
            tmp_result = False
        except NotAuthorized as e:
            import traceback
            log.error(traceback.print_exc())
            package['errors'] = {'fatal': {'NotAuthorized': ['{0},Ckan-name: {1}'.format(str(e), package.get('name',''))]}}
            tmp_result = False
        except Exception as e:
            log.warning('Ingestion of dataset {0} failed'.format(uri))
            import traceback
            log.error(traceback.print_exc())
            package['errors'] = {'fatal': {'Server Error': ['{0},Ckan-name: {1}'.format(str(e), package.get('name',''))]}}

            tmp_result = False

        result = tmp_result if result is True else False

    for delete_action in ingestion_dict.get('delete', {}):
        tmp_result = False


        try:
            tmp_result = delete_dataset(context, delete_action)
            if tmp_result is True:
                result_dict['deleted'].append(delete_action)
        except NotAuthorized as e:
            fatal = delete_action.get('errors', {}).get('fatal', {})
            fatal.update({'NotAuthorized': ['{0},Ckan-name: {1}'.format(str(e), delete_action.get('name', ''))]})
            delete_action.get('errors', {})['fatal'] = fatal
            tmp_result = False

        result = tmp_result if result is True else False

    for upload_action in ingestion_dict.get('files', {}):
        tmp_result = False
        upload_action['publisher'] = ingestion_dict.get('organization', {}).get('name', '').upper()
        tmp_result = upload_files(context, upload_action)
        if tmp_result is True:
            result_dict['file_uploads'].append(upload_action)

        result = tmp_result if result is True else False
    return result_dict if result is True else []

def delete_dataset(context, pkg_dict):

    id = {'id': pkg_dict.get('name','')}
    get_action('package_delete')(context,id)

    return True

def upload_files(context, file_dict):

    destination_path = '{0}/{1}/{2}'.format(BASE_FILE_LOCATION, file_dict['publisher'], file_dict['name'])
    shutil.copy2(file_dict.get('local_path'),destination_path)

    return True


