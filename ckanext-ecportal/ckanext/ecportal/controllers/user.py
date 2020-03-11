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
import shutil

from urllib import urlencode, urlopen

import ckan.controllers.package as core_package
import ckan.controllers.user as core_user
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.maintain as maintain
import ckan.lib.plugins
import ckan.lib.render
import ckan.logic as logic
import ckan.model as model
import ckan.new_authz as new_authz
import ckan.plugins as plugins
import ckan.plugins as p
import ckanext.ecportal.action.customsearch as customsearch
import ckanext.ecportal.lib.groups_util as util
import ckanext.ecportal.lib.ingestion.ingestion_package as ingestion
import ckanext.ecportal.lib.page_util as page_util
import ckanext.ecportal.logic as ecportal_logic
import os
import requests
import ckanext.ecportal.helpers as helper
from urlparse import urljoin, urlparse, parse_qsl, urlunparse
from ckan.common import _, request, c, g, OrderedDict, response
from ckan.lib.dictization import model_dictize
from ckan.model import Package, Member, User, Group
from ckanext.ecportal.controllers.package import ECPORTALPackageController
from ckanext.ecportal.lib.validation.ecportal_validator import Validator
from ckanext.ecportal.model.ecodp_package_contact_info import Package_contact_info
from pylons import config, session
from wheezy.validation.rules import email
from pylons.config import config
from lxml import objectify
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

redirect = base.redirect


WORKDIR = CKAN_PATH + '/var/tmp'

abort = base.abort
get_action = logic.get_action
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin
dataset = ECPORTALPackageController()

FILENAME = '/PUBLusr2/20150505145918_EAC_20150504143801.zip'
TEST = config.get('ofs.storage_dir') + FILENAME

BASE_DIR = config.get('ofs.storage_dir')

log = logging.getLogger(__name__)

CACHE_PARAMETERS = ['__cache', '__no_cache__']


def build_search_for_all_words(search):
    result = ''
    for token in search:
        if result == '':
            result = '(%s' % (token)
        else:
            result = '%s AND %s' % (result, token)

    return result + ')'


def build_search_for_any_words(search):
    result = ''
    for token in search:
        if result == '':
            result = '(%s' % (token)
        else:
            result = '%s OR %s' % (result, token)

    return result + ')'


def build_owner_filter(organisation_ids):
    result = ''
    for id in organisation_ids:
        if result == '':
            result = 'owner_org:%s' % id
        else:
            result = '%s OR %s' % (result, id)

    result = '%s' % result
    return result


def search_url(params, package_type=None):
    if not package_type or package_type in ('dataset', 'datasets'):
        url = h.url_for(controller='ckanext.ecportal.controllers.user:ECPortalUserController',
                        action='dashboard')
    else:
        url = h.url_for('{0}_search'.format(package_type))
    return core_package.url_with_params(url, params)


class ECPortalUserController(core_user.UserController):
    def logged_in(self):
        #override the logged_in method after the access was granted or denied
        #if login was successfull check the group membership
        if c.user:
            util.add_missing_user_to_all_groups()
        return super(ECPortalUserController, self).logged_in()

    def login_user(self, tup):
        if tup:
            user = tup[0]

            user_object = model.User.get(user)
            if not user_object:
                user_object = model.User.get('api')
                c.userobj = user_object
                c.user = 'api'

                try:
                    # Create user
                    user_attributes = tup[1]
                    user_name = user
                    user_email = user_attributes["email"].text
                    user_password = "random_password"
                    user_fullname = user_attributes["firstName"].text+" "+user_attributes["lastName"].text

                    h.get_action('user_create',
                                 {"name" : user_name,
                                  "email" : user_email,
                                  "password" : user_password,
                                  "fullname" : user_fullname})


                    rememberer = request.environ['repoze.who.plugins']['friendlyform']
                    identity = {'repoze.who.userid': user}
                    response.headerlist += rememberer.remember(request.environ,
                                                               identity)
                except logic.ActionError:
                    base.abort(401, _('Error while creating new user'))
            else:
                c.userobj = user_object
                c.user = user

                rememberer = request.environ['repoze.who.plugins']['friendlyform']
                identity = {'repoze.who.userid': user}
                response.headerlist += rememberer.remember(request.environ,
                                                           identity)

            self.logged_in()

    def read(self, id=None):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True, 'return_minimal':True,
                   'save': 'save' in request.params}
        data_dict = {'id': id,
                     'user_obj': c.userobj}

        context['with_related'] = True

        self._setup_user_template_variables(context, data_dict)

        if context['save']:
            request.POST.pop('save')
            data = ecportal_logic.transform_to_data_dict(request.POST)

            credential_validator = Validator({
                'contact_mailbox': [email]
                #'contact_phone_number': [IntPhoneNumberRule]
            })
            errors = {}
            succeed = credential_validator.validate(data, results=errors)

            if succeed is True:
                contact_info = Package_contact_info.get_by_user(c.userobj.id)
                if not contact_info:
                    contact_info = Package_contact_info(c.userobj.id)

                contact_info.from_dict(data)
                contact_info.save()
                h.flash_success(_('ecodp.user.save.success'))
            elif errors:
                h.flash_error(_('ecodp.user.save.error'))

            c.user_dict.update(data)

            c.errors = errors


        # The legacy templates have the user's activity stream on the user
        # profile page, new templates do not.
        if h.asbool(config.get('ckan.legacy_templates', False)):
            c.user_activity_stream = get_action('user_activity_list_html')(
                context, {'id': c.user_dict['id']})

        #vars = {'data': {}, 'errors': {}, 'error_summary': {}}
        #c.form = base.render('user/edit_contact_info_form.html', extra_vars=vars)
        return base.render('user/read.html')


    def read_contact_info(self, id=None):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True, 'return_minimal':True,
                   'save': 'save' in request.params}
        data_dict = {'id': id,
                     'user_obj': c.userobj}

        context['with_related'] = True

        self._setup_user_template_variables(context, data_dict)

        if context['save']:
            request.POST.pop('save')
            data = ecportal_logic.transform_to_data_dict(request.POST)

            credential_validator = Validator({
                'contact_mailbox': [email]
                #'contact_phone_number': [IntPhoneNumberRule]
            })
            errors = {}
            succeed = credential_validator.validate(data, results=errors)

            if succeed is True:
                contact_info = Package_contact_info.get_by_user(c.userobj.id)
                if not contact_info:
                    contact_info = Package_contact_info(c.userobj.id)

                contact_info.from_dict(data)
                contact_info.save()
                h.flash_success(_('ecodp.user.save.success'))
            elif errors:
                h.flash_error(_('ecodp.user.save.error'))

            c.user_dict.update(data)

            c.errors = errors


        # The legacy templates have the user's activity stream on the user
        # profile page, new templates do not.
        if h.asbool(config.get('ckan.legacy_templates', False)):
            c.user_activity_stream = get_action('user_activity_list_html')(
                context, {'id': c.user_dict['id']})

        #vars = {'data': {}, 'errors': {}, 'error_summary': {}}
        #c.form = base.render('user/edit_contact_info_form.html', extra_vars=vars)
        return base.render('user/read_contact_info.html')


    def dashboard(self):

        def query_for_datasets():
            query  =''

            if not new_authz.is_sysadmin(c.user):
                organisation_ids = self.__get_users_organizations_ids(c.user);

                if not organisation_ids:
                    # return an empty query result with the needed (i.e.: accessed later) elements
                    return {'results': [], 'count': 0}

                query = build_owner_filter(organisation_ids)

            if c.q != u'':
                search = c.q.strip().split(' ')
                result = ''
                if request.params.get('ext_boolean') == 'any':
                    result = build_search_for_any_words(search)
                elif request.params.get('ext_boolean') == 'all':
                    result = build_search_for_all_words(search)
                elif request.params.get('ext_boolean') == 'exact':
                    result = '("%s")' % (c.q)
                    log.info("%s" % (request.params.get('ext_boolean')))

                query = query + " + title:" + result;

            return query

        log.debug("Entering MDT dashboard")

        c.is_sysadmin = new_authz.is_sysadmin(c.user)

        context = {
            'for_view': True,
            'user': c.user or c.author,
            'auth_user_obj': c.userobj,
            'return_minimal': True,
            'ignore_capacity_check': True  # Display also private datasets
        }
        user_data = {"id":c.userobj.id,'user_obj': c.userobj}

        try:
            user_dict = logic.get_action('user_show')(context, user_data)
        except logic.NotFound:
            base.abort(404, _('User not found'))
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))

        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])
        c.search_choice = request.params.get('ext_boolean')

        # Save the used search paramters in a proper format to the exchange variable
        user = user_dict['name']

        log.debug("Start getting the datasets")
        # ---------------------------------------------------------------------------------------------------------------
        # Get the datasets
        from ckan.lib.search import SearchError

        package_type = self._guess_package_type()

        if request.GET.get('ext_boolean') in ['all', 'any', 'exact']:
            session['ext_boolean'] = request.GET['ext_boolean']
            session.save()

        # unicode format (decoded from utf8)
        c.q = request.params.get('q', u'')
        c.query_error = False

        q = query_for_datasets()

        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))
        limit = g.datasets_per_page

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        new_params_nopage = [];
        for key, value in params_nopage:
            if key == 'eurovoc_domains':
                new_params_nopage.append(('groups', value))
            else:
                new_params_nopage.append((key, value))

        params_nopage = new_params_nopage;

        def drill_down_url(alternative_url=None, **by):
            return h.add_url_param(alternative_url=alternative_url,
                                   controller='package', action='search',
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='ckanext.ecportal.controllers.user:ECPortalUserController',
                                      action='dashboard')

        c.remove_field = remove_field

        sort_by = request.params.get('sort', 'views_total desc')
        params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']

        def _sort_by(fields):
            """
            Sort by the given list of fields.

            Each entry in the list is a 2-tuple: (fieldname, sort_order)

            eg - [('metadata_modified', 'desc'), ('name', 'asc')]

            If fields is empty, then the default ordering is used.
            """
            params = params_nosort[:]

            if fields:
                sort_string = ', '.join('%s %s' % f for f in fields)
                params.append(('sort', sort_string))
            return search_url(params, package_type)

        c.sort_by = _sort_by
        if not sort_by:
            c.sort_by_fields = []
        else:
            c.sort_by_fields = [field.split()[0]
                                for field in sort_by.split(',')]

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params, package_type)

        c.search_url_params = urlencode(core_package._encode_params(params_nopage))

        try:
            c.fields = []
            # c.fields_grouped will contain a dict of params containing
            # a list of values eg {'tags':['tag1', 'tag2']}
            c.fields_grouped = {}
            search_extras = {}
            fq = ''

            # if request.params.get('private'):
            #    fq = 'private: %s' % request.params.get('private')

            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort', 'id'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        # paramFQ = 'groups' if (param == 'eurovoc_domains') else param;
                        fq += ' %s:"%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

                        # if package_type and package_type != 'dataset':
                        # Only show datasets of this particular type
                        #     fq += ' +dataset_type:{type}'.format(type=package_type)
                        #  else:
                        # Unless changed via config options, don't show non standard
                        # dataset types on the default search page
                        #     if not asbool(config.get('ckan.search.show_all_types', 'False')):
                        #         fq += ' +dataset_type:dataset'

            facets = OrderedDict()

            default_facet_titles = {
                'organization': _('Organizations'),
                'groups': _('Groups'),
                'tags': _('Tags'),
                'res_format': _('Formats'),
                'license_id': _('Licenses'),
            }

            for facet in g.facets:
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Facet titles
            for plugin in p.PluginImplementations(p.IFacets):
                facets = plugin.dashboard_facets(facets, package_type)

            c.facet_titles = facets

            facet_fields = facets.keys()
            facet_fields.append('private')
            data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facet_fields,
                'rows': limit,
                'start': (page - 1) * limit,
                'sort': sort_by,
                'extras': search_extras
            }

            if sort_by == 'modified_date desc':
                # This is the customized part for ODP-570
                # add the group parameter to the solr query
                data_dict['group'] = 'true'
                data_dict['group.query'] = [
                    '-organization:estat AND -organization:comp AND -organization:grow', 'organization:estat',
                    'organization:comp', 'organization:grow']
                data_dict['group.format'] = 'simple'
                data_dict['rows'] = 2147483646

                query = get_action('custom_package_search')(context, data_dict)

                cached_result = []

                for name, group in query['groups'].iteritems():
                    cached_result += group['doclist']['docs']

                start = (page - 1) * limit
                result_list = customsearch.check_solr_result(context, cached_result[start:], limit)


            else:
                query = get_action('package_search')(context, data_dict)
                result_list = query['results']

            c.sort_by_selected = query['sort']

            c.page = page_util.Page(
                collection=result_list,
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )
            c.facets = query['facets']
            c.search_facets = query['search_facets']
            c.page.items = result_list
        except SearchError, se:
            log.error('Dataset search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.search_facets = {}
            c.page = page_util.Page(collection=[])
        c.search_facets_limits = {}
        for facet in c.search_facets.keys():
            try:
                limit = int(request.params.get('_%s_limit' % facet,
                                               g.facets_default_number))
            except ValueError:
                abort(400, _('Parameter "{parameter_name}" is not '
                             'an integer').format(
                    parameter_name='_%s_limit' % facet
                ))
            c.search_facets_limits[facet] = limit

        maintain.deprecate_context_item(
            'facets',
            'Use `c.search_facets` instead.')

        self._setup_template_variables(context, {},
                                       package_type=package_type)

        return base.render('user/rdft_dashboard_datasets.html')

    def upload_package(self):
        package_type = 'dataset'
        context = {'user': c.user or c.author, 'auth_user_obj': c.userobj,
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
                   'add_delete': 'add_delete' in request.params,
                   'upload': 'upload' in request.params,}

        # Package needs to have a organization group in the call to
        # check_access and also to save it
        try:
            check_access('package_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        data = None
        id = TEST
        workdir = os.path.join(BASE_DIR, c.user)
        if os.path.exists(os.path.join(workdir, request.POST.get('file_path', 'nofile'))):
            id = os.path.join(workdir, request.POST.get('file_path', ''))

        if context['upload']:
            request.POST.pop('upload')
            file = request.POST.pop('resource_file_upload')
            data = data or  ecportal_logic.transform_to_data_dict(request.POST)
            data = self._safe_resource_upload(data, file)

        if context['save_locally'] and not data:
            request.POST.pop('save_locally')
            data = data or  ecportal_logic.transform_to_data_dict(request.POST)

            for package in data.get('dataset', []):
                package = get_action('validate_dataset')(context, package)
                if package.get('domains_eurovoc'):
                    groups = ingestion.get_groups_from_database_by_title(package.get('domains_eurovoc'))
                    package['groups'] = groups
                split_id = package['owner_org']
                if not data.get('organization'):
                    org = get_action('organization_show')(context,
                                                          {'id': split_id, 'include_datasets': 'false'})
                    package['organization'] = org
            self._create_temporary_files_for_packaging(context, data)
            return

        if context['add_rdf'] and not data:
            request.POST.pop('add_rdf')
            data = data or ecportal_logic.transform_to_data_dict(request.POST)
            tmp_list = data.get('dataset', [])
            tmp_list.append({'id': 'dew_dataset'})
            data['dataset'] = tmp_list

        if context['add_delete'] and not data:
            request.POST.pop('add_delete')
            data = data or ecportal_logic.transform_to_data_dict(request.POST)
            tmp_list = data.get('delete', [])
            tmp_list.append({'name': 'dew_delete_action'})
            data['delete'] = tmp_list

        if not data:
            data = {'dataset': [],
                    'manifest': [{}],
                    'files': [],
                    'delete': [],
                    'organization': {}
                    }

            if id:
                zf = ingestion.read_zip_file_content(id)

                for file in zf.namelist():
                    if '.xml' in file and '/files' not in file:
                        fileContent = zf.read(file)
                        simple_name = os.path.basename(os.path.splitext(file)[0])
                        manifest = ingestion.parse_xml_to_dict(fileContent)
                        data['manifest'] = [
                            {'publisher_uri': manifest.get('ecodp:manifest').get('@ecodp:publisher'),
                             'package_id': manifest.get('ecodp:manifest').get('@ecodp:package-id'),
                             'creation_date': manifest.get('ecodp:manifest').get(
                                 '@ecodp:creation-date-time')}]

                        action_list = []
                        for del_action in manifest.get('ecodp:manifest').get('ecodp:action'):
                            if del_action.get('ecodp:remove'):
                                action_list.append({'uri': del_action.get('@codp:object-uri'),
                                                    'name': del_action.get('@ecodp:object-ckan-name')})

                        data['delete'] = action_list

                for file in zf.namelist():
                    if '.rdf' in file and '/files' not in file:
                        rdf = {}
                        fileContent = zf.read(file)
                        simple_name = os.path.basename(os.path.splitext(file)[0])
                        rdf = ingestion.mapp_rdf2ckan_fields(fileContent)
                        split_id = rdf['owner_org'].split('/')
                        if not data.get('organization'):
                            org = get_action('organization_show')(context, {'id': split_id[-1].lower(),
                                                                            'include_datasets': 'false'})
                            data['organization'] = org
                        rdf['owner_org'] = org if org else rdf['owner_org']
                        rdf['id'] = simple_name

                        data['dataset'].append(rdf)
                        rdf['keywords'] = rdf.get('keyword_string', [])

                    elif '/files' in file and not file.endswith('/'):

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

        for package in data.get('dataset', []):
            if package.get('groups'):
                glist = []
                for value in package.get('groups'): glist.extend([result for result in value.values()])
                groups = ingestion.get_groups_from_database_by_title(glist)
                package['groups'] = groups

        for item in plugins.PluginImplementations(plugins.IPackageController):
            new_item = []
            for rdf in data['dataset']:
                new_item.append(item.before_view(rdf))
            data['dataset'] = new_item

        c.pkg_dict = data
        # for key, value in c.pkg_dict.get('datasets/EAC_Erasmus_mobility_statistics_2012_2013-odp.rdf').get('rdf:RDF').get('dcat:Dataset').iteritems():
        #    if 'dct:title' == key:
        #        new_lang = value.get('@xml:lang')
        #        new_text = value.get('#text')

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

    def _safe_resource_upload(self, data_dict, file):
        zip_name = data_dict['manifest'][0].get('package_id')
        try:
            if not os.path.isdir(os.path.join(WORKDIR, zip_name)): os.makedirs(os.path.join(WORKDIR, zip_name))
            if not os.path.isdir(os.path.join(WORKDIR + '/' + zip_name, 'dataset')): os.makedirs(os.path.join(WORKDIR + '/' + zip_name, 'dataset'))
            path = os.path.join(WORKDIR + '/' + zip_name, 'dataset/files')
            if not os.path.isdir(path): os.makedirs(path)
            stream = file
            label = file.filename

            file = open('%s/%s' % (path, label), 'w')
            file.write(stream.file.read())

            files = data_dict.get('files',[])
            files.append({'local_path': path,
                          'path': '%s/%s' % ('dataset/files', label),
                          'name': label})

        except Exception, e:
            import traceback
            log.error(traceback.print_exc())
        finally:
            file.close()

        return data_dict


    def _create_temporary_files_for_packaging(self, context, data):
        zip_name = data['manifest'][0].get('package_id')
        data['organization'] = get_action('organization_show')(context,
                                                               {'id': data['manifest'][0].get('publisher'),
                                                                'include_datasets': 'false'})
        #data['organization'] =  [{'name': value['name']} for value in data['list']]
        try:
            os.makedirs(os.path.join(WORKDIR, zip_name))
            os.makedirs(os.path.join(WORKDIR + '/' + zip_name, 'dataset'))
            context['format'] = 'xml'
            new_fiel = dataset.create_rdf_from_data_dict(context, data)
            file = open('%s/%s/manifest.xml' % (WORKDIR, zip_name), 'w')
            file.write(new_fiel)
            file.close()

            for value in data.get('dataset', []):
                context['format'] = 'rdf'
                new_fiel = dataset.create_rdf_from_data_dict(context, value)
                file = open('%s/%s/dataset/%s.rdf' % (WORKDIR, zip_name, value.get('name')), 'w')
                file.write(new_fiel)
                file.close()

            os.makedirs(os.path.join(WORKDIR + '/' + zip_name, 'dataset/files'))
            for file in data.get('files'):
                # if not os.path.join(WORKDIR+'/'+zip_name,'dataset/files'): os.makedirs(os.path.join(WORKDIR+'/'+zip_name,'dataset/files'))
                if not file.get('local_path') == os.path.join(WORKDIR + '/' + zip_name, 'dataset/files'):
                    shutil.copy2(file.get('local_path'), os.path.join(WORKDIR + '/' + zip_name, 'dataset/files'))

            ingestion.zip_temp_ingestion_package_folder(os.path.join(WORKDIR, zip_name), '%s.zip' % zip_name)
            zip_file = '%s.zip' % zip_name
            if os.path.isfile(zip_file):
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(zip_file)
                with open(zip_file, 'r') as f:
                    shutil.copyfileobj(f, base.response)
                base.response.headers['Content-Length'] = size
                base.response.headers['Content-type'] = 'application/zip'
                return
        except Exception, e:
            import traceback
            log.error(traceback.print_exc())
        finally:
            shutil.rmtree(os.path.join(WORKDIR, zip_name))

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

    def get_deleted_datasets_filtered(self):
        # TODO: this was the code to retrive the deleted datasets
        # Query result is a list of tuples, each tuple contains only the dataset id as elements
        deleted_datasets = ckan.model.Session.query(Package). \
            join(Group, Group.id == Package.owner_org). \
            filter(Package.state == 'deleted'). \
            join(Member, Member.group_id == Group.id). \
            filter(Member.table_name == 'user'). \
            join(User, User.id == Member.table_id). \
            filter(User.name == c.user).all()

        # Adapt deleted datasets representation anf filter if needed
        adapted_deleted_datasets = []
        for ds in deleted_datasets:
            ds_dict = model_dictize.package_dictize(ds, {'model': ckan.model})

            # Add missing properties to circumvent access errors / emtpy fields in thr Jinja templates
            if not ds_dict.get('tracking_summary', None):
                ds_dict['tracking_summary'] = {'total': 0}
            if not ds_dict.get('description', None):
                ds_dict['description'] = ds.notes

            adapted_deleted_datasets.append(ds_dict)

        # Only keep datasets matching the criteria
        adapted_filtered_deleted_datasets = []
        for ds in adapted_deleted_datasets:
            ds_title = ds.get('title', '')
            if c.q != u'':
                search = c.q.strip().split(' ')
                if request.params.get('ext_boolean') == 'any':
                    if any([token in ds_title for token in search]):
                        adapted_filtered_deleted_datasets.append(ds)
                elif request.params.get('ext_boolean') == 'all':
                    if all([token in ds_title for token in search]):
                        adapted_filtered_deleted_datasets.append(ds)
                elif request.params.get('ext_boolean') == 'exact':
                    if " ".join(search) == ds_title:
                        adapted_filtered_deleted_datasets.append(ds)
            else:
                adapted_filtered_deleted_datasets.append(ds)

        log.debug("MDT: Deleted datasets adapted and filtered")
        return adapted_filtered_deleted_datasets

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

    def _setup_user_template_variables(self, context, data_dict):
        c.is_sysadmin = new_authz.is_sysadmin(c.user)
        try:
            user_dict = get_action('user_show')(context, data_dict)
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        contact_info = Package_contact_info.get_by_user(user_dict.get('id', ''))
        if contact_info:
            info_dict = contact_info.as_dict()
            user_dict.update(info_dict)
        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])

    def _package_form(self, package_type=None):
        log.debug(str(package_type) + " / " +
                  str(lookup_package_plugin(package_type)) + " / " +
                  str(lookup_package_plugin(package_type).package_form()))
        if package_type == 'ingestion_package':
            return 'user/manage_package_form.html'
        elif package_type == 'upload_package':
            return 'user/upload_package_form.html'

        return lookup_package_plugin(package_type).package_form()



        # def __transform_to_data_dict(self, reqest_post):
        #     '''
        #     Transform the POST body to data_dict usable by the actions ('package_update', 'package_create', ...)
        #     :param the POST body of the request object
        #     :return: a dict usable by the actions
        #     '''
        #
        #     # Initialize params dictionary
        #     data_dict = logic.parse_params(reqest_post)
        #
        #     for key in data_dict.keys():
        #         if 'template' in key:
        #             data_dict.pop(key, None)
        #
        #     # Transform keys like 'group__0__key' to a tuple (like resources, extra fields, ...)
        #     try:
        #         data_dict = logic.tuplize_dict(data_dict)
        #     except Exception, e:
        #         import traceback
        #         log.error(traceback.print_exc())
        #
        #     # Collect all tuplized key groups in one key containing a list of dicts
        #     data_dict = dict_func.unflatten(data_dict)
        #     data_dict = logic.clean_dict(data_dict)
        #
        #     return data_dict
