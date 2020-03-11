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

import cPickle as pickle
import logging
import time
import ujson as json

import sqlalchemy
from pylons import config

import ckan.lib.dictization
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.navl.dictization_functions
import ckan.lib.search as search
import ckan.logic as logic
import ckan.logic.schema
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckanext.ecportal.lib.cache.redis_cache as redis_cache
import ckanext.ecportal.lib.dataset_util as dataset_util
import ckanext.ecportal.lib.ui_util as ui_util
import ckanext.ecportal.lib.controlled_vocabulary_util as mdr_util
import ckanext.ecportal.lib.tag_util as tag_util
import ckanext.ecportal.lib.uri_util as uri_util

from pylons import config
from ckan.common import _
from ckan.lib.search.common import  SearchError, SearchQueryError
from ckanext.ecportal.lib.search.solr_search import SchemaSearchQuery
from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_distribution_schema import DistributionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric, ResourceValue
from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_revision_schema import  RevisionSchemaDcatApOp
from ckanext.ecportal.lib.ui_util import _get_translated_term_from_dcat_object, DEFAULT_LANGUAGE, _get_organization_translation_from_database
from redis.connection import ConnectionError
from ckanext.ecportal.model.identifier_mapping import DatasetIdMapping
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': CKAN_PATH + '/var/cache',
    'cache.lock_dir': CKAN_PATH + '/var/cache'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))



log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_table_dictize = ckan.lib.dictization.table_dictize
_check_access = logic.check_access
NotFound = logic.NotFound
DataError = ckan.lib.navl.dictization_functions.DataError
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust

_select = sqlalchemy.sql.select
_aliased = sqlalchemy.orm.aliased
_or_ = sqlalchemy.or_
_and_ = sqlalchemy.and_
_func = sqlalchemy.func
_desc = sqlalchemy.desc
_case = sqlalchemy.case
_text = sqlalchemy.text

NUM_MOST_VIEWED_DOMAINS = int(config.get('ckan.eurovoc_domains.hompage', 9))

THEME_ICON_MAPPING = {'http://publications.europa.eu/resource/authority/data-theme/GOVE': '07',
                    'http://publications.europa.eu/resource/authority/data-theme/JUST': '08',
                    'http://publications.europa.eu/resource/authority/data-theme/ECON': '05',
                    'http://publications.europa.eu/resource/authority/data-theme/SOCI': '12',
                    'http://publications.europa.eu/resource/authority/data-theme/EDUC': '10',
                    'http://publications.europa.eu/resource/authority/data-theme/HEAL': '11',
                    'http://publications.europa.eu/resource/authority/data-theme/TRAN': '04',
                    'http://publications.europa.eu/resource/authority/data-theme/ENVI': '09',
                    'http://publications.europa.eu/resource/authority/data-theme/AGRI': '01',
                    'http://publications.europa.eu/resource/authority/data-theme/TECH': '13',
                    'http://publications.europa.eu/resource/authority/data-theme/ENER': '02',
                    'http://publications.europa.eu/resource/authority/data-theme/REGI': '03',
                    'http://publications.europa.eu/resource/authority/data-theme/INTR': '06'}

def _package_list_with_resources(context, package_revision_list):
    package_list = []
    for package in package_revision_list:
        result_dict = model_dictize.package_dictize(package, context)
        package_list.append(result_dict)
    return package_list


def site_read(context, data_dict=None):
    '''Return ``True``.

    :rtype: boolean

    '''
    _check_access('site_read', context, data_dict)
    return True

@logic.side_effect_free
def package_show_rest(context, data_dict):
    _check_access('package_show_rest',context, data_dict)


    pkg = logic.get_action('package_show')(context, data_dict)


    return pkg


@logic.side_effect_free
def package_show(context, data_dict):
    '''Return the metadata of a dataset (package) and its resources.
    This overrides core package_show to deal with DCAT-AP data

    :param str uri: the uri  of the dataset

    :rtype: dictionary

    '''
    start = time.time()
    uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'dataset')
    dataset_uri_ckan2odp = data_dict.get("objectUri")
    if dataset_uri_ckan2odp:
        name_or_id = dataset_uri_ckan2odp
    elif data_dict.get("id"):
        name_or_id = '{0}/{1}'.format(uri_prefix, data_dict.get("id"))
    else:
        name_or_id = data_dict.get("uri")  # or 'http://data.europa.eu/999/dataset/dgt-translation-memory-V1-2'

    if not name_or_id:
        raise DataError('No id provided')
    active_cache = config.get('ckan.cache.active', 'false')
    dataset = None  # type: DatasetDcatApOp
    if active_cache == 'true':
        # get the ds from cache
        dataset_string = redis_cache.get_from_cache(name_or_id, pool=redis_cache.DATASET_POOL)
        if dataset_string:
            dataset = pickle.loads(dataset_string)
            log.info('Load dataset from cache: {0}'.format(name_or_id))
            # dataset = DatasetDcatApOp(name_or_id,dataset_json)

    if not dataset or not dataset.schema:

        dataset = DatasetDcatApOp(name_or_id)
        graph_name = dataset.find_the_graph_in_ts()
        loaded = False
        if graph_name not in [DCATAPOP_PRIVATE_GRAPH_NAME,DCATAPOP_PUBLIC_GRAPH_NAME]:
            raise logic.NotFound('Package show: dataset {0} {1}'.format(name_or_id, _('ecodp.dcat.dataset.not_found')))
        if graph_name == DCATAPOP_PUBLIC_GRAPH_NAME:
            dataset.set_state_as_public()
            loaded = dataset.get_description_from_ts()
        elif graph_name == DCATAPOP_PRIVATE_GRAPH_NAME and (context.get('auth_user_obj',None) or context.get('ignore_auth',False) == True):
            dataset.set_state_as_private()
            active_cache = 'false'
            loaded = dataset.get_description_from_ts()
        if loaded:
            log.info('Load dataset from ts: {0}'.format(name_or_id))
        else:
            log.info('Load dataset from ts failed: {0}'.format(name_or_id))
            raise logic.NotFound('Package show: dataset {0} {1}'.format(name_or_id, _('ecodp.dcat.dataset.not_found')))
        if active_cache == 'true' and loaded:
            redis_cache.set_value_no_ttl_in_cache(name_or_id, pickle.dumps(dataset))

    if not dataset.schema and not loaded:
        raise logic.NotFound('Package show: dataset {0} {1}'.format(name_or_id, _('ecodp.dcat.dataset.not_found')))

    context['package'] = dataset
    permission = _check_access('package_show', context, data_dict)
    if not permission:
        raise logic.NotAuthorized()

    if context.get('internal'):
        log.info('Package show internal took {0} sec'.format(time.time() - start))
        context['package'] = dataset
        return dataset

    output_format = data_dict.get('output_format', u'standard')
    if output_format not in [u'standard', u'rdf', u'json']:
        output_format = u'standard'
    package_dict = {}
    if not output_format == u'json':
        package_dict['rdf'] = dataset.get_dataset_as_rdfxml()

    if not output_format == u'rdf':
        package_dict['dataset'] = dataset.schema.schema_dictaze()

    if not output_format == u'rdf':
        package_dict['catalog_record'] = {} if not dataset.schema_catalog_record else dataset.schema_catalog_record.schema_dictaze()

    if output_format == u'standard':
        package_dict['capacity']= dataset.privacy_state

    if context.get('for_view'):
        try:
            locale = tk.request.environ['CKAN_LANG']
        except Exception:
            locale = config.get('ckan.locale_default', 'en')


        package_dict = ui_util.transform_dcat_schema_to_ui_schema(dataset, locale)
        # package_dict.update(ui_dict)
        for item in plugins.PluginImplementations(plugins.IPackageController):
            log.debug('Loaded plugin: {0}'.format(item.__class__.__name__))
            package_dict = item.before_view(package_dict)

        for key, resource_dict in package_dict.get('distribution_dcat', {}).items():
            resource_dict['id'] = resource_dict['uri'].split('/')[-1]
            for item in plugins.PluginImplementations(plugins.IResourceController):
                log.debug('Loaded plugin: {0}'.format(item.__class__.__name__))
                resource_dict = item.before_show(resource_dict)

    # for item in plugins.PluginImplementations(plugins.IPackageController):
    #     item.after_show(context, package_dict)
    log.info('Package show took {0} sec'.format(time.time() - start))
    return package_dict


@logic.side_effect_free
def catalogue_show(context, data_dict):
    """

    :param context:
    :param data_dict:
    :return:
    """
    start = time.time()
    uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'catalogue')
    if data_dict.get("id"):
        name_or_id = '{0}/{1}'.format(uri_prefix, data_dict.get("id"))
    else:
        name_or_id = data_dict.get("uri")  # or 'http://data.europa.eu/999/dataset/dgt-translation-memory-V1-2'

    if not name_or_id:
        raise DataError('No id provided')
    active_cache = config.get('ckan.cache.active', 'false')
    catalogue = None  # type: CatalogDcatApOp
    if active_cache == 'true':
        # get the ds from cache
        catalogue_string = redis_cache.get_from_cache(name_or_id, pool=redis_cache.DATASET_POOL)
        if catalogue_string:
            catalogue = pickle.loads(catalogue_string)
            log.info('Load catalogue from cache: {0}'.format(name_or_id))
            # dataset = DatasetDcatApOp(name_or_id,dataset_json)

    if not catalogue or not catalogue.schema:
        catalogue = CatalogDcatApOp(name_or_id)
        # todo optimize the code
        loaded = catalogue.get_description_from_ts()
        if not loaded and (context.get('auth_user_obj',None) or context.get('ignore_auth',False) == True):
            catalogue.set_state_as_private()
            #private dataset should not be cached
            active_cache = 'false'
            loaded = catalogue.get_description_from_ts()

        if not loaded:
            raise logic.NotFound('Package show: catalogue {0} {1}'.format(name_or_id, _('ecodp.dcat.dataset.not_found')))


        if active_cache == 'true':
            redis_cache.set_value_no_ttl_in_cache(name_or_id, pickle.dumps(catalogue), pool=redis_cache.DATASET_POOL)

    if not catalogue.schema:
        raise logic.NotFound('Package show: dataset {0} {1}'.format(name_or_id, _('ecodp.dcat.dataset.not_found')))

    context['catalogue'] = catalogue
    if context.get('internal'):
        log.info('Catalogue show internal took {0} sec'.format(time.time() - start))
        return catalogue

    package_dict = {}#{'rdf': catalogue.get_dataset_as_rdfxml()}
    package_dict['catalogue'] = catalogue.schema.schema_dictaze()


    log.info('Catalogue show took {0} sec'.format(time.time() - start))
    return package_dict


@logic.side_effect_free
def catalogue_list(context, data_dict):
    """

    :param context:
    :param data_dict:
    :return:
    """
    active_cache = config.get('ckan.cache.active', 'false')
    catalog_list = None

    if active_cache == 'true':
        # get the ds from cache
        catalogue_string = redis_cache.get_from_cache('catalogue_list', pool=redis_cache.MISC_POOL)
        if catalogue_string:
            catalog_list = pickle.loads(catalogue_string)
            log.info('Load catalogue list from cache')

    if not catalog_list:
        catalog = CatalogDcatApOp('TMP') # type: CatalogDcatApOp
        catalog_list = catalog.get_list_catalogs()
        if active_cache == 'true':
            redis_cache.set_value_no_ttl_in_cache('catalogue_list', pickle.dumps(catalog_list),pool=redis_cache.MISC_POOL)

    return catalog_list



@logic.side_effect_free
def package_search(context, data_dict):
    '''
    Searches for packages satisfying a given search criteria.

    This action accepts solr search query parameters (details below), and
    returns a dictionary of results, including dictized datasets that match
    the search criteria, a search count and also facet information.

    **Solr Parameters:**

    For more in depth treatment of each paramter, please read the `Solr
    Documentation <http://wiki.apache.org/solr/CommonQueryParameters>`_.

    This action accepts a *subset* of solr's search query parameters:


    :param q: the solr query.  Optional.  Default: `"*:*"`
    :type q: string
    :param fq: any filter queries to apply.  Note: `+site_id:{ckan_site_id}`
        is added to this string prior to the query being executed.
    :type fq: string
    :param sort: sorting of the search results.  Optional.  Default:
        'relevance asc, metadata_modified desc'.  As per the solr
        documentation, this is a comma-separated string of field names and
        sort-orderings.
    :type sort: string
    :param rows: the number of matching rows to return.
    :type rows: int
    :param start: the offset in the complete result for where the set of
        returned datasets should begin.
    :type start: int
    :param output_format: the structure of the returned packages.  Optional.  Default: "standard".
        - "rdf" to return only the RDF structure of each packages.
        - "json" to return only the JSON structure of each packages.
        - "standard" to return only the complete structure of each packages.
    :type output_format: string
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
    :param results: ordered list of datasets matching the query, where the
        ordering defined by the sort parameter used in the query.
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

     {'count': 2,
      'results': [ { <snip> }, { <snip> }],
      'search_facets': {u'tags': {'items': [{'count': 1,
                                             'display_name': u'tolstoy',
                                             'name': u'tolstoy'},
                                            {'count': 2,
                                             'display_name': u'russian',
                                             'name': u'russian'}
                                           ]
                                 }
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
    rdf2ckan = data_dict.pop('rdf2ckan_list', None)
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

    # retrieved the output structure format
    output_format = data_dict.get('output_format', u'standard')
    if 'output_format' in data_dict:
        del data_dict['output_format']

    results = []
    facets = {}
    if not abort:
        # data_source = 'data_dict' if data_dict.get('use_default_schema',
        #                                            False) else 'validated_data_dict'
        # return a list of package ids
        # data_dict['fl'] = 'id {0}'.format(data_source)


        data_dict['fl'] = 'id name owner_org notes title resource_list views_total res_format title_{0} text_{0} modified_date capacity'.format((locale))

        if rdf2ckan:
            data_dict['fl'] = 'name id'

        #if not context.get('for_view', False):
        #    data_dict['fl'] = '*'

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
        log.info("Query execution took {0}".format(duration))
        # Add them back so extensions can use them on after_search
        # data_dict['extras'] = extras
        start_time = time.time()
        if context.get('for_view', False):
            for package in query.results:
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
        elif rdf2ckan:
            #special rdf2ckan search
            publisher = fq.split(':')[-1]
            mapping = DatasetIdMapping.get_dict_of_mappings_by_publisher(publisher)

            for package in query.results:
                int_id = package.get('id').split('/')[-1]
                url = mapping.get(int_id, {}).get('external_id', None)
                solr_name = package.get('name')
                if url:
                    new_name = uri_util.generate_local_part_URI(url)
                    results.append({'name': new_name})


                results.append({'name': solr_name})

        elif context.get('package_list', False):
            results = [result.get('id').split('/')[-1] for result in query.results]
            return results

        else:
            for package in query.results:
                try:
                    key = 'uri'
                    uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'dataset')
                    if uri_prefix not in package['id']:
                        key = 'id'
                    tmp_package = logic.get_action('package_show')(context, {key: package['id'], 'output_format': output_format})

                except ConnectionError as e:
                    import traceback
                    log.error(traceback.print_exc())

                except Exception as e:
                    import traceback
                    log.error(traceback.print_exc())
                    log.error(e.message)


                results.append(tmp_package)

        duration = time.time() - start_time
        log.info("result processing took {0}".format(duration))

        count = query.count
        facets = query.facets
    else:
        count = 0
        facets = {}
        results = []

    start_time = time.time()
    search_results = {
        'count': count,
        'facets': facets,
        'results': results,
        'sort': data_dict['sort']
    }

    # Transform facets into a more useful data structure.
    restructured_facets = {}
    if facets:
        groups = model.Session.query(model.Group.name, model.Group.title).filter(model.Group.state == 'active').filter(model.Group.type != 'eurovoc_domain').all()

    duration = time.time() - start_time
    log.info("Groups query took {0}".format(duration))

    start_time = time.time()
    for key, value in facets.items():
        restructured_facets[key] = {
            'title': key,
            'items': []
        }
        for key_, value_ in value.items():
            new_facet_dict = {}
            new_facet_dict['name'] = key_
            if key in ('eurovoc_domains', 'groups', 'organization'):

                group_title = next((group.title for group in groups if group.name == key_),'')
                if group_title:
                    new_facet_dict['display_name'] = group_title
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
    duration = time.time() - start_time
    log.info("Facets processing took {0}".format(duration))

    start_time = time.time()
    # check if some extension needs to modify the search results
    for item in plugins.PluginImplementations(plugins.IPackageController):
        plugin_start_time = time.time()
        log.debug('Loaded after_search plugin: {0}'.format(item.__class__.__name__))
        search_results = item.after_search(search_results, data_dict)
        plugin_duration = time.time() - plugin_start_time
        log.info("{0} processing took {1}".format(item.__class__.__name__, plugin_duration))

    duration = time.time() - start_time
    log.info("After search plugins took {0}".format(duration))
    return search_results

@logic.side_effect_free
def package_list(context, data_dict):
    '''Return a list of the names of the site's datasets (packages).

    :param limit: if given, the list of datasets will be broken into pages of
        at most ``limit`` datasets per page and only one page will be returned
        at a time (optional)
    :type limit: int
    :param offset: when ``limit`` is given, the offset to start returning packages from
    :type offset: int

    :rtype: list of strings

    '''
    model = context["model"]
    context['package_list'] = True
    api = context.get("api_version", 1)

    _check_access('package_list', context, data_dict)


    query_dict = {}
    limit = data_dict.get('limit', None)
    if limit:
        query_dict['rows'] = limit
    else:
        query_dict['rows'] = 2147483647

    offset = data_dict.get('offset')
    if offset:
        query_dict['start'] = offset

    result = package_search(context, query_dict)

    ## Returns the first field in each result record
    return result


def current_package_list_with_resources(context, data_dict):
    '''Return a list of the site's datasets (packages) and their resources.

    The list is sorted most-recently-modified first.

    :param limit: if given, the list of datasets will be broken into pages of
        at most ``limit`` datasets per page and only one page will be returned
        at a time (optional)
    :type limit: int
    :param offset: when ``limit`` is given, the offset to start returning packages from
    :type offset: int
    :param page: when ``limit`` is given, which page to return, Deprecated use ``offset``
    :type page: int

    :rtype: list of dictionaries

    '''
    model = context["model"]
    limit = data_dict.get('limit')
    offset = data_dict.get('offset', 0)

    if not 'offset' in data_dict and 'page' in data_dict:
        log.warning('"page" parameter is deprecated.  '
                    'Use the "offset" parameter instead')
        page = data_dict['page']
        if limit:
            offset = (page - 1) * limit
        else:
            offset = 0

    _check_access('current_package_list_with_resources', context, data_dict)

    context['for_view'] = True

    result = package_search(context,{'start': offset, 'rows': limit})

    return result.get('results', [])


def _add_tracking_summary_to_resource_dict(resource_dict, model):
    '''Add page-view tracking summary data to the given resource dict.

    '''
    tracking_summary = model.TrackingSummary.get_for_resource(
        resource_dict['url'])
    resource_dict['tracking_summary'] = tracking_summary


def user_show(context, data_dict):
    '''Return a user account.

    Either the ``id`` or the ``user_obj`` parameter must be given.

    :param id: the id or name of the user (optional)
    :type id: string
    :param user_obj: the user dictionary of the user (optional)
    :type user_obj: user dictionary

    :rtype: dictionary

    '''

    model = context['model']

    id = data_dict.get('id',None)
    provided_user = data_dict.get('user_obj',None)
    if id:
        user_obj = model.User.get(id)
        context['user_obj'] = user_obj
        if user_obj is None:
            raise NotFound
    elif provided_user:
        context['user_obj'] = user_obj = provided_user
    else:
        raise NotFound

    _check_access('user_show',context, data_dict)

    user_dict = model_dictize.user_dictize(user_obj,context)

    if context.get('return_minimal'):
        return user_dict

    if not context.get('no_groups'):
        revisions_q = model.Session.query(model.Revision
                ).filter_by(author=user_obj.name)

        revisions_list = []
        for revision in revisions_q.limit(20).all():
            revision_dict = logic.get_action('revision_show')(context,{'id':revision.id})
            revision_dict['state'] = revision.state
            revisions_list.append(revision_dict)
        user_dict['activity'] = revisions_list

    if not context.get('no_datasets'):
        user_dict['datasets'] = []
        dataset_q = model.Session.query(model.Package).join(model.PackageRole
                ).filter_by(user=user_obj, role=model.Role.ADMIN
                ).limit(50)

    user_dict['num_followers'] = logic.get_action('user_follower_count')(
            {'model': model, 'session': model.Session},
            {'id': user_dict['id']})

    return user_dict

@logic.side_effect_free
def resource_show(context, data_dict):
    '''Return the metadata of a resource.

    :param id: the id of the resource
    :type id: string

    :rtype: dictionary

    '''
    model = context['model']
    id = _get_or_bust(data_dict, 'id')

    uri_prefix = config.get('ckan.ecodp.uri_prefix')
    uri = '{0}/{1}/{2}'.format(config.get('ckan.ecodp.uri_prefix'), 'distribution', id)

    resource = DistributionSchemaDcatApOp(uri)

    if not resource.get_description_from_ts():
        uri = '{0}/{1}/{2}'.format(config.get('ckan.ecodp.uri_prefix'), 'document', id)
        resource = DocumentSchemaDcatApOp(uri)

    if not resource.get_description_from_ts():
        raise NotFound('Resource {0} not found.'.format(id))

    context['resource'] = resource

   # _check_access('resource_show', context, data_dict)
    resource_dict = resource.schema_dictaze()
    resource_dict['format'] = ''
    if isinstance(resource, DistributionSchemaDcatApOp):
        resource_dict['url'] = resource.downloadURL_dcat.get('0', SchemaGeneric('')).uri or resource.accessURL_dcat.get('0', SchemaGeneric('')).uri
        resource_dict['format'] = resource.format_dcterms.get('0', SchemaGeneric('')).uri.split('/')[-1]
    elif isinstance(resource, DocumentSchemaDcatApOp):
        resource_dict['url'] = resource.url_schema.get('0', ResourceValue('')).value_or_uri
        resource_dict['format'] = resource.format_dcterms.get('0', SchemaGeneric('')).uri.split('/')[-1]

    if isinstance(resource, DistributionSchemaDcatApOp):
        resource_dict['id'] = resource.uri.split('/')[-1]
        for item in plugins.PluginImplementations(plugins.IResourceController):
            resource_dict = item.before_show(resource_dict)

    try:
            prev_url = resource_dict['url']
            prev_format = resource_dict.get('format', '')
            prev_res = {'url': prev_url,
                        'format': prev_format,
                        'id': id}
    except Exception as e:
            import traceback
            log.error('{0}'.format(e))
            log.error(traceback.print_exc())
    resource_dict['can_be_previewed'] = _resource_preview({'resource': prev_res})

    return resource_dict


def _resource_preview(data_dict):
        import ckan.lib.datapreview as datapreview
        return bool(datapreview.res_format(
            data_dict['resource']) in datapreview.direct() + datapreview.loadable() or datapreview.get_preview_plugin(
            data_dict, return_first=True))


def theme_list(context, data_dict=None):
    if not data_dict:
        data_dict = {}
    logic.check_access('group_list', context, data_dict)
    ckan_lang = config.get('ckan.locale_default', 'en')
    try:
        ckan_lang = tk.request.environ['CKAN_LANG']
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())
    mdr_list = ['http://publications.europa.eu/resource/authority/data-theme']
    vocab = mdr_util.retrieve_all_themes(ckan_lang)
    result = []
    if data_dict.get('mode','') == 'most_common':
        result = vocab[:NUM_MOST_VIEWED_DOMAINS]
    elif data_dict.get('mode','') == 'less_common':
        result = vocab[NUM_MOST_VIEWED_DOMAINS:]
    else:
        result = vocab

    if context.get('for_view', ''):
        for theme in result:
            icon_id = THEME_ICON_MAPPING.get(theme['uri'], '')
            theme['icon_id'] = icon_id

    return result

@logic.side_effect_free
def legacy_package_show(context, data_dict):
    '''Return the metadata of a dataset (package) and its resources.
    This overrides core package_show to deal with DCAT-AP data

    :param str uri: the uri  of the dataset

    :rtype: dictionary

    '''
    import ckanext.ecportal.model.mapping.old_model_mapper as mapper

    if config.get('ckan.ecodp.backward_compatibility', 'true') in 'false, False':
        raise logic.NotFound('Function not available')

    uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'dataset')
    dataset_uri_ckan2odp = data_dict.get("objectUri")
    if dataset_uri_ckan2odp:
        name_or_id = dataset_uri_ckan2odp
    elif data_dict.get("id"):
        name_or_id = '{0}/{1}'.format(uri_prefix, data_dict.get("id"))
    else:
        name_or_id = data_dict.get("uri")  # or 'http://data.europa.eu/999/dataset/dgt-translation-memory-V1-2'

    if not name_or_id:
        raise DataError('No id provided')
    active_cache = config.get('ckan.cache.active', 'false')
    dataset = None  # type: DatasetDcatApOp
    if active_cache == 'true':
        # get the ds from cache
        dataset_string = redis_cache.get_from_cache(name_or_id, pool=redis_cache.DATASET_POOL)
        if dataset_string:
            dataset = pickle.loads(dataset_string)
            log.info('Load dataset from cache: {0}'.format(name_or_id))
            # dataset = DatasetDcatApOp(name_or_id,dataset_json)

    if not dataset or not dataset.schema:
        dataset = DatasetDcatApOp(name_or_id)
        # todo optimize the code
        if not dataset.get_description_from_ts() and (context.get('auth_user_obj',None) or context.get('ignore_auth',False) == True):
            dataset.set_state_as_private()
            #private dataset should not be cached
            active_cache = 'false'

        if not dataset.get_description_from_ts():
            raise logic.NotFound(_('ecodp.dcat.dataset.not_found'))

        log.info('Load dataset from ts: {0}'.format(name_or_id))
        if active_cache == 'true':
            redis_cache.set_value_no_ttl_in_cache(name_or_id, pickle.dumps(dataset))

    if not dataset.schema:
        raise logic.NotFound('ecodp.dcat.dataset.not_found')

    context['package'] = dataset
    permission = _check_access('package_show', context, data_dict)

    if not permission:
        raise logic.NotAuthorized()

    package_dict = mapper.package_show_schema(dataset)

    return package_dict

@logic.side_effect_free
def vocabulary_list(context, data_dict=None):

    return tag_util.get_vocabulary_list()

@logic.side_effect_free
def tag_list(context, data_dict):

    vocab = data_dict.get('vocabulary_id', None)

    result_list = tag_util.get_all_items_of_vocabulary(vocab)

    if not data_dict.get('all_fields', False):
        return [value for key, value in result_list.items()]
    else:
        return [{"vocabulary_id": vocab,
            "display_name": value,
            "id": key,
            "name": value} for key, value in result_list.items()]

@logic.side_effect_free
def group_show(context, data_dict):
    '''Return the details of a group.

    :param id: the id or name of the group
    :type id: string
    :param include_datasets: include a list of the group's datasets
         (optional, default: ``True``)
    :type id: boolean

    :rtype: dictionary

    .. note:: Only its first 1000 datasets are returned

    '''
    from ckan.logic.action.get import _group_or_org_show

    if 'eurovoc_domain' in data_dict.get('id','') :
            raise NotFound('EurovocDomains are not available any more')
    return _group_or_org_show(context, data_dict)

@logic.side_effect_free
def group_show_read(context, data_dict):
    """
    Adapt the grouyp show to return as result the group_dict and the contgext itself.
    The idea is to allow caching it
    :param context:
    :param data_dict:
    :return: dict
    """

    @cache.cache('cached_group_show_read', expire=3600)
    def _group_or_org_show_cached(key_context, key_data_dict):
        import pickle
        from ckan.logic.action.get import _group_or_org_show

        group_dict = _group_or_org_show(context, data_dict)
        group = context.get('group')
        group.Session = None


        result = {'group_dict':group_dict,'group':group}
        return result
    def reset_cache ():
        from  ckanext.ecportal.lib.cache.cache_util import CacheUtil
        CacheUtil().invalidate_cache()
        log.info("Reset cache folder after group show failed")

        result = {}
    try:
        # import shutil
        # shutil.rmtree("/hhh")
        result = _group_or_org_show_cached(context.get('user'),data_dict)
    except BaseException as e:
        import traceback
        log.error("group_show_read failed")
        log.error(traceback.print_exc(e))
        # reset_cache()
        # result = _group_or_org_show_cached(context.get('user'), data_dict)
    return result

