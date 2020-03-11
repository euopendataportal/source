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
import time
import pickle

import ckan.plugins.toolkit as tk
import ckan.lib.base as base
import ckan.lib.navl.dictization_functions
import ckan.logic as logic
import ckan.plugins as plugins
import sqlalchemy
from ckan.common import json
from ckan.lib.search.common import make_connection, SearchError
from pylons import config
from solr import SolrException

check_access = logic.check_access
render = base.render
abort = base.abort
redirect = base.redirect
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

log = logging.getLogger(__name__)
_validate = ckan.lib.navl.dictization_functions.validate
_check_access = logic.check_access
_and_ = sqlalchemy.and_

QUERY_FIELDS = "name^4 title^4 tags^2 groups^2 text"

@logic.side_effect_free
def custom_package_search(context, data_dict):
    '''
    Searches for packages satisfying a given search criteria.

    This action accepts also group parameter for solr search query
    for details see:
    https://cwiki.apache.org/confluence/display/solr/Result+Grouping

    The result dict is left quite raw to let the caller handle
    the grouped result.

    This action is NOT supplied to the REST API

    This action accepts a *subset* of solr's search query parameters:


    :param q: the solr query.  Optional.  Default: `"*:*"`
    :type q: string
    :param fq: any filter queries to apply.  Note: `+site_id:{ckan_site_id}`
        is added to this string prior to the query being executed.
    :type fq: string
    :param sort: sorting of the search results.  Optional.  Default:
        'relevance asc, modified_date desc'.  As per the solr
        documentation, this is a comma-separated string of field names and
        sort-orderings.
    :type sort: string
    :param rows: the number of matching rows to return.
    :type rows: int
    :param start: the offset in the complete result for where the set of
        returned datasets should begin.
    :type start: int
    :param facet: whether to enable faceted results.  Default: "true".
    :type facet: string
    :param facet.mincount: the minimum counts for facet fields should be
        included in the results.
    :type facet.mincount: int
    :param facet.limit: the maximum number of values the facet fields return.
        A negative value means unlimited. This can be set instance-wide with
        the :ref:`search.facets.limit` config option. Default is 50.
    :type facet.limit: int
    :param facet.field: the fields to facet upon.  Default empty.  If empty,
        then the returned facet information is empty.
    :type facet.field: list of strings


    The following advanced Solr parameters are supported as well. Note that
    some of these are only available on particular Solr versions. See Solr's
    `dismax`_ and `edismax`_ documentation for further details on them:

    ``qf``, ``wt``, ``bf``, ``boost``, ``tie``, ``defType``, ``mm``


    .. _dismax: http://wiki.apache.org/solr/DisMaxQParserPlugin
    .. _edismax: http://wiki.apache.org/solr/ExtendedDisMax


    **Results:**

    The result of this action is a dict with the following keys:

    :rtype: A dictionary with the following keys
    :param count: the number of results found.  Note, this is the total number
        of results found, not the total number of results returned (which is
        affected by limit and row parameters used in the input).
    :type count: int
    :param grouped: dict of the result groups, every group contains paramter 'matches' which is the overall count of all groups,
            'doclist' is a dict that specifes the results in this group
    :type results: list of dictized datasets.
    :param facets: DEPRECATED.  Aggregated information about facet counts.
    :type facets: DEPRECATED dict
    :param search_facets: aggregated information about facet counts.  The outer
        dict is keyed by the facet field name (as used in the search query).
        Each entry of the outer dict is itself a dict, with a "title" key, and
        an "items" key.  The "items" key's value is a list of dicts, each with
        "count", "display_name" and "name" entries.  The display_name is a
        form of the name that can be used in titles.
    :type search_facets: nested dict of dicts.
    :param use_default_schema: use default package schema instead of
        a custom schema defined with an IDatasetForm plugin (default: False)
    :type use_default_schema: bool

    An example result: ::

     'grouped' : {
		'-organization:estat AND -organization:comp' : {
			'matches' : 7801,
			'doclist' : {
				'start' : 0,
				'numFound' : 1701,
				'docs' : [{'id': 'cfd3654c-06b7-400a-adf0-bb0733ce2172',
				    'validated_data_dict' : '{ --dict with dataset metadata--
				    }
				}]
			}
		}

    **Limitations:**

    The full solr query language is not exposed, including.

    fl
        The parameter that controls which fields are returned in the solr
        query cannot be changed.  CKAN always returns the matched datasets as
        dictionary objects.
    '''
    # sometimes context['schema'] is None
    schema = (context.get('schema') or
              logic.schema.default_package_search_schema())
    data_dict, errors = _validate(data_dict, schema, context)
    # put the extras back into the data_dict so that the search can
    # report needless parameters
    data_dict.update(data_dict.get('__extras', {}))
    data_dict.pop('__extras', None)
    if errors:
        raise ValidationError(errors)

    model = context['model']
    session = context['session']

    _check_access('package_search', context, data_dict)
    locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
    # Move ext_ params to extras and remove them from the root of the search
    # params, so they don't cause and error
    data_dict['extras'] = data_dict.get('extras', {})
    for key in [key for key in data_dict.keys() if key.startswith('ext_')]:
        data_dict['extras'][key] = data_dict.pop(key)

    # check if some extension needs to modify the search params
    for item in plugins.PluginImplementations(plugins.IPackageController):
        try:
            data_dict = item.before_search(data_dict)
        except Exception as e:
            log.error(e)
            abort = True

    # the extension may have decided that it is not necessary to perform
    # the query
    abort = data_dict.get('abort_search', False)

    if data_dict.get('sort') in (None, 'rank'):
        data_dict['sort'] = 'score desc, modified_date desc'

    results = {}
    if not abort:
        data_source = 'data_dict' if data_dict.get('use_default_schema',
                                                   False) else 'validated_data_dict'

        # return a list of package ids
        # data_dict['fl'] = 'id {0}'.format(data_source)

        data_dict['fl'] = 'id name notes title resource_list views_total res_format title_{0} text_{0} modified_date capacity'.format((locale))

        # If this query hasn't come from a controller that has set this flag
        # then we should remove any mention of capacity from the fq and
        # instead set it to only retrieve public datasets
        fq = data_dict.get('fq', '')
        if not context.get('ignore_capacity_check', False):
            fq = ' '.join(p for p in fq.split(' ')
                          if not 'capacity:' in p)
            data_dict['fq'] = fq + ' capacity:"public"'

        # Pop these ones as Solr does not need them
        # changed this for creatig the right query for solr
        # extras = data_dict.pop('extras', None)

        # query = search.query_for(model.Package)
        start_time = time.time()
        response = _run(data_dict)
        duration = time.time() - start_time
        log.info("Custom query execution took {0}".format(duration))
        count = response['count']
        facets = response['facets']
    else:
        count = 0
        facets = {}
        results = []

    search_results = {
        'count': count,
        'facets': facets,
        'results': results,
        'groups': response['response'],
        'sort': data_dict['sort']
    }

    # separate eurovoc_domains from groups
    if facets != {}:
        groups_list = {}
        eurovoc_domains_list = {}
        for key, value in facets['groups'].items():
            group = model.Group.get(key)
            if group:
                if group.type == 'eurovoc_domain':
                    eurovoc_domains_list[key] = value
                else:
                    groups_list[key] = value

        facets['eurovoc_domains'] = eurovoc_domains_list;
        facets['groups'] = groups_list;

    # Transform facets into a more useful data structure.
    restructured_facets = {}
    for key, value in facets.items():
        restructured_facets[key] = {
            'title': key,
            'items': []
        }
        for key_, value_ in value.items():
            new_facet_dict = {}
            new_facet_dict['name'] = key_
            if key in ('eurovoc_domains', 'groups', 'organization'):
                group = model.Group.get(key_)
                if group:
                    new_facet_dict['display_name'] = group.display_name
                else:
                    new_facet_dict['display_name'] = key_
            elif key == 'license_id':
                license = model.Package.get_license_register().get(key_)
                if license:
                    new_facet_dict['display_name'] = license.title
                else:
                    new_facet_dict['display_name'] = key_
            else:
                new_facet_dict['display_name'] = key_
            new_facet_dict['count'] = value_
            restructured_facets[key]['items'].append(new_facet_dict)
    search_results['search_facets'] = restructured_facets

    # check if some extension needs to modify the search results
    for item in plugins.PluginImplementations(plugins.IPackageController):
        search_results = item.after_search(search_results, data_dict)

    # After extensions have had a chance to modify the facets, sort them by
    # display name.
    for facet in search_results['search_facets']:
        search_results['search_facets'][facet]['items'] = sorted(
            search_results['search_facets'][facet]['items'],
            key=lambda facet: facet['display_name'], reverse=True)

    return search_results


def _run(query):
    '''
    Custom final preparation of the solr query
    and call to the solr api.

    :param query:
    :return:
    '''

    # default query is to return all documents
    q = query.get('q')
    if not q or q == '""' or q == "''":
        query['q'] = "*:*"

    # number of results
    rows_to_return = query.get('rows', 0)
    if rows_to_return > 0:
        # #1683 Work around problem of last result being out of order
        #       in SOLR 1.4
        rows_to_query = rows_to_return + 1
    else:
        rows_to_query = rows_to_return
    query['rows'] = rows_to_query

    # show only results from this CKAN instance
    fq = query.get('fq', '')
    if not '+site_id:' in fq:
        fq += ' +site_id:"%s"' % config.get('ckan.site_id')

    # filter for package status
    if not '+state:' in fq:
        fq += " +state:active"
    query['fq'] = [fq]

    fq_list = query.get('fq_list', [])
    query['fq'].extend(fq_list)

    # faceting
    query['facet'] = query.get('facet', 'true')
    query['facet.limit'] = query.get('facet.limit', config.get('search.facets.limit', '50'))
    query['facet.mincount'] = query.get('facet.mincount', 1)

    # return the package ID and search scores
    query['fl'] = query.get('fl', 'name')

    # return results as json encoded string
    query['wt'] = query.get('wt', 'json')

    # If the query has a colon in it then consider it a fielded search and do use dismax.
    defType = query.get('defType', 'dismax')

    boolean = query.get('extras', {}).get('ext_boolean', 'all')
    if boolean not in ['all', 'any', 'exact']:
        log.error('Ignoring unknown boolean search operator %r'
                  % (boolean,))
        boolean = 'all'

    if ':' not in query['q']:
        query['defType'] = 'dismax'
        query['tie'] = '0.1'
        if boolean == 'any':
            query['mm'] = '0'
        elif boolean == 'all':
            query['mm'] = '100%'
        elif boolean == 'exact':
            query['q'] = '"' + q.replace('"', '\\"') + '"'
        query['qf'] = query.get('qf', QUERY_FIELDS)

    conn = make_connection()
    log.info('Package query: %r' % query)
    try:
        start_time = time.time()
        solr_response = conn.raw_query(**query)
        duration = time.time() - start_time
        log.info("Solr returned the resilt after {0}".format(duration))
    except SolrException, e:
        raise SearchError('SOLR returned an error running query: %r Error: %r' %
                          (query, e.reason))
    response = {'query': query,
                'result': []
                }
    try:
        data = json.loads(solr_response)
        response['response'] = data['grouped']

        response['count'] = response['response'].itervalues().next().get('matches', 0)

        # get any extras and add to 'extras' dict
        for result in response['result']:
            extra_keys = filter(lambda x: x.startswith('extras_'), result.keys())
            extras = {}
            for extra_key in extra_keys:
                value = result.pop(extra_key)
                extras[extra_key[len('extras_'):]] = value
            if extra_keys:
                result['extras'] = extras

        # get facets and convert facets list to a dict
        response['facets'] = data.get('facet_counts', {}).get('facet_fields', {})
        for field, values in response['facets'].iteritems():
            response['facets'][field] = dict(zip(values[0::2], values[1::2]))
    except Exception, e:
        log.exception(e)
        raise SearchError(e)
    finally:
        conn.close()

    return response


def check_solr_result(context, source_list, limit):
    '''
    Encapsulate the check if a dataset returned by solr really exists in
    CKAN database

    :param context:
    :param source_list:
    :param limit:
    :return:
    '''
    results = []
    data_source = 'validated_data_dict'
    count = 0
    locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
    if context.get('for_view', False):
        for package in source_list:

            try:
                package['resources'] = [json.loads(res) for res in package.get('resource_list', []) if res]
            except Exception as e:
                log.error(e.message, e)

                if locale != 'en' and package.get('title_{0}'.format(locale),''):
                    package['title'] = package.get('title_{0}'.format(locale))
                if locale != 'en' and package.get('text_{0}'.format(locale),''):
                    package['notes'] = package.get('text_{0}'.format(locale))
            # if context.get('for_view'):
            #     for item in plugins.PluginImplementations(plugins.IPackageController):
            #         package = item.before_view(package)

            # for resource in package.get('resources', []):
            #     input_list = int(resource.get('download_total_resource','') or '0')

            input_list = [int(resource.get('download_total_resource','') or '0') for resource in package.get('resources', []) ]
            if not input_list:
                input_list = [0]

            download_count = reduce(lambda x, y: x + y, input_list)
            package['download_total'] = download_count

            results.append(package)
            count += 1

            if count == limit:
                break
    else:
        for package in source_list:
            try:

                package = logic.get_action('package_show')(context, {'id': package['name']})
            except Exception as e:
                log.error(e.message, e)

            results.append(package)
            count += 1

            if count == limit:
                break



    return results
