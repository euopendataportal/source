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

"""
This file was taken from the CKAN core and will be adapted to the needs of the RSS/Atom feed feature of the
ECPortal extension

This file combines contents coming from:
 * ``ckan/controllers/feed.py`` produces Atom feeds of datasets (datasets belonging to a particular group,
    datasets tagged with a particular tag, datasets that match an arbitrary search)
 * ``ckan/controllers/package.py`` provides an atom feed of a dataset's revision history.

Other possible feed functionality not yet included resides in:
 * ``ckan/controllers/group.py`` provides an atom feed of a group's revision history.
 * ``ckan/controllers/revision.py`` provides an atom feed of the repository's revision history.
"""

import logging
import urlparse
import datetime
import time

import webhelpers.feedgenerator
from pylons import config


import ckan.logic as logic
import ckan.plugins as plugins
import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.lib.i18n as i18n
import ckan.lib.search as search
import ckan.plugins as p
import urllib as url
import ujson as json
import ckanext.ecportal.action.customsearch as customsearch
import ckan.lib.plugins as lookup_plugin
import ckanext.ecportal.lib.cache.redis_cache as cache
import ckan.lib.navl.dictization_functions as dictization_functions

from ckan.lib.search.common import  SearchError
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.action.revision import diff_datasets
from ckanext.ecportal.model.schemas.dcatapop_kind_schema import KindSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric

import ckanext.ecportal.helpers as ckanext_helpers
import ckanext.ecportal.lib.ui_util as ui_util
import ckan.plugins.toolkit as tk
import ckanext.ecportal.lib.controlled_vocabulary_util as nal_util
import ckanext.ecportal.lib.cache.redis_cache as redis_cache
import cPickle as pickle

from ckan.common import _, g, c, request, response

# TODO make the item list configurable
ITEMS_LIMIT = 20


log = logging.getLogger(__name__)

render = base.render
abort = base.abort

_validate = dictization_functions.validate
_check_access = logic.check_access
ValidationError = logic.ValidationError
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
get_action = logic.get_action



def _package_search(data_dict):
    """
    Helper method that wraps the package_search action.

     * unless overridden, sorts results by modified_date date
     * unless overridden, sets a default item limit
    """
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}

    if 'sort' not in data_dict or not data_dict['sort'] or data_dict['sort'] == 'modified_date desc':
        data_dict['sort'] = 'modified_date desc'

        try:
            page = int(request.params.get('page', 1))
        except ValueError, e:
            abort(400, ('"page" parameter must be an integer'))

        data_dict['group'] = 'true'
        data_dict['group.query'] = ['-organization:estat AND -organization:comp AND -organization:grow', 'organization:estat', 'organization:comp', 'organization:grow']
        data_dict['group.format'] = 'simple'
        data_dict['rows'] = 2147483646

        start = (page - 1) * ITEMS_LIMIT

        result_cache_key = '{0}:{1}'.format(json.dumps(data_dict),start)
        count_cache_key = '{0}:{1}:{2}'.format(json.dumps(data_dict),start, 'count')


        result_list_string = cache.get_from_cache(result_cache_key, pool=cache.MISC_POOL)
        count_cache = cache.get_from_cache(count_cache_key, pool=cache.MISC_POOL)

        if result_list_string and count_cache:

            return int(count_cache), pickle.loads(result_list_string)

        else:
            try:
                query = get_action('custom_package_search')(context, data_dict.copy())
            except SearchError as se:
                log.warning(se)
                import traceback
                log.error(traceback.print_exc(se))
                abort(400, ('Search query could not be parsed'))

            cached_result= []

            for name, group in query['groups'].iteritems():
                cached_result += group['doclist']['docs']


            #result_list = customsearch.check_solr_result(context, cached_result[start:], ITEMS_LIMIT)
            result_list = []
            for item in cached_result[start:start+ITEMS_LIMIT]:
                try:
                    get_action('package_show')(context, {'id': item.get('id')})
                    result_list.append(context.get('package'))
                except NotFound as e:
                    log.warning('Package show: {0} Dataset not found'.format(item.get('id')))

            cache.set_value_in_cache(result_cache_key, pickle.dumps(result_list), pool=cache.MISC_POOL)
            cache.set_value_in_cache(count_cache_key, query['count'], pool=cache.MISC_POOL)

        return query['count'], result_list


    result_cache_key = '{0}'.format(json.dumps(data_dict))
    count_cache_key = '{0}:{1}'.format(json.dumps(data_dict), 'count')


    result_list_string = cache.get_from_cache(result_cache_key, pool=cache.MISC_POOL)
    count_cache = cache.get_from_cache(count_cache_key, pool=cache.MISC_POOL)

    if result_list_string and count_cache:
        return int(count_cache), pickle.loads(result_list_string)

    if 'rows' not in data_dict or not data_dict['rows']:
        data_dict['rows'] = ITEMS_LIMIT

    # package_search action modifies the data_dict, so keep our copy intact.
    try:
        context['internal'] = True
        query = __common_search(context, data_dict.copy())

        cache.set_value_in_cache(result_cache_key, pickle.dumps(query['results']), pool=cache.MISC_POOL)
        cache.set_value_in_cache(count_cache_key, query['count'], pool=cache.MISC_POOL)
    except search.SearchError, se:
        log.error('Search error: %r', se.args)
        query = {'count' : 0, 'results' : []}
    except ValueError, se:
        log.error('Search error: %r', se.args)
        query = {'count' : 0, 'results' : []}

    return query['count'], query['results']


def __common_search(context, data_dict):
    schema = (context.get('schema') or
              logic.schema.default_package_search_schema())
    data_dict, errors = _validate(data_dict, schema, context)
    try:
        locale = tk.request.environ['CKAN_LANG']
    except Exception:
        locale = config.get('ckan.locale_default', 'en')
    # put the extras back into the data_dict so that the search can
    # report needless parameters
    data_dict.update(data_dict.get('__extras', {}))
    data_dict.pop('__extras', None)
    if errors:
        raise ValidationError(errors)

    model = context['model']
    session = context['session']

    _check_access('package_search', context, data_dict)

    # Move ext_ params to extras and remove them from the root of the search
    # params, so they don't cause and error
    data_dict['extras'] = data_dict.get('extras', {})
    for key in [key for key in data_dict.keys() if key.startswith('ext_')]:
        data_dict['extras'][key] = data_dict.pop(key)

    abort = data_dict.get('abort_search', False)

    # check if some extension needs to modify the search params
    for item in plugins.PluginImplementations(plugins.IPackageController):
        try:
            data_dict = item.before_search(data_dict)
        except SearchError as e:
            raise e
        except Exception as e:
            log.error(e)
            abort = True

    # the extension may have decided that it is not necessary to perform
    # the query

    if data_dict.get('sort') in (None, 'rank'):
        data_dict['sort'] = 'score desc, metadata_modified desc'

    results = []
    facets = {}
    if not abort:
        # data_source = 'data_dict' if data_dict.get('use_default_schema',
        #                                            False) else 'validated_data_dict'
        # return a list of package ids
        # data_dict['fl'] = 'id {0}'.format(data_source)


        data_dict['fl'] = 'id'

        fq = data_dict.get('fq', '')
        # If this query hasn't come from a controller that has set this flag
        # then we should remove any mention of capacity from the fq and
        # instead set it to only retrieve public datasets
        if not context.get('ignore_capacity_check', False):

            fq = ' '.join(p for p in fq.split(' ')
                          if not 'capacity:' in p)
            data_dict['fq'] = fq + ' capacity:"public"'

        # Pop these ones as Solr does not need them
        # changed this for creatig the right query for solr
        # extras = data_dict.pop('extras', None)

        query = search.query_for(model.Package)
        start_time = time.time()
        query.run(data_dict)
        duration = time.time() - start_time
        log.info("Feeds Query execution took {0}".format(duration))

        result = {'count': query.count,
                  'facets': query.facets}
        ds_list = []
        for uri in query.results:

            tmp_context = context.copy()
            try:
                get_action('package_show')(tmp_context, {'uri': uri})
                dataset = tmp_context.get('package')
                ds_list.append(dataset)
            except NotFound as e:
                log.warning('Package show: {0} Dataset not found'.format(uri))

        result['results'] = ds_list

        return result






def __custom_grouped_search(context, data_dict):
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

        data_dict['fl'] = 'id'




def _create_atom_id(resource_path, authority_name=None, date_string=None):
    """
    Helper method that creates an atom id for a feed or entry.

    An id must be unique, and must not change over time.  ie - once published,
    it represents an atom feed or entry uniquely, and forever.  See [4]:

        When an Atom Document is relocated, migrated, syndicated,
        republished, exported, or imported, the content of its atom:id
        element MUST NOT change.  Put another way, an atom:id element
        pertains to all instantiations of a particular Atom entry or feedl;
        revisions retain the same content in their atom:id elements.  It is
        suggested that the atom:id element be stored along with the
        associated resource.

    resource_path
        The resource path that uniquely identifies the feed or element.  This
        mustn't be something that changes over time for a given entry or feed.
        And does not necessarily need to be resolvable.

        e.g. ``"/group/933f3857-79fd-4beb-a835-c0349e31ce76"`` could represent
        the feed of datasets belonging to the identified group.

    authority_name
        The domain name or email address of the publisher of the feed.  See [3]
        for more details.  If ``None`` then the domain name is taken from the
        config file.  First trying ``ckan.feeds.authority_name``, and failing
        that, it uses ``ckan.site_url``.  Again, this should not change over
        time.

    date_string
        A string representing a date on which the authority_name is owned by
        the publisher of the feed.

        e.g. ``"2012-03-22"``

        Again, this should not change over time.

        If date_string is None, then an attempt is made to read the config
        option ``ckan.feeds.date``.  If that's not available,
        then the date_string is not used in the generation of the atom id.

    Following the methods outlined in [1], [2] and [3], this function produces
    tagURIs like:
    ``"tag:thedatahub.org,2012:/group/933f3857-79fd-4beb-a835-c0349e31ce76"``.

    If not enough information is provide to produce a valid tagURI, then only
    the resource_path is used, e.g.: ::

        "http://thedatahub.org/group/933f3857-79fd-4beb-a835-c0349e31ce76"

    or

        "/group/933f3857-79fd-4beb-a835-c0349e31ce76"

    The latter of which is only used if no site_url is available.   And it
    should be noted will result in an invalid feed.

    [1] http://web.archive.org/web/20110514113830/http://diveintomark.org/\
    archives/2004/05/28/howto-atom-id
    [2] http://www.taguri.org/
    [3] http://tools.ietf.org/html/rfc4151#section-2.1
    [4] http://www.ietf.org/rfc/rfc4287
    """
    if authority_name is None:
        authority_name = config.get('ckan.feeds.authority_name', '').strip()
        if not authority_name:
            site_url = config.get('ckan.site_url', '').strip()
            authority_name = urlparse.urlparse(site_url).netloc

    if not authority_name:
        log.warning('No authority_name available for feed generation.  '
                    'Generated feed will be invalid.')

    if date_string is None:
        date_string = config.get('ckan.feeds.date', '')

    if not date_string:
        log.warning('No date_string available for feed generation.  '
                    'Please set the "ckan.feeds.date" config value.')

        # Don't generate a tagURI without a date as it wouldn't be valid.
        # This is best we can do, and if the site_url is not set, then
        # this still results in an invalid feed.
        site_url = config.get('ckan.site_url', '')
        return '/'.join([site_url, resource_path])

    tagging_entity = ','.join([authority_name, date_string])
    return ':'.join(['tag', tagging_entity, resource_path])


class ECPortalFeedsController(base.BaseController):

    base_url = config.get('ckan.site_url')

    def _alternate_url(self, params, **kwargs):
        search_params = params.copy()
        search_params.update(kwargs)

        # Can't count on the page sizes being the same on the search results
        # view.  So provide an alternate link to the first page, regardless
        # of the page we're looking at in the feed.
        search_params.pop('page', None)
        return self._feed_url(search_params,
                              controller='package',
                              action='search')

    def group(self, id):
        try:
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}
            group_dict = logic.get_action('group_show')(context, {'id': id})
        except logic.NotFound:
            base.abort(404, _('Group not found'))

        data_dict, params = self._parse_url_params()
        data_dict['fq'] = 'groups:"%s"' % id

        item_count, results = _package_search(data_dict)

        navigation_urls = self._navigation_urls(params,
                                                item_count=item_count,
                                                limit=data_dict['rows'],
                                                controller='feed',
                                                action='group',
                                                id=id)

        feed_url = self._feed_url(params,
                                  controller='feed',
                                  action='group',
                                  id=id)

        alternate_url = self._alternate_url(params, groups=id)

        return self.output_feed(results,
                                feed_title=u'%s - Group: "%s"' %
                                (_(g.site_title), group_dict['title']),
                                feed_description=u'Recently created or '
                                'updated datasets on %s by group: "%s"' %
                                (_(g.site_title), group_dict['title']),
                                feed_link=alternate_url,
                                feed_guid=_create_atom_id
                                (u'/feeds/groups/%s.atom' % id),
                                feed_url=feed_url,
                                navigation_urls=navigation_urls)

    def tag(self, id):
        data_dict, params = self._parse_url_params()
        data_dict['fq'] = 'tags:"%s"' % id

        item_count, results = _package_search(data_dict)

        navigation_urls = self._navigation_urls(params,
                                                item_count=item_count,
                                                limit=data_dict['rows'],
                                                controller='feed',
                                                action='tag',
                                                id=id)

        feed_url = self._feed_url(params,
                                  controller='feed',
                                  action='tag',
                                  id=id)

        alternate_url = self._alternate_url(params, tags=id)

        return self.output_feed(results,
                                feed_title=u'%s - Tag: "%s"' %
                                (_(g.site_title), id),
                                feed_description=u'Recently created or '
                                'updated datasets on %s by tag: "%s"' %
                                (_(g.site_title), id),
                                feed_link=alternate_url,
                                feed_guid=_create_atom_id
                                (u'/feeds/tag/%s.atom' % id),
                                feed_url=feed_url,
                                navigation_urls=navigation_urls)

    def general(self):
        data_dict, params = self._parse_url_params()
        data_dict['q'] = '*:*'

        item_count, results = _package_search(data_dict)

        navigation_urls = self._navigation_urls(params,
                                                item_count=item_count,
                                                limit=data_dict['rows'],
                                                controller='feed',
                                                action='general')

        feed_url = self._feed_url(params,
                                  controller='feed',
                                  action='general')

        alternate_url = self._alternate_url(params)

        return self.output_feed(results,
                                feed_title=_(g.site_title),
                                feed_description=u'Recently created or '
                                'updated datasets on %s' % _(g.site_title),
                                feed_link=alternate_url,
                                feed_guid=_create_atom_id
                                (u'/feeds/dataset.atom'),
                                feed_url=feed_url,
                                navigation_urls=navigation_urls)

    # TODO check search params
    def custom(self):
        q = request.params.get('q', u'')
        fq = ''
        search_params = {}
        params_dict = {}

        for plugin in p.PluginImplementations(p.IFacets):
            facets = plugin.dataset_facets(None, None);

        for (param, value) in request.params.items():
            if param not in ['q', 'plage', 'sort'] \
                    and len(value) and not param.startswith('_'):
                search_params[param] = value
                params_dict[param] = params_dict.get(param, []) + [value];
                param = "groups" if param == "eurovoc_domains" else param;
                fq += ' %s:"%s"' % (param, value)

        params_dict.pop('ext_boolean',None)
        try:
            page = int(request.params.get('page', 1)) or 1
        except ValueError:
            base.abort(400, _('"page" parameter must be a positive integer'))
        if page < 0:
            base.abort(400, _('"page" parameter must be a positive integer'))

        limit = ITEMS_LIMIT
        data_dict = {
            'q': q,
            'fq': fq,
            'start': (page - 1) * limit,
            'rows': limit,
            'sort': request.params.get('sort', None),
        }

        item_count, results = _package_search(data_dict)

        navigation_urls = self._navigation_urls(request.params,
                                                item_count=item_count,
                                                limit=data_dict['rows'],
                                                controller='feed',
                                                action='custom')

        feed_url = self._feed_url(request.params,
                                  controller='feed',
                                  action='custom')

        atom_url = h._url_with_params('/feeds/custom.atom',
                                      search_params.items())

        alternate_url = self._alternate_url(request.params)


        if q:
            q = "'%s'" % q
            if params_dict:
                q += ";"
        elif not q and params_dict:
            q = ''
        else:
            q = '[everything]'

        facets_title = '%s' % q
        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')


        for (param, value) in params_dict.iteritems():
            facets_title += u' %s filters:' % _(facets.get(param, 'Not set'))
            for term_trans in value:
                query = ''
                if param == 'vocab_theme':
                    trans_res_list = nal_util.retrieve_all_themes(locale)#.get(term_trans)
                    trans_res = next((item.get('label') for item in trans_res_list if item.get('uri') == term_trans), '')
                    query_result = [tuple([trans_res])]
                elif param == 'vocab_concepts_eurovoc':
                    trans_res_list = nal_util.retrieve_all_controlled_keyword(locale)#.get(term_trans)
                    trans_res = next((item[1] for item in trans_res_list if item[0] == term_trans),'')
                    query_result = [tuple([trans_res])]
                elif param == 'vocab_language':
                    trans_res_list = nal_util.retrieve_all_labels_in_graphs_for_language([nal_util.controlled_vocabulary['language'], locale])#.get(term_trans)
                    trans_res = next((item['label'] for item in trans_res_list if item['uri'] == term_trans),'')
                    query_result = [tuple([trans_res])]
                elif param == 'vocab_geographical_coverage':
                    trans_res_list = nal_util.retrieve_all_labels_in_graphs_for_language([nal_util.controlled_vocabulary['country'], locale])#.get(term_trans)
                    trans_res = next((item['label'] for item in trans_res_list if item['uri'] == term_trans), '')
                    query_result = [tuple([trans_res])]
                elif param == 'organization':
                    query = "select tt.term_translation from \"group\" gr join term_translation tt on tt.term = gr.title where gr.name = '%s' and gr.type = '%s' and tt.lang_code = '%s'" % (term_trans, param, unicode(i18n.get_lang()))
                    query_result = model.Session.execute(query).fetchall()
                    if not query_result:
                       query = "select title from \"group\" where type = 'organization' and name = '%s'" % term_trans
                       query_result = model.Session.execute(query).fetchall()
                else:
                    query_result = [tuple([term_trans])]


                for result in query_result:
                    facets_title += ' %s' % url.unquote(str(url.quote(result[0].encode('utf8'), safe=''))).decode('utf8')
                    if term_trans != value[-1]:
                        facets_title += ","
                    if term_trans == value[-1] and param != params_dict.keys()[-1]:
                        facets_title += ';'

        try:
            result = self.output_feed(results,
                                feed_title=u'%s - Custom query: %s' % (_(g.site_title),facets_title),
                                feed_description=u'Recently created or updated'
                                ' datasets on %s. Custom query: %s' %
                                (_(g.site_title), facets_title),
                                feed_link=alternate_url,
                                feed_guid=_create_atom_id(atom_url),
                                feed_url=feed_url,
                                navigation_urls=navigation_urls)
            return result
        except BaseException as e:
            import traceback
            log.error("Output feed failed")
            log.error(traceback.print_exc(e))
            # abort (417, "Output feed faild")


    def output_feed(self, results, feed_title, feed_description,
                    feed_link, feed_url, navigation_urls, feed_guid):
        author_name = config.get('ckan.feeds.author_name', '').strip() or \
            config.get('ckan.site_id', '').strip()
        author_link = config.get('ckan.feeds.author_link', '').strip() or \
            config.get('ckan.site_url', '').strip()
        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        # TODO language
        feed = _FixedAtom1Feed(
            title=feed_title,
            link=feed_link,
            description=feed_description,
            language=u'en',
            author_name=author_name,
            author_link=author_link,
            feed_guid=feed_guid,
            feed_url=feed_url,
            previous_page=navigation_urls['previous'],
            next_page=navigation_urls['next'],
            first_page=navigation_urls['first'],
            last_page=navigation_urls['last'],
        )

        sos_date = "1970-01-01T09:00:07.649436"  # use this date to allow the preview of the dataset
        for pkg in results: #type: DatasetDcatApOp
            pkg_id = pkg.dataset_uri
            if not pkg_id:
                raise BaseException('No valid dataset in result')
            context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj}
            try:
                translated_ds = ui_util.transform_dcat_schema_to_ui_schema(pkg,locale)


                modified_date = pkg.schema_catalog_record.modified_dcterms.get('0').value_or_uri
                updated_date = None

                if modified_date:
                    try:
                        updated_date = h.date_str_to_datetime(modified_date)
                    except BaseException as e:
                        log.warn('Could not cast {0} into date object'.format(modified_date))
                if not updated_date:
                    try:
                        updated_date = h.date_str_to_datetime(sos_date)
                    except BaseException as te:
                        log.warn('Could not cast {0} into date object. Dataset {1}.'.format(sos_date), pkg_id)

                issued_date = pkg.schema_catalog_record.issued_dcterms.get('0').value_or_uri
                published_date = None

                if issued_date:
                    try:
                        published_date = h.date_str_to_datetime(issued_date)
                    except BaseException as e:
                        log.warn('Could not cast {0} into date object. Dataset {1}'.format(issued_date, pkg_id))
                if not published_date:
                    try:
                        published_date = h.date_str_to_datetime(sos_date)
                    except BaseException as e:
                        log.warn(
                            'Could not cast {0} into date object. Dataset {1}.'.format(sos_date,
                                                                                       pkg_id))

                if updated_date and published_date:
                    feed.add_item(
                        title=translated_ds.get('title'),
                        #TODO: maybe replace urlparse.urljoin by h._url_with_params??
                        link=urlparse.urljoin(self.base_url,
                                              h.url_for(controller='package',
                                                      action='read',
                                                      id=pkg_id.split('/')[-1])),
                        description=translated_ds.get('description'),
                        updated=updated_date,
                        published=published_date,
                        unique_id=_create_atom_id(u'/dataset/%s' % pkg_id.split('/')[-1]),
                        author_name=pkg.schema.contactPoint_dcat.get('0', KindSchemaDcatApOp('')).organisationDASHname_vcard.get('0', ResourceValue('')).value_or_uri or '',
                        author_email=pkg.schema.contactPoint_dcat.get('0', KindSchemaDcatApOp('')).hasEmail_vcard.get('0', SchemaGeneric('')).uri or '',
                        categories=[t['display_name'] for t in translated_ds.get('keywords', [])],
                        #TODO: maybe replace urlparse.urljoin by h._url_with_params ??
                        enclosure=webhelpers.feedgenerator.Enclosure(
                            urlparse.urljoin(self.base_url,
                                            h.url_for(controller='api',
                                                    register='package',
                                                    action='show',
                                                    id=pkg_id.split('/')[-1],
                                                    ver='2')),
                            unicode(len(json.dumps(translated_ds))),  # TODO fix this
                            u'application/json'
                        )
                    )
            except BaseException as e:
                import traceback
                log.warning("Error to add item to feed {0}".format(pkg.dataset_uri))
                log.error(traceback.print_exc(e))

        response.content_type = feed.mime_type
        return feed.writeString('utf-8')

    #### CLASS PRIVATE METHODS ####

    def _feed_url(self, query, controller, action, **kwargs):
        """
        Constructs the url for the given action. Encoding the query parameters.
        """
        path = h.url_for(controller=controller, action=action, **kwargs)
        return h._url_with_params(self.base_url + path, query.items())

    def _navigation_urls(self, query, controller, action,
                         item_count, limit, **kwargs):
        """
        Constructs and returns first, last, prev and next links for paging
        """
        urls = dict((rel, None) for rel in 'previous next first last'.split())

        page = int(query.get('page', 1))

        # first: remove any page parameter
        first_query = query.copy()
        first_query.pop('page', None)
        urls['first'] = self._feed_url(first_query, controller,
                                       action, **kwargs)

        # last: add last page parameter
        last_page = (item_count / limit) + min(1, item_count % limit)
        last_query = query.copy()
        last_query['page'] = last_page
        urls['last'] = self._feed_url(last_query, controller,
                                      action, **kwargs)

        # previous
        if page > 1:
            previous_query = query.copy()
            previous_query['page'] = page - 1
            urls['previous'] = self._feed_url(previous_query, controller,
                                              action, **kwargs)
        else:
            urls['previous'] = None

        # next
        if page < last_page:
            next_query = query.copy()
            next_query['page'] = page + 1
            urls['next'] = self._feed_url(next_query, controller,
                                          action, **kwargs)
        else:
            urls['next'] = None

        return urls

    def _parse_url_params(self):
        """
        Constructs a search-query dict from the URL query parameters.

        Returns the constructed search-query dict, and the valid URL
        query parameters.
        """
        try:
            page = int(request.params.get('page', 1)) or 1
        except ValueError:
            base.abort(400, _('"page" parameter must be a positive integer'))
        if page < 0:
            base.abort(400, _('"page" parameter must be a positive integer'))

        limit = ITEMS_LIMIT
        data_dict = {
            'q': request.params.get('q', u''),
            'sort': request.params.get('sort', None),
            'start': (page - 1) * limit,
            'rows': limit
        }

        # Filter ignored query parameters
        valid_params = ['page']
        params = dict((p, request.params.get(p)) for p in valid_params
                      if p in request.params)
        return data_dict, params

    def history(self, id):
        import time
        package_type = self._get_package_type(id.split('@')[0])
        start = time.time()

        try:

            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}
            data_dict = {'id': id}
            c.pkg_dict = get_action('package_show')(context, data_dict)

            pkg_revisions = None
            pkg_revisions_str = redis_cache.get_from_cache('rss_revisions:{0}'.format(id), pool=redis_cache.MISC_POOL)
            if pkg_revisions_str:
                pkg_revisions = pickle.loads(pkg_revisions_str)
            else:
                pkg_revisions = get_action('package_revision_list')(context, data_dict)
                redis_cache.set_value_no_ttl_in_cache('rss_revisions:{0}'.format(id), pickle.dumps(pkg_revisions), pool=redis_cache.MISC_POOL)

            c.pkg_revisions = pkg_revisions


            c.package = context.get('package')
            dataset = context.get('package') #type: DatasetDcatApOp

            list_revisions = None
            revision_list_str = redis_cache.get_from_cache('rss_history:{0}'.format(id), pool=redis_cache.MISC_POOL)
            if revision_list_str:
                list_revisions = pickle.loads(revision_list_str)
            else:
                list_revisions = dataset.get_list_revisions_ordred(20)
                redis_cache.set_value_no_ttl_in_cache('rss_history:{0}'.format(id), pickle.dumps(list_revisions), pool=redis_cache.MISC_POOL)

            log.info('****************** rss1 /history took {0} sec**********************'.format((time.time()-start)))
            start = time.time()
            if 'diff' in request.params or 'selected1' in request.params:
                try:
                    params = {'id': request.params.getone('pkg_name'),
                              'diff': request.params.getone('selected1'),
                              'oldid': request.params.getone('selected2'),
                              }
                except KeyError, e:
                    if 'pkg_name' in dict(request.params):
                        id = request.params.getone('pkg_name')
                    c.error = \
                        _('Select two revisions before doing the comparison.')
                else:
                    params['diff_entity'] = 'package'
                    data_dict['list_revisions']= list_revisions
                    diff_report = diff_datasets(context, data_dict, params.get('diff'), params.get('oldid'))

                    c.diff = diff_report.get('diff_dict')
                    c.diff.sort()
                    c.revision_to ={}
                    c.revision_from ={}
                    c.revision_to = {'timestamp':diff_report['revision_to_time'],'id':params.get('oldid')}
                    c.revision_from = {'timestamp':diff_report['revision_from_time'],'id':params.get('diff')}
                    c.name = diff_report.get('title','')
                    c.diff_entity='package'
                    c.dataset_id= dataset.dataset_uri.split('/')[-1]
                    return base.render('revision/diff.html')
                    # h.redirect_to(controller='revision', action='diff', **params)

            c.pkg = context['package']
            log.info('****************** rss2 /history took {0} sec**********************'.format((time.time()-start)))

        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))

        start = time.time()
        format = request.params.get('format', '')
        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        web_schema = ui_util.transform_dcat_schema_to_ui_schema(dataset)
        log.info('****************** rss3 /history took {0} sec**********************'.format((time.time()-start)))

        start = time.time()
        if format == 'atom':
            # Generate and return Atom 1.0 document.
            start_loop = time.time()
            from webhelpers.feedgenerator import Atom1Feed
            feed = Atom1Feed(
                title=_(u''+web_schema.get('title','')),
                link=h.url_for(controller='revision', action='read',
                               id=web_schema.get('name')),
                description=_(u'Recent changes to CKAN Dataset: ') +
                (web_schema.get('title','') or ''),
                language=unicode(i18n.get_lang()),
            )
            for revision_dict in c.pkg_revisions:
                revision_date = h.date_str_to_datetime(
                    revision_dict['timestamp'])
                try:
                    dayHorizon = int(request.params.get('days'))
                except:
                    dayHorizon = 30
                dayAge = (datetime.datetime.now() - revision_date).days
                if dayAge >= dayHorizon:
                    break
                if revision_dict['message']:
                    item_title = u'%s' % revision_dict['message'].\
                        split('\n')[0]
                else:
                    item_title = u'%s' % revision_dict['id']
                item_link = h.url_for(controller='revision', action='read',
                                      id=revision_dict['id'])
                item_description = _('Log message: ')
                item_description += '%s' % (revision_dict['message'] or '')
                item_author_name = revision_dict['author']
                item_pubdate = revision_date
                feed.add_item(
                    title=item_title,
                    link=item_link,
                    description=item_description,
                    author_name=item_author_name,
                    pubdate=item_pubdate,
                )
                log.info('****************** rss loop execution /history took {0} sec**********************'.format((time.time()-start_loop)))

            feed.content_type = 'application/atom+xml'
            log.info('****************** rss4 /history took {0} sec**********************'.format((time.time()-start)))
            return feed.writeString('utf-8')

        c.related_count = 0
        log.info('****************** rss5 /history took {0} sec**********************'.format((time.time()-start)))
        return render('revision/history.html')

    def _history_template(self, package_type):
        return lookup_plugin.lookup_package_plugin(package_type).history_template()

    def _get_package_type(self, id):
        """
        Given the id of a package it determines the plugin to load
        based on the package's type name (type). The plugin found
        will be returned, or None if there is no plugin associated with
        the type.
        """
        pkg = model.Package.get(id)
        if pkg:
            return pkg.type or 'dataset'
        return None


# TODO paginated feed
class _FixedAtom1Feed(webhelpers.feedgenerator.Atom1Feed):
    """
    The Atom1Feed defined in webhelpers doesn't provide all the fields we
    might want to publish.

     * In Atom1Feed, each <entry> is created with identical <updated> and
       <published> fields.  See [1] (webhelpers 1.2) for details.

       So, this class fixes that by allow an item to set both an <updated> and
       <published> field.

     * In Atom1Feed, the feed description is not used.  So this class uses the
       <subtitle> field to publish that.

       [1] https://bitbucket.org/bbangert/webhelpers/src/f5867a319abf/\
       webhelpers/feedgenerator.py#cl-373
    """

    def add_item(self, *args, **kwargs):
        """
        Drop the pubdate field from the new item.
        """
        if 'pubdate' in kwargs:
            kwargs.pop('pubdate')
        defaults = {'updated': None, 'published': None}
        defaults.update(kwargs)
        super(_FixedAtom1Feed, self).add_item(*args, **defaults)

    def latest_post_date(self):
        """
        Calculates the latest post date from the 'updated' fields,
        rather than the 'pubdate' fields.
        """
        updates = [item['updated'] for item in self.items
                   if item['updated'] is not None]
        if not len(updates):  # delegate to parent for default behaviour
            return super(_FixedAtom1Feed, self).latest_post_date()
        return max(updates)

    def add_item_elements(self, handler, item):
        """
        Add the <updated> and <published> fields to each entry that's written
        to the handler.
        """
        super(_FixedAtom1Feed, self).add_item_elements(handler, item)

        dfunc = webhelpers.feedgenerator.rfc3339_date

        if(item['updated']):
            handler.addQuickElement(u'updated',
                                    dfunc(item['updated']).decode('utf-8'))

        if(item['published']):
            handler.addQuickElement(u'published',
                                    dfunc(item['published']).decode('utf-8'))

    def add_root_elements(self, handler):
        """
        Add additional feed fields.

         * Add the <subtitle> field from the feed description
         * Add links other pages of the logical feed.
        """
        super(_FixedAtom1Feed, self).add_root_elements(handler)

        handler.addQuickElement(u'subtitle', self.feed['description'])

        for page in ['previous', 'next', 'first', 'last']:
            if self.feed.get(page + '_page', None):
                handler.addQuickElement(u'link', u'',
                                        {'rel': page,
                                         'href':
                                            self.feed.get(page + '_page')})


