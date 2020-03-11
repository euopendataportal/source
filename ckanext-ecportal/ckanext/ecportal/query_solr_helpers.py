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
import ckan.model as model
import cPickle as cPickle
import ckan.logic as logic
import ckanext.ecportal.lib.cache.redis_cache as redis
import ckan.lib.helpers as h
import ckan.plugins as plugins
import ckan.lib.base as base
import ckanext.ecportal.lib.page_util as page_util
from urllib import urlencode
from ckan.common import OrderedDict, request, c, _
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

log = logging.getLogger(__name__)

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': CKAN_PATH + '/var/cache',
    'cache.lock_dir': CKAN_PATH + '/var/cache'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))
get_action = logic.get_action
abort = base.abort


def get_checkbox_query(q, checkbox):
    """
    :param checkbox: 'all' - 'any' or 'exact'
    :param q: query str solr
    :return: a concatenate string of query string for checkbox
    """
    if q:
        q_tab = q.split(' ')
        if checkbox == 'all':
            return '(' + ' AND '.join(q_tab) + ')'
        elif checkbox == 'any':
            return '(' + ' OR '.join(q_tab) + ')'
        elif checkbox == 'exact':
            return '"' + q + '"'
        else:
            return q
    else:
        return q


def get_filter_fields(params):
    """
    :param params: list of tuples (param, value)
    :return: fields for filter box
    """
    fields = []
    for (param, value) in params:
        if param not in ['q', 'page', 'sort'] and len(value) and not param.startswith('_'):
            if not param.startswith('ext_'):
                fields.append((param, value))
    return fields


def concat_query_with_fields(q, fields):
    """
    :param q: query string for SolR search
    :param fields: fields of the filter box
    :return: the updated query string with the fields of the filter box
    """
    new_q = q
    for(param, value) in fields:
        new_q += ' %s:"%s"' % (param, value)
    return new_q


def initialize_query():
    """
    Get parameters from the request and build a query_dict. This dict can be used to set the context of a
    controller and make a solr query.
    :return: query_dict = {
                'q': query str
                'facet_titles': names of the different facets
                'sort_by_selected': the sort parameter selected by the user
                'params_nopage': all parameters except page
                'page': number of the current page
            }
    """
    q = request.params.get('q', '')
    q = get_checkbox_query(q, request.params.get('ext_boolean'))
    fields = get_filter_fields(request.params.items())
    q = concat_query_with_fields(q, fields)
    page = get_page_number_from_request()
    # Most search operations should reset the page counter
    params_no_page = [(k, v) for k, v in request.params.items() if k != 'page']

    query_dict = {'q': q,
                  'facet_titles': get_facets(),
                  'fields': fields,
                  'sort_by_selected': request.params.get('sort', None),
                  'params_no_page': params_no_page,
                  'page': page}

    return query_dict


def execute_query(active_cache, query_dict, user):
    """
    Execute the SolR query. Get (or Set) the response from the cache if activated.
    :param active_cache: == 'true' if cache is activated (from config)
    :param query_dict: represents a SolR dict to execute a query
    :param user: c.user or c.author
    :return: query response from SolR
    """
    context = {'model': model,
               'session': model.Session,
               'user': user,
               'for_view': True,
               'extras_as_string': True,
               'return_query': True}



    query = get_action('package_search')(context, query_dict)

    return query


def get_facets():
    """
    :return: OrderedDict with facets to display
    """
    facets = OrderedDict()
    for plugin in plugins.PluginImplementations(plugins.IFacets):
        facets = plugin.dataset_facets(facets, None)
    return facets


def get_page_number_from_request():
    """
    :return: request page number (int)
    """
    try:
        page = int(request.params.get('page', 1))
        return page
    except ValueError:
        abort(400, '"page" parameter must be an integer')


def treat_search_error_exception(error_msg, se):
    log.error(error_msg + ': %r', se.args)
    c.query_error = True
    c.facets = {}
    c.page = page_util.Page(collection=[])
    c.search_url_params = ''


@cache.cache('search_url', expire=3600)
def search_url(params):
    url = h.url_for(controller=c.controller, action='read', id=c.id)
    return url + u'?' + urlencode(params)


@cache.cache('drill_down_url', expire=3600)
def drill_down_url(**by):
    return h.add_url_param(alternative_url=None, controller=c.controller, action='read',
                           extras=dict(id=c.id), new_params=by)


def remove_field(key, value=None, replace=None):
    return h.remove_url_param(key, value=value, replace=replace, controller=c.controller, action='read',
                              extras=dict(id=c.id))


def pager_url(q=None, page=None):
    params = list(c.params_no_page)
    params.append(('page', c.page.page))
    return search_url(params)


def update_template_ctx_before_query(query_dict):
    c.remove_field = remove_field
    c.sort_by_selected = query_dict.get('sort_by_selected')
    c.facet_titles = query_dict.get('facet_titles')
    c.fields = query_dict.get('fields')
    c.params_no_page = query_dict.get('params_no_page')
    c.num_page = query_dict.get('page')


def update_template_ctx_after_query(query_res, page_limit=20, facets_default_number=10):
    c.page = page_util.Page(collection=query_res['results'], page=c.num_page, url=pager_url,
                            item_count=query_res['count'], items_per_page=page_limit)
    c.page.items = query_res['results']
    # Compute limit for displaying facets #
    c.facets = query_res['facets']
    c.search_facets = query_res['search_facets']
    c.search_facets_limits = {}
    for facet in c.facets.keys():
        try:
            limit = int(request.params.get('_%s_limit' % facet, facets_default_number))
            c.search_facets_limits[facet] = limit
        except ValueError:
            abort(400, _('Parameter "{param}" is not an integer').format(param='_%s_limit' % facet))
