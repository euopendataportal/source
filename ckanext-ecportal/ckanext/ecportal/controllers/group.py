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

from urllib import urlencode

import ckan.lib.helpers as h
import ckan.lib.maintain as maintain
import ckan.lib.search as search
import ckan.model as model
import ckan.new_authz as new_authz
import ckan.plugins as plugins
import ckanext.ecportal.lib.page_util as page_util
import ckan.lib.base as base
import ckan.plugins.toolkit as tk
import time
#import pickle
import ujson as pickle
import ckanext.ecportal.lib.cache.redis_cache as redis

from ckan.common import OrderedDict, c, g, request, _
from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
from pylons import config
from ckan.controllers.group import GroupController
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

import ckan.logic as logic
get_action = logic.get_action

import ckan.lib.base as base
abort = base.abort
NotFound = logic.NotFound

import logging
log = logging.getLogger(__name__)

NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': CKAN_PATH + '/var/cache',
    'cache.lock_dir': CKAN_PATH + '/var/cache'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring)
            else str(v))
            for k, v in params]

amount_group_displayed = int(config.get('amount_group_displayed', 21))
amount_catalog_displayed = int(config.get('amouont_catalog_displayed', 21))


class ECODPGroupController(GroupController):


    def index(self):
        start = time.time()
        group_type = self._guess_group_type()
        language = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        q = c.q = request.params.get('q', '')
        data_dict = {'all_fields': True, 'q': q}
        sort_by = c.sort_by_selected = request.params.get('sort')
        if sort_by:
            data_dict['sort'] = sort_by
        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin

        results = self._action('group_list')(context, data_dict)

        c.amount_group_displayed = amount_group_displayed

        c.groups = results[:amount_group_displayed]
        c.hasmoregroups = len(results) > amount_group_displayed
        c.themes = self._action('theme_list')(context, {})
        c.catalogs = CatalogDcatApOp.get_ui_list_catalogs(config.get('ckan.locale_default', 'en'))
        c.amount_catalog_displayed = amount_catalog_displayed

        #c.page = h.Page(
        #    collection=results,
        #    page=request.params.get('page', 1),
        #    url=h.pager_url,
        #    items_per_page=21
        #)
        # @cache.cache('cached_render', expire=3600)
        def cached_render(user, languge, group_type):
            _render = base.render(group_type)
            return _render
        start_render = time.time()
        _render = cached_render(context.get('user'), language, self._index_template(group_type))

        duration_render= time.time() - start_render
        log.info("Duration index  render. {0}".format(duration_render))
        duration = time.time() - start
        log.info("Duration index. {0}".format(duration))
        return _render

    def read(self, id, limit=20):

        start = time.time()
        if request.GET.get('ext_boolean') in ['all', 'any', 'exact']:
            base.session['ext_boolean'] = request.GET['ext_boolean']
            base.session.save()
        language = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')

        group_type = self._get_group_type(id.split('@')[0])
        if (group_type != self.group_type) and (group_type != "eurovoc_domain"):
            abort(404, _('Incorrect group type'))

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True}
        # Do not query for the group datasets when dictizing, as they will
        # be ignored and get requested on the controller anyway
        data_dict = {'id': id, 'include_datasets': False}

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', '')

        try:
            stratqs = time.time()
            if 'eurovoc_domain' in data_dict.get('id','') :
                raise NotFound('EurovocDomains are not available any more')
            result = self._action('group_show_read')(context, data_dict)
            c.group_dict = result.get('group_dict', None)
            context["group"] = result.get('group')
            durationgs = time.time() - stratqs
            log.info("Duration group show read. {0}".format(durationgs))
            c.group = context['group']
        except NotFound:
            abort(404, _('Group not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read group %s') % id)

        self._read(id, limit)

        start_render = time.time()

        # @cache.cache('render_cached_read', expire=3600)
        def render_cached(user, id, language,  group_type):
            _render = base.render(self._read_template(c.group_dict['type']))
            return _render

        _render = render_cached(context.get('user'), id, language, c.group_dict['type'])
        duration_render = time.time() - start_render



        # _render = base.render(self._read_template(c.group_dict['type']))
        duration = time.time() - start
        log.info("Duration read_group. {0}".format(duration))
        return _render

    def _read(self, id, limit=20):
        import  time
        language = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        start = time.time()
        ''' This is common code used by both read and bulk_process'''
        group_type = self._get_group_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        q = c.q = request.params.get('q', '')
        # Search within group

        if q != u'':
            qTab = q.split(' ')
            checkbox = request.params.get('ext_boolean')
            if checkbox == 'all':
                q = '(' + ' AND '.join(qTab) + ')'
            elif checkbox == 'any':
                q = '(' + ' OR '.join(qTab) + ')'
            else: #checkbox == 'exact'
                q = '"' + q + '"'

        c.description_formatted = h.render_markdown(c.group_dict.get('description'))

        context['return_query'] = True

        # c.group_admins is used by CKAN's legacy (Genshi) templates only,
        # if we drop support for those then we can delete this line.
        c.group_admins = new_authz.get_group_or_org_admin_ids(c.group.id)

        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        new_params_nopage = []
        for key, value in params_nopage:
            if key == 'eurovoc_domains':
                new_params_nopage.append(('groups', value))
            else:
                new_params_nopage.append((key,value))

        params_nopage = new_params_nopage

        #sort_by = request.params.get('sort', 'name asc')
        sort_by = request.params.get('sort', None)

        @cache.cache('search_url', expire=3600)
        def search_url(params):
            if group_type == 'organization':
                if c.action == 'bulk_process':
                    url = self._url_for(controller='organization',
                                        action='bulk_process',
                                        id=id)
                else:
                    url = self._url_for(controller='organization',
                                        action='read',
                                        id=id)
            else:
                url = self._url_for(controller='group', action='read', id=id)
            params = [(k, v.encode('utf-8') if isinstance(v, basestring)
                       else str(v)) for k, v in params]
            return url + u'?' + urlencode(params)

        @cache.cache('drill_down_url', expire=3600)
        def drill_down_url(**by):
            return h.add_url_param(alternative_url=None,
                                   controller='group', action='read',
                                   extras=dict(id=c.group_dict.get('name')),
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            if c.group_dict.get('is_organization'):
                return h.remove_url_param(key, value=value, replace=replace,
                                      controller='organization', action='read',
                                      extras=dict(id=c.group_dict.get('id')))
            else:
                return h.remove_url_param(key, value=value, replace=replace,
                                      controller='group', action='read',
                                      extras=dict(id=c.group_dict.get('name')))

        c.remove_field = remove_field

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            c.fields = []
            search_extras = {}
            for (param, value) in request.params.items():
                if not param in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        param = 'eurovoc_domains' if (param == 'eurovoc_domains') else param;
                        q += ' %s:"%s"' % (param, value)
                    else:
                        search_extras[param] = value

            fq = ''
            if c.group_dict.get('is_organization'):
                q += ' owner_org:"%s"' % c.group_dict.get('id')
            elif c.group_dict.get('name') not in q:
                q += ' groups:"%s"' % c.group_dict.get('name')

            fq = fq + ' capacity:"public"'
            user_member_of_orgs = [org['id'] for org
                                   in h.organizations_available('read')]
            if (c.group and c.group.id in user_member_of_orgs):
                fq = ''
                context['ignore_capacity_check'] = True

            facets = OrderedDict()

            default_facet_titles = {'organization': _('Organizations'),
                                    'groups': _('Groups'),
                                    'tags': _('Tags'),
                                    'res_format': _('Formats'),
                                    'license_id': _('Licenses')}

            for facet in g.facets:
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Facet titles
            for plugin in plugins.PluginImplementations(plugins.IFacets):
                if self.group_type == 'organization':
                    facets = plugin.organization_facets(
                        facets, self.group_type, None)
                else:
                    facets = plugin.group_facets(
                        facets, self.group_type, None)

            if 'capacity' in facets and (self.group_type != 'organization' or
                                         not user_member_of_orgs):
                del facets['capacity']

            c.facet_titles = facets

            data_dict = {
                'q': q,
                'fq': fq,
                'facet.field': facets.keys(),
                'rows': limit,
                'sort': sort_by,
                'start': (page - 1) * limit,
                'extras': search_extras,
                'defType': 'edismax'
            }

            active_cache = config.get('ckan.cache.active', 'false')

            context_ = dict((k, v) for (k, v) in context.items() if k != 'schema')

            has_result = False
            dict_as_pickle = None

            if active_cache == 'true':
                dict_as_pickle = pickle.dumps(data_dict)
                query_json = redis.get_from_cache(dict_as_pickle, pool=redis.MISC_POOL)
                if query_json:
                    query = pickle.loads(query_json)
                    has_result = True

            if has_result == False:
                query = get_action('package_search')(context_, data_dict)
                if active_cache == 'true':
                    redis.set_value_in_cache(dict_as_pickle, pickle.dumps(query), pool=redis.MISC_POOL)


            c.search_url_params = urlencode(_encode_params(params_nopage))
            c.page = page_util.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )

            c.group_dict['package_count'] = query['count']
            c.facets = query['facets']
            #maintain.deprecate_context_item('facets', 'Use `c.search_facets` instead.')

            c.search_facets = query['search_facets']
            c.search_facets_limits = {}
            for facet in c.facets.keys():
                limit = int(request.params.get('_%s_limit' % facet,
                                               g.facets_default_number))
                c.search_facets_limits[facet] = limit
            c.page.items = query['results']

            c.sort_by_selected = sort_by
            duration = time.time() - start
            log.info("Duration _read. {0}".format(duration))


        except search.SearchError, se:
            log.error('Group search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.page = page_util.Page(collection=[])
            c.search_url_params = ''
        except ValueError, se:
            log.error('Group search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.page = page_util.Page(collection=[])
            c.search_url_params = ''

        self._setup_template_variables(context, {'id':id},
            group_type=group_type)

    def edit(self, id, data=None, errors=None, error_summary=None):
        import ckan.lib.base as base
        group_type = self._get_group_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'save': 'save' in request.params,
                   'for_edit': True,
                   'parent': request.params.get('parent', None)
                   }
        data_dict = {'id': id}
        data_dict['include_datasets'] = False

        if context['save'] and not data:
            return self._save_edit(id, context)

        try:
            old_data = self._action('group_show')(context, data_dict)
            c.grouptitle = old_data.get('title')
            c.groupname = old_data.get('name')
            data = data or old_data
        except NotFound:
            abort(404, _('Group not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read group %s') % '')

        group = context.get("group")
        c.group = group
        c.group_dict = self._action('group_show')(context, data_dict)

        try:
            self._check_access('group_update', context)
        except NotAuthorized, e:
            abort(401, _('User %r not authorized to edit %s') % (c.user.encode('ascii','ignore'), id))

        errors = errors or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'edit'}

        self._setup_template_variables(context, data, group_type=group_type)
        c.form = base.render(self._group_form(group_type), extra_vars=vars)
        return base.render(self._edit_template(c.group.type))