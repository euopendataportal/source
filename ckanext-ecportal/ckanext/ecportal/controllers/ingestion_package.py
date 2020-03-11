# -*- coding: utf-8 -*-
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

import ujson as json
import logging
import shutil
import copy

from datetime import date

import os
from ckanext.ecportal.model.schemas import DistributionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_agent_schema import AgentSchemaDcatApOp
from pylons import config

import ckan.lib.base as base
import ckan.lib.plugins
import ckan.lib.render
import ckan.plugins as plugins
import ckan.logic as logic
import ckanext.ecportal.logic as ecportal_logic
import ckanext.ecportal.lib.ingestion.ingestion_package as ingestion
import ckan.lib.helpers as core_helpers
import ckanext.ecportal.helpers as ckanext_helpers
import ckanext.ecportal.lib.ui_util as ui_util
import ckanext.ecportal.lib.uri_util  as uri_util
import ckanext.ecportal.action.ecportal_validation as validation
import ckan.plugins.toolkit as tk
import codecs

from ckanext.ecportal.action.rdf2odp_dataset_description import Rdf2odpDatasetDescription
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_helpers import TripleStoreIngestionHelpers
from ckan.common import _, request, c, OrderedDict
from ckan.model import Member, User, Group
from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
from ckanext.ecportal.controllers.package import ECPORTALPackageController
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

WORKDIR = CKAN_PATH + '/var/tmp'

abort = base.abort
get_action = logic.get_action
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized
lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin
dataset = ECPORTALPackageController()

MAX_DATASETS_FOR_INGESTION_PACKAGE = int(config.get('ckan.ingestion_package.max_datasets', '100')) if int(config.get('ckan.ingestion_package.max_datasets', '100')) < 15 else 15

BASE_DIR = config.get('ofs.storage_dir')

log = logging.getLogger(__name__)

URI_TEMPLATE = config.get('ckan.ecodp.uri_prefix', '')

CACHE_PARAMETERS = ['__cache', '__no_cache__']

class ECPortalIngestion_PackageController(base.BaseController):

    def upload_package(self):
        package_type = 'dataset'
        context = {'model': 'DCATAP',
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'upload': 'upload' in request.params}

        # Package needs to have a organization group in the call to
        # check_access and also to save it
        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        if context['upload']:
            # save file
            workdir = os.path.join(BASE_DIR, c.user)
            if not os.path.isdir(workdir): os.makedirs(workdir)
            params = dict(request.params.items())
            stream = params.get('file')
            label = params.get('key')
            try:
                file = open('%s/%s' % (workdir, label), 'w')
                file.write(stream.file.read())
                return base.render('storage/success.html')
            except Exception, e:
                import traceback
                log.error(traceback.print_exc())
            finally:
                file.close()

        vars = {'data': {}, 'errors': {},
                'error_summary': {}, 'action': 'upload_package'}

        self._setup_template_variables(context, {},
                                       package_type=package_type)
        c.form = base.render(self._package_form(package_type='upload_package'), extra_vars=vars)
        return base.render('user/manage_base.html')

    def manage_package(self):
        package_type = 'dataset'
        context = {'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'save_locally': 'save_locally' in request.params,
                   'add_rdf': 'add_rdf' in request.params,
                   'validate': 'validate' in request.params,
                   'add_delete': 'add_delete' in request.params,
                   'upload': 'upload' in request.params,
                   'start_ingestion': 'start_ingestion' in request.params}

        # Package needs to have a organization group in the call to
        # check_access and also to save it
        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        data = None
        workdir = os.path.join(BASE_DIR, c.user)
        if os.path.exists(os.path.join(workdir, request.POST.get('file_path', 'nofile'))):
            id = os.path.join(workdir, request.POST.get('file_path', ''))

        if context['upload']:
            request.POST.pop('upload')
            file = request.POST.pop('resource-file-upload')
            data = data or  ecportal_logic.transform_to_data_dict(request.POST)
            if not data.get('organization'):
                split_id = data['manifest'][0]['publisher_uri'].split('/')[-1]
                org = get_action('organization_show')(context, {'id': split_id.lower(),
                                                    'include_datasets': 'false'})
                data['organization'] = org
            if file not in [None,'']:
                data = self._safe_resource_upload(data, file)
            data['manifest'][0]['publisher_uri'] = 'http://publications.europa.eu/resource/authority/corporate-body/{0}'.format(data.get('organization', {}).get('name', '').upper())

        if context['validate']and not data:
            request.POST.pop('validate')
            data = self.__validate_package(context)


        if context['save_locally'] and not data:
            request.POST.pop('save_locally')

            return self.__safe_locally(context)


        if context['start_ingestion'] and not data:
            request.POST.pop('start_ingestion')
            data = self.__start_ingestion(context)
            if not isinstance(data, dict):
                return data

        if context['add_rdf'] and not data:
            request.POST.pop('add_rdf')
            data = self.__add_new_dataset(context)

        if context['add_delete'] and not data:
            request.POST.pop('add_delete')
            data = self.__add_delete_action()


        if not data:
            data = {'dataset': [],
                    'manifest': [{}],
                    'files': [],
                    'delete': [],
                    'organization': {}
                    }
            log.warn('[DB] check id {0}'.format(id))
            if id:

                if not id:
                    abort(400, _('No file found'))

                zf = ingestion.read_zip_file_content(id)

                if 'manifest.xml' not in zf.namelist() and 'datasets/' not in zf.namelist():
                    c.content = 'Uploaded zip is not an ingestion package'
                    return base.render('user/ingestion_error_document_template.html')

                ds_list = [file for file in zf.namelist() if '.rdf' in file and '/files' not in file]

                if len(ds_list) > MAX_DATASETS_FOR_INGESTION_PACKAGE:
                    c.content = 'Uploaded zip can not be processed, it has more than {0:d} datasets'.format(MAX_DATASETS_FOR_INGESTION_PACKAGE)
                    return base.render('user/ingestion_warning_document_template.html')

                datasets = {}
                log.warn('[DB] list files {0}'.format(zf.namelist()))
                for file in zf.namelist():
                    log.warn('[DB] file {0}'.format(file))
                    if '.xml' in file and '/files' not in file:
                        log.warn('[DB] xml file {0}'.format(file))
                        fileContent = zf.read(file)
                        simple_name = os.path.basename(os.path.splitext(file)[0])
                        manifest = ingestion.parse_xml_to_dict(fileContent)
                        ecodp_manifest = manifest.get('ecodp:manifest')
                        if not ecodp_manifest:
                            abort(400, _('The content of the ingested package is not valid'))

                        data['manifest'] = [
                            {'publisher_uri': ecodp_manifest.get('@ecodp:publisher'),
                             'package_id': ecodp_manifest.get('@ecodp:package-id'),
                             'creation_date': ecodp_manifest.get(
                                 '@ecodp:creation-date-time')}]

                        split_id = ecodp_manifest.get('@ecodp:publisher').split('/')[-1]
                        if not data.get('organization'):
                             org = get_action('organization_show')(context, {'id': split_id.lower(),
                                                                'include_datasets': 'false'})
                             data['organization'] = org


                        action_list = []

                        actions = ecodp_manifest.get('ecodp:action')

                        if isinstance( actions, list):
                            for del_action in actions:
                                log.warn('[DB] del_action: {0}'.format(del_action))
                                if del_action.get('ecodp:remove'):
                                    action_list.append({'uri': del_action.get('@ecodp:object-uri'),
                                                        'name': del_action.get('@ecodp:object-ckan-name')})


                                elif del_action.get('ecodp:add-replace'):
                                    log.warn('[DB] is OrderedDict {0}'.format(del_action))

                                    log.warn('[DB] add-replace {0}'.format(del_action))
                                    uri = del_action.get('@ecodp:object-uri')
                                    ckanname = del_action.get('@ecodp:object-ckan-name')
                                    action = del_action.get('ecodp:add-replace',{})
                                    path = action.get('@ecodp:package-path', '')
                                    if path.startswith('/'):
                                        path = path[1:]
                                    state = action.get('@ecodp:object-status')

                                    if isinstance(datasets.get(path, ''), list):
                                         datasets[path].append({'state': state,
                                                           'name':ckanname,
                                                            'uri': uri})
                                    else:
                                        datasets[path] = [{'state': state,
                                                           'name':ckanname,
                                                           'uri': uri}]

                        else:
                            if actions.get('ecodp:remove'):
                                    action_list.append({'uri': actions.get('@ecodp:object-uri'),
                                                        'name': actions.get('@ecodp:object-ckan-name')})

                            elif actions.get('ecodp:add-replace'):
                                uri = actions.get('@ecodp:object-uri')
                                ckanname = actions.get('@ecodp:object-ckan-name')
                                action = actions.get('ecodp:add-replace',{})
                                path = action.get('@ecodp:package-path', '')
                                if path.startswith('/'):
                                    path = path[1:]
                                state = action.get('@ecodp:object-status')

                                if isinstance(datasets.get(path, ''), list):
                                     datasets[path].append({'state': state,
                                                       'name':ckanname,
                                                        'uri': uri})
                                else:
                                    datasets[path] = [{'state': state,
                                                       'name':ckanname,
                                                       'uri': uri}]





                        data['delete'] = action_list


                    elif '/files' in file and not file.endswith('/'):
                        log.warn('[DB] upload file {0}'.format(file))
                        if not os.path.join(WORKDIR, 'files'): os.makedirs(os.path.join(WORKDIR, 'files'))
                        if not os.path.join(WORKDIR + '/files',
                                            data['manifest'][0].get('package_id')): os.makedirs(
                            os.path.join(WORKDIR + '/files', data['manifest'][0].get('package_id')))
                        local_path = zf.extract(file, os.path.join(WORKDIR + '/files',
                                                                   data['manifest'][0].get('package_id')))
                        upload_file = {'name': os.path.basename(file),
                                       'path': file,
                                       'local_path': local_path}
                        data['files'].append(upload_file)

               # URI may be a tmp uri
                log.warn('[DB] datasets {0}'.format(datasets))
                ingestion_helper = TripleStoreIngestionHelpers()
                for path, value in datasets.iteritems():
                    log.warn('[DB1] path {0} value {1}'.format(path, value))
                    fileContent = zf.read(path).decode('utf-8')
                    uris = {}
                    for action in value:
                        if not URI_TEMPLATE +'/dataset' in action['uri'] or  uri_util.is_uri_unique(action['uri']):
                            #create
                            new_uri = uri_util.new_dataset_uri_from_name(ckanname)
                            fileContent = fileContent.replace(action['uri'], new_uri)
                            uris[new_uri] = Rdf2odpDatasetDescription(action['name'], action['state'], action.get('generateDoi',''))
                        else:
                            uris[action['uri']] = Rdf2odpDatasetDescription(action['name'], action['state'], action.get('generateDoi',''))

                    tmp_dict = ingestion_helper.build_embargo_datasets_from_string_content(fileContent, uris) # type_ dict[str, DatasetDcatApOp]

                    if not tmp_dict:
                        abort(400, _('Data Error. Could not retrieve and transform dataset'))
                    for tmp_uri, tmp_ds in tmp_dict.iteritems():
                        log.warn('[DB2] path {0} value {1}'.format(tmp_uri, tmp_ds))
                        tmp_ds.privacy_state = uris[tmp_uri]

                        # split_id = tmp_ds.get_owner_org().split('/')[-1]
                        # if not data.get('organization'):
                        #      org = get_action('organization_show')(context, {'id': split_id.lower(),
                        #                                         'include_datasets': 'false'})
                        #      data['organization'] = org
                        ds_dict = {}
                        try:
                            ds_dict = ui_util.transform_dcat_schema_to_form_schema(tmp_ds)
                        except Exception as e:
                            import traceback
                            log.error(traceback.print_exc())
                            abort(400, _('Data Error. Could not retrieve and transform dataset'))
                        data['dataset'].append(ds_dict)

        orgs = get_action('organization_list_for_user')(context, {'permission': 'manage_group'})
        access = next((pub for pub in orgs if pub.get('name') == data['organization'].get('name','')), None)
        if not access:
            c.content = 'No permission to edit package with publisher {0}'.format(data['organization'].get('display_name',''))
            return base.render('user/ingestion_error_document_template.html')

        c.pkg_dict = data
        # for key, value in c.pkg_dict.get('datasets/EAC_Erasmus_mobility_statistics_2012_2013-odp.rdf').get('rdf:RDF').get('dcat:Dataset').iteritems():
        #    if 'dct:title' == key:
        #        new_lang = value.get('@xml:lang')
        #        new_text = value.get('#text')


        catalog_list = get_action('catalogue_list')(context, {'uri': {}}) or {}
        language = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')

        catalogs = {}
        for key, value in catalog_list.items():

            title = next((title.value_or_uri for title in value.schema.title_dcterms.values() if title.lang == language),key)
            catalogs[key] = title

        c.catalogs = catalogs

        errors = {}
        error_summary = {}

        data['resources_types'] = dataset.RESOURCES_TYPES
        tags = logic.get_action('tag_list')(context, {'vocabulary_id': u'concepts_eurovoc'})
        c.resources_types_documentation = dataset.RESOURCES_TYPES_DOCUMENTATION
        c.resources_types_distribution = dataset.RESOURCES_TYPES_DISTRIBUTION
        c.resources_types_visualization = dataset.RESOURCES_TYPES_VISUALIZATION

        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'manage_package'}

        self._setup_template_variables(context, {},
                                       package_type=package_type)
        c.form = base.render(self._package_form(package_type='ingestion_package'), extra_vars=vars)
        return base.render('user/manage_base.html')


    def __validate_package(self, context):
        data = ecportal_logic.transform_to_data_dict(request.POST)
        ui_datasets = []


        split_id = data['manifest'][0]['publisher_uri'].split('/')[-1]
        org = get_action('organization_show')(context, {'id': split_id.lower(),
                                                    'include_datasets': 'false'})
        data['organization'] = org

        for package in data.get('dataset', []):
            uri = package.get('uri')
            if not uri or '__temporal/uri' == uri:
                uri,  name= uri_util.new_cataloge_uri_from_title(package.get('title','default'))
                package['name'] = name
            if not package.get('name'):
                package['name'] = uri_util.create_name_from_title(package.get('title','default'))
            dataset = DatasetDcatApOp(uri)
            try:
                publisher_uri = data['manifest'][0]['publisher_uri']
                package['creator'] = publisher_uri
                dataset.create_dataset_schema_for_package_dict(package, {}, context)
                dataset.schema.publisher_dcterms['0'] = AgentSchemaDcatApOp(publisher_uri)

            except Exception as e:
                import traceback
                log.error(traceback.print_exc())

            dataset, errors = validation.validate_dacat_dataset(dataset, context)
            ui_ds = ui_util.transform_dcat_schema_to_form_schema(dataset)
            if errors:
                ui_ds['errors']  = errors
                data['errors'] = True
            ui_datasets.append(ui_ds)

        data['dataset'] = ui_datasets
        # data['manifest'][0]['publisher_uri'] = 'http://publications.europa.eu/resource/authority/corporate-body/{0}'.format(
        #             data.get('organization', {}).get('name', '').upper())

        return data


    def __safe_locally(self, context):
        data = ecportal_logic.transform_to_data_dict(request.POST)
        split_id = data['manifest'][0]['publisher_uri'].split('/')[-1]
        org = get_action('organization_show')(context, {'id': split_id.lower(),
                                                    'include_datasets': 'false'})
        data['organization'] = org
        datasets = []
        errors = []
        for package in data.get('dataset', []):
            ui_dict = {}
            uri = package.get('uri')
            if not uri or '__temporal/uri' == uri:
                uri,  name= uri_util.new_cataloge_uri_from_title(package.get('title','default'))
                package['name'] = name
            if not package.get('name'):
                package['name'] = uri_util.create_name_from_title(package.get('title','default'))
            dataset = DatasetDcatApOp(uri)
            try:
                dataset.create_dataset_schema_for_package_dict(package, {}, context)
                datasets.append(dataset)

            except Exception as e:
                import traceback
                log.error(traceback.print_exc())


        data['dataset'] = datasets
        self._create_temporary_files_for_packaging(context, data)
        return

    def __start_ingestion(self, context):
        data = ecportal_logic.transform_to_data_dict(request.POST)

        result_dict = get_action('ingest_package')(context, data)

        if result_dict:
            #success, redirect to result page
            redirect_targets = result_dict.get('updated', []) + result_dict.get('created', [])
            id_list = [ ('name',value.get('name')) for value in redirect_targets]
            #id_list.append([ value.get('name') for value in result_dict.get('created', [])])
            table = {'header': ['rdftool.ingestion.table.title', 'rdftool.ingestion.table.name', 'rdftool.ingestion.table.url', 'rdftool.ingestion.table.state']}
            rows = [{'rdftool.ingestion.table.title': value.get('title',''),
                     'rdftool.ingestion.table.name': value.get('name', ''),
                     'rdftool.ingestion.table.url': value.get('url', ''),
                     'rdftool.ingestion.table.state': value.get('private', ''),} for value in result_dict.get('updated', [])]
            table['data'] = copy.deepcopy(rows)
            c.datasets = {'updates': table.copy()}

            rows = [{'rdftool.ingestion.table.title': value.get('title', ''),
                     'rdftool.ingestion.table.name': value.get('name', ''),
                     'rdftool.ingestion.table.url': value.get('url', ''),
                     'rdftool.ingestion.table.state': value.get('private', ''), } for value in result_dict.get('created', [])]
            table['data'] = copy.deepcopy(rows)
            c.datasets['created'] = table.copy()

            table = {'header': ['rdftool.ingestion.table.title', 'rdftool.ingestion.table.name', 'rdftool.ingestion.table.url']}
            rows = [{'rdftool.ingestion.table.title': value.get('title', ''),
                     'rdftool.ingestion.table.name': value.get('name', ''),
                     'rdftool.ingestion.table.url': value.get('url', ''), } for value in result_dict.get('deleted', [])]
            table['data'] = copy.deepcopy(rows)
            c.datasets['deleted'] = table.copy()

            table = {'header': ['rdftool.ingestion.table.name', 'rdftool.ingestion.table.url']}
            rows = [{'rdftool.ingestion.table.name': value.get('name', ''),
                     'rdftool.ingestion.table.url': value.get('url', ''), } for value in result_dict.get('file_uploads', [])]
            table['data'] = copy.deepcopy(rows)
            c.datasets['file_uploads'] = table.copy()



            url = core_helpers.url_for(controller='ckanext.ecportal.controllers.user:ECPortalUserController',
                                action='dashboard')
            test = ''
            for field, name in id_list:
                test += '{0}:{1} '.format(field, name)

            url = ckanext_helpers.url_with_params(url, [('q', test), ('ext_boolean', 'any')])

            c.id_list = url
            self._setup_template_variables(context, {},
                                           package_type='dataset')
            return base.render('user/ingestion_report.html')


        else:
            data['errors'] = True
            tmp_list = data.get('dataset', [])
            result_list = []
            for ds in tmp_list:
                uri = ds.get('uri')
                dataset = DatasetDcatApOp(uri)
                try:
                    dataset.create_dataset_schema_for_package_dict(ds, {}, context)
                except Exception as e:
                    import traceback
                    log.error(traceback.print_exc())

                split_id = dataset.get_owner_org().split('/')[-1]
                if not data.get('organization'):
                     org = get_action('organization_show')(context, {'id': split_id.lower(),
                                                        'include_datasets': 'false'})
                     data['organization'] = org
                ui_ds = ui_util.transform_dcat_schema_to_form_schema(dataset)
                ui_ds['errors'] = ds.get('errors', {})
                result_list.append(ui_ds)

            #result_list.append({'id': 'new_dataset'})

            data['dataset'] = result_list



        return data

    def __add_new_dataset(self, context):
        data = ecportal_logic.transform_to_data_dict(request.POST)
        tmp_list = data.get('dataset', [])
        result_list = []

        split_id = data['manifest'][0]['publisher_uri'].split('/')[-1]
        if not data.get('organization'):
             org = get_action('organization_show')(context, {'id': split_id.lower(),
                                                'include_datasets': 'false'})
             data['organization'] = org

        for ds in tmp_list:
            uri = ds.get('uri')
            dataset = DatasetDcatApOp(uri)
            try:
                dataset.create_dataset_schema_for_package_dict(ds, {}, context)
            except Exception as e:
                import traceback
                log.error(traceback.print_exc())

            ui_ds = ui_util.transform_dcat_schema_to_form_schema(dataset)
            result_list.append(ui_ds)

        result_list.append({'id': 'new_dataset',
                            'uri': '__temporal/uri'})

        data['dataset'] = result_list

        return data

    def __add_delete_action(self,context):

        data = ecportal_logic.transform_to_data_dict(request.POST)
        tmp_list = data.get('delete', [])
        tmp_list.append({'name': 'new_delete_action'})
        data['delete'] = tmp_list

        ds_list = data.get('dataset', [])
        result_list = []
        for ds in ds_list:
            uri = ds.get('uri')
            dataset = DatasetDcatApOp(uri)
            try:
                dataset.create_dataset_schema_for_package_dict(ds, {}, context)
            except Exception as e:
                import traceback
                log.error(traceback.print_exc())
            split_id = dataset.get_owner_org().split('/')[-1]
            if not data.get('organization'):
                 org = get_action('organization_show')(context, {'id': split_id.lower(),
                                                    'include_datasets': 'false'})
                 data['organization'] = org
            ui_ds = ui_util.transform_dcat_schema_to_form_schema()
            result_list.append(ui_ds)

        data['dataset'] = result_list

        data['manifest'][0]['publisher_uri'] = 'http://publications.europa.eu/resource/authority/corporate-body/{0}'.format(
            data.get('organization', {}).get('name', '').upper())

        return data

    def _safe_resource_upload(self, data_dict, file):
        zip_name = data_dict['manifest'][0].get('package_id')
        try:
            if not os.path.isdir(os.path.join(WORKDIR, zip_name)): os.makedirs(os.path.join(WORKDIR, zip_name))
            if not os.path.isdir(os.path.join(WORKDIR + '/' + zip_name, 'datasets')): os.makedirs(os.path.join(WORKDIR + '/' + zip_name, 'datasets'))
            path = os.path.join(WORKDIR + '/' + zip_name, 'datasets/files')
            if not os.path.isdir(path): os.makedirs(path)
            stream = file
            label = file.filename.replace(' ', '_')

            file = open('%s/%s' % (path, label), 'w')
            file.write(stream.file.read())
            res_url = '{0}/uploads/{1}/{2}'.format(config.get('ckan.site_url','http://data.europa.eu/euodp'), data_dict.get('organization',{}).get('name', 'default'), label)
            files = data_dict.get('files',[])
            files.append({'local_path': path,
                          'path': '%s/%s' % ('datasets/files', label),
                          'name': label,
                          'url': res_url})
            data_dict['files'] = files
        except Exception, e:
            import traceback
            log.error(traceback.print_exc())
        finally:
            file.close()

        return data_dict


    def _create_temporary_files_for_packaging(self, context, data):
        zip_name = data['manifest'][0].get('package_id')
        if not data['organization']:
            data['organization'] = get_action('organization_show')(context,
                                                               {'id': data['manifest'][0].get('publisher'),
                                                                'include_datasets': 'false'})
        #data['organization'] =  [{'name': value['name']} for value in data['list']]
        try:
            if not os.path.exists(os.path.join(WORKDIR, zip_name)):os.makedirs(os.path.join(WORKDIR, zip_name))
            if not os.path.exists(os.path.join(WORKDIR + '/' + zip_name, 'datasets')):os.makedirs(os.path.join(WORKDIR + '/' + zip_name, 'datasets'))
            context['format'] = 'xml'
            new_fiel = dataset.create_rdf_from_data_dict(context, data)
            file = open('%s/%s/manifest.xml' % (WORKDIR, zip_name), 'w')
            file.write(new_fiel.encode('utf-8'))
            file.close()

            for value in data.get('dataset', []): #type: DatasetDcatApOp
                if not '__temporal' in value.schema.uri:
                    context['format'] = 'rdf'
                    value.schema.publisher_dcterms['0'] = AgentSchemaDcatApOp(data['manifest'][0]['publisher_uri'])
                    new_fiel = value.get_dataset_as_rdfxml()
                    with open('%s/%s/datasets/%s.rdf' % (WORKDIR, zip_name, value.schema.ckanName_dcatapop.get('0').value_or_uri), 'w') as file:
                        file.write(new_fiel.decode("utf-8").encode("utf-8"))

                    file.close()

            if not os.path.exists(os.path.join(WORKDIR + '/' + zip_name, 'datasets/files')):os.makedirs(os.path.join(WORKDIR + '/' + zip_name, 'datasets/files'))
            for file in data.get('files',[]):
                # if not os.path.join(WORKDIR+'/'+zip_name,'dataset/files'): os.makedirs(os.path.join(WORKDIR+'/'+zip_name,'dataset/files'))
                if not file.get('local_path') == os.path.join(WORKDIR + '/' + zip_name, 'datasets/files'):
                    shutil.copy2(file.get('local_path'), os.path.join(WORKDIR + '/' + zip_name, 'datasets/files'))

            ingestion.zip_temp_ingestion_package_folder(os.path.join(WORKDIR, zip_name), '%s.zip' % zip_name)
            zip_file = '%s.zip' % zip_name
            if os.path.isfile(zip_file):
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(zip_file)
                with open(zip_file, 'r') as f:
                    shutil.copyfileobj(f, base.response)
                base.response.headers['Content-Length'] = str(size)
                base.response.headers['Content-type'] = str('application/zip')
                base.response.headers['Content-Disposition'] = str('attachment; filename="%s"' % zip_file)
                return
        except Exception, e:
            import traceback
            log.error(traceback.print_exc())
        finally:
            shutil.rmtree(os.path.join(WORKDIR, zip_name))


    def get_dataset_information(self):
        log.info('Get information')
        context = {'user': c.user or c.author, 'auth_user_obj': c.userobj, 'for_view': True}

        # Package needs to have a organization group in the call to
        # check_access and also to save it
        try:
            check_access('package_create', context)
            context['ignore_auth'] = True
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        post_data = ecportal_logic.transform_to_data_dict(request.POST)
        raw_ids = post_data.get('ids').split(',')

        data_list = []
        global_org = None

        for id in raw_ids:
            dataset_dict = {}
            dataset = get_action('package_show')(context,{'id':id})
            try:
                for item in plugins.PluginImplementations(plugins.IPackageController):
                    dataset = item.before_view(dataset)
            except BaseException as e:
                log.error("plugin error on preparation of dataset")
            selected_dataset = context.get('package') #type:DatasetDcatApOp

            if not global_org:
                org_id = selected_dataset.schema.publisher_dcterms['0'].uri.split('/')[-1]
                global_org = get_action('organization_show')(context, {'id': org_id.lower(),
                                                        'include_datasets': 'false'})
            else:
                if global_org['name'] != selected_dataset.schema.publisher_dcterms['0'].uri.split('/')[-1].lower():
                    abort(403, _('Unauthorized to create a package from different Publisher'))

            #org = selected_dataset.schema.publisher_dcterms.get('0').uri
            organization = dataset.get("organization")# todo get the name of the organization
            dataset_name = selected_dataset.schema.ckanName_dcatapop.get('0').value_or_uri
            dataset_title = "No title"
            for titlte_dcterms in selected_dataset.schema.title_dcterms.values():
                if titlte_dcterms.lang == 'en':
                    dataset_title = titlte_dcterms.value_or_uri
            dataset_url = selected_dataset.schema.uri
            status = ['published' if selected_dataset.privacy_state == 'public' else 'draft'] # todo get the correct value
            dataset_dict['title'] = dataset_title
            dataset_dict['url'] = dataset_url
            dataset_dict['organization'] = organization
            dataset_dict['status'] = status
            dataset_dict['name'] = dataset_name

            data_list.append(dataset_dict)

        result = [{'title': value['title'],
                   'name': value['name'],
                   'url': value['url'],
                   'publisher': value['organization'].get('name','').upper(),
                   'state': next((item for item in value['status'] if item is not None), '')} for value in data_list]
        return json.dumps(result)


    def create_ingestion_package(self):
        log.info('Create ingestion Package')
        package_type = 'dataset'
        context = {'user': c.user or c.author, 'auth_user_obj': c.userobj}

        # Package needs to have a organization group in the call to
        # check_access and also to save it
        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        post_data = ecportal_logic.transform_to_data_dict(request.POST)

        url = post_data.pop('current_url')
        url_param = url.split('?')[1] if '?' in url else None

        package_name = post_data.get('ingestion_name')

        if '.zip' in package_name:
            package_id = package_name.split('.zip')[0]
        else:
            package_id = package_name
            package_name = '%s.zip' % package_name


        dataset_list = post_data.get('dataset')

        data_dict = {'dataset': [],
         'manifest': [],
         'files': [],
         'organization': {}}

        request_dict = {'permission': 'manage_group'}
        data_dict['organization'] =  next(item for item in get_action('organization_list_for_user')(context, request_dict))


        local_url = 'data/uploads'#/{0}'.format(data_dict['organization'].get('name').upper())

        global_org = None

        for dataset in dataset_list:
            get_action('package_show')(context, {'id': dataset['name']})
            dcat_dataset = context.get('package') #type:DatasetDcatApOp

            if not global_org:
                org_id = dcat_dataset.schema.publisher_dcterms['0'].uri.split('/')[-1]
                global_org = get_action('organization_show')(context, {'id': org_id.lower(),
                                                        'include_datasets': 'false'})


            #maybe check dataset.organization with 'global' organization
            #if dataset.get('organization' == data_dict.get('
            for resource in dcat_dataset.schema.distribution_dcat.values(): #type: DistributionSchemaDcatApOp
                for downloadURL_dcat in resource.downloadURL_dcat.values():
                    resource_url = downloadURL_dcat.uri
                    if local_url in resource_url:
                        #copy resource to tmp_location
                        local_path = resource_url.split('uploads')[1]
                        res_name = resource_url.split('/')[-1]

                        data_dict['files'].append({'name': res_name,
                                                   'path': '/datasets/files/%s' % res_name,
                                                   'local_path' : CKAN_PATH + '/var/uploads%s' % local_path})
                    elif '/storage/f/' in resource_url:
                        local_path = resource_url.split('/storage/f/')[1]
                        res_name = resource_url.split('/')[-1]
                        data_dict['files'].append({'name': res_name,
                                                   'path': '/datasets/files/%s' % res_name,
                                                   'local_path' : CKAN_PATH + '/var/file-storage/pairtree_root/de/fa/ul/t/obj/%s' % local_path})


            data_dict['dataset'].append(dcat_dataset)


        data_dict['manifest'].append({'package_id': package_id,
                              'creation_date': date.today().strftime('%Y-%m-%d'),
                                'publisher_uri': 'http://publications.europa.eu/resource/authority/corporate-body/%s' % global_org.get('name').upper()})


        return self._create_temporary_files_for_packaging(context, data_dict)



    def __get_users_organizations_ids(self, user):
        '''
        Retrieve all organizations of which the given user is a member
        '''

        query = ckan.model.Session.query(Group.id). \
            join(Member, Member.group_id == Group.id). \
            filter(Group.is_organization == True). \
            filter(Group.state != 'deleted'). \
            filter(Member.table_name == 'user'). \
            join(User, User.id == Member.table_id). \
            filter(User.name == user)

        user_orgs_ids = map(lambda tup: tup[0], query.all())
        return user_orgs_ids


    def _guess_package_type(self, expecting_name=False):
        """
            Guess the type of package from the URL handling the case
            where there is a prefix on the URL (such as /data/package)
        """

        # Special case: if the rot URL '/' has been redirected to the package
        # controller (e.g. by an IRoutes extension) then there's nothing to do
        # here.
        if request.path == '/':
            return 'dataset'

        parts = [x for x in request.path.split('/') if x]

        idx = -1
        if expecting_name:
            idx = -2

        pt = parts[idx]
        if pt == 'package':
            pt = 'dataset'

        return pt

    def _setup_template_variables(self, context, data_dict, package_type=None):
        return lookup_package_plugin(package_type).setup_template_variables(context, data_dict)

    def _package_form(self, package_type=None):
        log.debug(str(package_type) + " / " +
                  str(lookup_package_plugin(package_type)) + " / " +
                  str(lookup_package_plugin(package_type).package_form()))
        if package_type == 'ingestion_package':
            return 'user/manage_package_form.html'
        elif package_type == 'upload_package':
            return 'user/upload_package_form.html'

        return lookup_package_plugin(package_type).package_form()