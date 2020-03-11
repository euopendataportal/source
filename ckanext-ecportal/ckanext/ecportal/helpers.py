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

import Cookie
import logging
import operator
import ujson as json
import random
import time
import urllib
import urlparse
from datetime import datetime
from urllib import urlencode

import ckan.lib.formatters as formatters
import ckan.lib.base as base
import ckan.lib.helpers as ckanhelpers
import ckan.lib.i18n as i18n
import ckan.lib.search as search
import ckan.logic as logic
import ckan.model as model
import ckan.new_authz as authz
import ckan.plugins.toolkit as tk
import dateutil.parser
import os.path as path
import pylons.config as config
import re
import sqlalchemy.exc
import ckanext.ecportal.lib.groups_util as groups_util
import ckanext.ecportal.lib.cache.redis_cache as cache
from ckan.common import _, g, c
from ckan.common import request
from ckan.lib import datapreview
from ckan.lib.navl.dictization_functions import Invalid
from ckan.plugins.core import _PLUGINS
from jinja2 import Template

import ckanext.ecportal.controllers.configuration as configuration
import ckanext.ecportal.searchcloud as searchcloud
import ckanext.ecportal.unicode_sort as unicode_sort
from ckanext.ecportal.action import customsearch
from ckanext.ecportal.lib.controlled_vocabulary_util import Distribution_controlled_vocabulary, \
    Documentation_controlled_vocabulary, _get_translation, retrieve_all_labels_for_language, \
    retrieve_all_datasets_status, retrieve_all_file_types, retrieve_all_eurovoc_domains, retrieve_all_themes, retrieve_all_languages,\
    other_identifier_controlled_vocabulary, retrieve_all_licenses

from odp_common import RESOURCE_TYPE_VISUALIZATION, DISTRIBUTION_TYPES, DOCUMENTATION_TYPES, DOCUMENTATION_TYPE_WEBPAGE_RELATED
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric, ResourceValue
from ckanext.ecportal.virtuoso.graph_names_constants import GRAPH_LANGUAGE

from ckanext.ecportal.model.iso639_1_bcp47converison import ISO_639_1_TO_BCP47

from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

render = base.render
NUM_TOP_PUBLISHERS = 6
UNICODE_SORT = unicode_sort.UNICODE_SORT
EUROVOC_CONCEPTS = 1
EUROVOC_DOMAINS = 2
EUROVOC_CONCEPTS_VOCAB_NAME = u'concepts_eurovoc'
EUROVOC_DOMAINS_VOCAB_NAME = u'domains_eurovoc'
NUM_MOST_VIEWED_DATASETS = 10
_or_ = sqlalchemy.or_

KEYWORD = 0
log = logging.getLogger(__file__)
c = tk.c

translatable_resource_field = ['name', 'description', 'url', 'last_modified', 'size', 'iframe_code']


def resource_preview(resource, package):
    '''
    Returns a rendered snippet for a embedded resource preview.

    Depending on the type, different previews are loaded.
    This could be an img tag where the image is loaded directly or an iframe
    that embeds a web page, recline or a pdf preview.
    '''


    if not resource.get('url', None):
        return ckanhelpers.snippet("dataviewer/snippets/no_preview.html",
                                   resource_type=None,
                                   reason=_(u'The resource url is not specified.'))

    format_lower = datapreview.res_format(resource)
    directly = False
    data_dict = {'resource': resource, 'package': package}

    if datapreview.get_preview_plugin(data_dict, return_first=True):
        url = ckanhelpers.url_for(controller='package', action='resource_datapreview',
                      resource_id=resource['id'], id=package['id'])
    elif format_lower in datapreview.direct():
        directly = True
        url = resource['url']
    elif format_lower in datapreview.loadable():
        url = resource['url']
    else:
        reason = None
        if format_lower:
            log.info(
                _(u'No preview handler for resource of type {0}'.format(
                    format_lower))
            )
        else:
            reason = _(u'The resource format is not specified.')
        return ckanhelpers.snippet("dataviewer/snippets/no_preview.html",
                       reason=reason,
                       resource_type=format_lower)

    return ckanhelpers.snippet("dataviewer/snippets/data_preview.html",
                   embed=directly,
                   resource_url=url,
                   raw_resource_url=resource.get('url'))

def filter_tags(vocab):
    def callable(key, data, errors, context):
        v = model.Vocabulary.get(vocab)
        if not v:
            raise Invalid(_('Tag vocabulary "%s" does not exist') % vocab)
        tags = []
        for k in data.keys():
            if k[0] == 'tags':
                if data[k].get('vocabulary_id') == v.id:
                    tags.append(data[k])
        data[key] = tags

    return callable


def current_url():
    return tk.request.environ['CKAN_CURRENT_URL'].encode('utf-8')


def current_locale():
    try:
        return i18n.get_locales_dict().get(tk.request.environ['CKAN_LANG']) \
               or fallback_locale()
    except BaseException as e:
        # a workaround to return always a language
        class mock:
            pass

        current = mock()
        current.language = 'en'
        return current

def current_locale_bcp47():
    lang = current_locale().language
    try:
        return ISO_639_1_TO_BCP47[lang]
    except BaseException as e:
        # a workaround to return always a language
        return 'en-GB'


def root_url(full=False):
    locale = tk.request.environ.get('CKAN_LANG')
    default_locale = tk.request.environ.get('CKAN_LANG_IS_DEFAULT', True)
    base_url = config.get('ckan.site_url', '') if full else ''
    if default_locale:
        return base_url + '/'
    else:
        return base_url + '/{0}/'.format(locale)


def fallback_locale():
    return i18n.get_locales_dict().get(config.get('ckan.locale_default', 'en'))


def filter_keywords_no_voc_id(keywords):
    if not keywords == None:
        return [tag for tag in keywords if not tag.get('vocabulary_id')]


def get_keywords_name(keywords):
    return_list = []
    for keyword in keywords:
        if isinstance(keyword, dict):
            return_list.append(keyword.get('display_name') or keyword.get('name'))
        else:
            return_list.append(keyword)
    return return_list


def get_viz_resources(pkg):
    rslt = []
    for resource in pkg.get('resources', []):
        if resource.get('resource_type') == RESOURCE_TYPE_VISUALIZATION:
            rslt.append(resource)
    rslt = sorted(rslt, key=lambda resource: resource.get('title', resource.get('description','')))
    return rslt


def is_viz_resource(res):
    return res.get('resource_type') == RESOURCE_TYPE_VISUALIZATION

def is_non_doc_resource(res):
    return res.get('resource_type') in DISTRIBUTION_TYPES

def get_doc_resources(pkg):
    rslt = [r for r in pkg.get('resources', []) if
            r.get('resource_type') in DOCUMENTATION_TYPES]
    rslt = sorted(rslt, key=lambda resource: resource.get('title', resource.get('description','')))
    return rslt

def is_web_page_resource(res):
    return res.get('resource_type') == DOCUMENTATION_TYPE_WEBPAGE_RELATED


def get_non_viz_resources(pkg, viz_resources, doc_resources):
    rslt = [r for r in pkg.get('resources', []) if not r in viz_resources and not r in doc_resources]
    rslt = sorted(rslt, key=lambda resource: resource.get('title', resource.get('description','')))
    return rslt


def get_non_viz_resources2(pkg):
    rslt = [r for r in pkg.get('resources', []) if not r in get_doc_resources(pkg) and not r in get_viz_resources(pkg)]
    rslt = sorted(rslt, key=lambda resource: resource.get('title', resource.get('description','')))
    return rslt


def _create_eurovoc_domain_name_with_link(eurovoc_uri):
        if eurovoc_uri:
            uri = eurovoc_uri.replace("http://", "").replace("https://", "").replace(".","_").replace("/","_")\
            .replace("europa", "domain").replace("_eu", "")
            return uri

def domain_render_link_list(domains, type=None):
    results = []
    for domain in domains:
        uri = _create_eurovoc_domain_name_with_link(domain.get("uri"))
        link = domain_render_link_search(uri)
        if type is not None:
            link += ("?eurovoc_domains=" if type == "domain" else "?groups=")
            link += urllib.quote_plus(domain.get("uri"))
        link_html = (ckanhelpers.link_to(domain.get("title"), link))
        results.append(link_html)
    return results


def domain_render_link_search(tag):
    # return ckanhelpers.url_for(controller='group', action='read', id=tag['name'])
    return ckanhelpers.url_for(controller='group', action='read', id=tag)


def group_render_link_list(groups):
    results = []

    for group in groups:
        group_uri = group.get("uri", None)
        if group_uri:
            group_name = group_uri.split('/')[-1]
            try:
                group_title = model.Session.query(model.Group.title) \
                    .filter(model.Group.state == 'active') \
                    .filter(model.Group.name == group_name).one()

                title = group_title.title
            except Exception as e:
                logging.error("group_render_link_list : Group {0} was not find in database".format(group_name))
                title = group.get('uri')

            link_html = ckanhelpers.link_to(title, group_uri)
            results.append(link_html)
        return results


def resource_display_format(resource_dict):
    return format_display_name(resource_dict.get('format'))


def format_display_name(resource_format):
    if resource_format in resource_mapping():
        resource_format = resource_mapping()[resource_format][1]
    return resource_format


_RESOURCE_MAPPING = None


def resource_mapping():
    global _RESOURCE_MAPPING
    if not _RESOURCE_MAPPING:
        file_location = config.get(
            'ckan.resource_mapping',
            '/applications/ecodp/users/ecodp/ckan/default/src/ckanext-ecportal/data/resource_mapping.json'
        )
        with open(file_location) as resource_file:
            _RESOURCE_MAPPING = json.loads(resource_file.read())

    return _RESOURCE_MAPPING


_RESOURCE_MAPPING_JSON = None


def resource_mapping_json():
    global _RESOURCE_MAPPING_JSON
    if not _RESOURCE_MAPPING_JSON:
        _RESOURCE_MAPPING_JSON = resource_mapping()

    return json.dumps(_RESOURCE_MAPPING_JSON)


def group_facets_by_field(fields):
    facet_order = {'tags': 0, 'res_format': 1}
    facets = {}
    fields = [i for i in fields if i[0] != 'id']
    for field, value in fields:
        if field in facets:
            facets[field].append(value)
        else:
            facets[field] = [value]
    return sorted(facets.items(),
                  key=lambda x: facet_order.get(x[0], len(facet_order)))
    return facets


def get_selected_facets_translation(fields, label_source):
    result = []
    if not label_source:
        return result
    for field, ids in fields:
        value_list = []
        for id in ids:
            for item in label_source.get(field,{}).get('items',[]):
                if item['name'] == id:
                    value = {}
                    value['name'] = id
                    value['display_name'] = item['display_name']
                    value_list.append(value)
                    break
        result.append((field, value_list))
    return result


def get_facet_title(name, fallback_title):
    return config.get('search.facets.%s.title' % name, fallback_title)


def search_url_params(key=None, value=None):
    # Parameter data is passed to the ckan.controllers.feed.custom.
    # As this current adds search parameters that are not in
    # ['q', 'page', 'sort'] and don't beging with '_' to the
    # Solr 'fq' field, we need to remove ext_boolean here.
    params = [(k, v) for k, v in tk.request.params.items()
              if not k in ['page', 'ext_boolean']]
    if key and value:
        params.append((key, value))
    return urllib.urlencode(
        [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
         for k, v in params])


def dataset_resource_formats(resources):
    '''
    Return a list of dataset resource formats.
    Will only return each format once.

    For example: if a dataset has 5 resources, 2 zip files and 3 csv files,
    this will return ['zip', 'csv']
    '''

    total_list_format = []
    for res in resources:
        format_string = res.get('format', [])
        # format_string = next((f for f in format), '')
        if format_string:
            total_list_format.append(format_string)

    return list(set(total_list_format))
    # return list(set([r.get('format') for r in resources if r.get('format')]))


def list_tags(tags, separator):
    result = ''
    for tag in tags:
        if not tag.get('vocabulary_id'):
            result += tag['display_name']
            result += separator
    # we remove the last separator
    result = result[:-1 * len(separator)]
    return result


def most_viewed_datasets(num_datasets=NUM_MOST_VIEWED_DATASETS):
    start_time = time.time()
    locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
    cache_key = 'most_viewed_datasets:{0}'.format(locale)
    dict_string = cache.get_from_cache(cache_key, pool=cache.MISC_POOL)
    search_results = None
    if dict_string:
        search_results = json.loads(dict_string)
    else:
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user or c.author, 'for_view': True}
        data = {
            'rows': num_datasets,
            'sort': u'views_total desc',
            'facet': u'false'}
        #    'fl': 'id, name, title, views_total'}
        # Ugly: going through ckan.lib.search directly
        # (instead of get_action('package_search').
        #
        # TODO: Can we return views_total using package_search for internal
        # use only (without outputting it during public API calls)?
        # query = search.query_for(model.Package)
        # result = query.run(data)
        optimized_search_results = []
        short_dataset = {}
        try:
            search_results = tk.get_action('package_search')(context, data)
            # optimize the list by seelcting only the three used fileds
            search_results = [r for r in search_results.get('results', [])]

            # for dataset in search_results:
            #     # TODO: should we dictalize the dataset like older dict ?
            #     short_dataset = {'name': dataset['name'],
            #                      'title': dataset['title'],
            #                      'tracking_summary': dataset['tracking_summary']}
            #
            #     # short_dataset['name'] = dataset['name']
            #     # short_dataset['title'] = dataset['title']
            #     # short_dataset['tracking_summary'] = dataset['tracking_summary']
            #     optimized_search_results.append(short_dataset)
            cache.set_value_in_cache(cache_key, json.dumps(search_results), pool=cache.MISC_POOL)
        except search.SearchError, e:
            log.error('Error searching for most viewed datasets')
            log.error(e)
    duration2 = time.time() - start_time
    log.info("Build most_viewed_datasets took {0}".format(duration2))
    # return [r for r in search_results.get('results', [])]
    # if r.get('tracking_summary').get('total',0) > 0]
    return search_results


def recent_updates(n):
    '''
    Return a list of the n most recently updated datasets.
    '''
    import ckanext.ecportal.action.customsearch as customsearch
    start_time = time.time()

    context = {'model': model,
               'session': model.Session,
               'user': c.user or c.author,
               'for_view': True}
    data = {'rows': n,
            'sort': 'modified_date desc',
            'facet': 'false',
            'fq': 'capacity:public',
            'group': 'true',
            'group.query': ['-organization:estat AND -organization:comp AND -organization:grow', 'organization:estat',
                            'organization:comp', 'organization:grow'],
            'group.limit': 10,
            }

    locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
    cache_key = 'recent_updates:{0}'.format(locale)
    dict_string = cache.get_from_cache(cache_key, pool=cache.MISC_POOL)
    if dict_string:

        prep_result = json.loads(dict_string)
    else:
        try:
            search_results = tk.get_action('custom_package_search')(context, data)

            result = customsearch.check_solr_result(context,
                                                    search_results['groups']['organization:estat']['doclist']['docs'],
                                                    4)
            result += customsearch.check_solr_result(context,
                                                     search_results['groups']['organization:comp']['doclist']['docs'],
                                                     1)
            result += customsearch.check_solr_result(context,
                                                     search_results['groups']['organization:grow']['doclist']['docs'],
                                                     1)
            prep_result = customsearch.check_solr_result(context, search_results['groups'][
                '-organization:estat AND -organization:comp AND -organization:grow']['doclist']['docs'],
                                                         10 - len(result))
            prep_result += result
            # r.set('recent_updates:en', prep_result)
            cache.set_value_in_cache(cache_key, json.dumps(prep_result),pool=cache.MISC_POOL)
        except search.SearchError:
            log.error('Error no results')
            prep_result = {}
        except Exception as e:
            log.error('Error no results', e)
            prep_result = {}

    end = time.time() - start_time
    log.info('Build Recent datasests took {0} s'.format(end))

    return prep_result


def approved_search_terms():
    try:
        terms = searchcloud.get_approved(model.Session)
        if terms:
            return searchcloud.approved_to_json(terms)
    except sqlalchemy.exc.ProgrammingError:
        log.error('Could not retrieve search cloud results from database. '
                  'Do the tables exist? Rolling back the session.')
        model.Session.rollback()


def ecportal_date_to_iso(date_string):
    '''
    Expects a date in either YYYY, YYYY-MM or YYYY-MM-DD format.
    Returns an ISO 8601 date string.
    '''

    return dateutil.parser.parse(date_string).isoformat()


def ecportal_render_datetime(datetime_, date_format=None, with_hours=False):
    date = dateutil.parser.parse(datetime_)
    return formatters.localised_nice_date(date, show_date=True,
                                          with_hours=with_hours)

def render_datetime_fix(datetime_, date_format=None, with_hours=False):

    try:
        datetime_ = dateutil.parser.parse(datetime_)
    except BaseException as e:
        return ''
    # if date_format was supplied we use it
    if date_format:
        formated_date_time =''
        try:
            formated_date_time = datetime_.strftime(date_format)
        except BaseException as e:
            formated_date_time = '{0}-{1}-{2}'.format(datetime_.year, datetime_.month, datetime_.day)
        return formated_date_time

    # the localised date
    return formatters.localised_nice_date(datetime_, show_date=True,
                                          with_hours=with_hours)

tags = None
tags_translations = dict([])



def translate(terms, lang, fallback_lang):
    if lang == fallback_lang:
        codes = lang
    else:
        codes = (lang, fallback_lang)
    translations = logic.get_action('term_translation_show')(
        {'model': model},
        {'terms': terms, 'lang_codes': codes}
    )

    term_translations = {}
    for term in terms:
        matching_translations = [translation for translation in
                                 translations if translation['term'] == term and
                                 translation['lang_code'] == lang]
        if not matching_translations:
            matching_translations = [translation for translation in
                                     translations if translation['term'] == term and
                                     translation['lang_code'] == fallback_lang]
        if matching_translations:
            assert len(matching_translations) == 1
            translation = matching_translations[0]['term_translation']
        else:
            translation = term
        term_translations[term] = translation
    return term_translations


def top_publishers(groups):
    '''
    Updates the 'packages' field in each group dict (up to a maximum
    of NUM_TOP_PUBLISHERS) to show the number of public datasets in the group.
    '''
    publishers = [g for g in groups if g['packages'] > 0]
    publishers.sort(key=operator.itemgetter('packages'), reverse=True)

    return publishers[:NUM_TOP_PUBLISHERS]


def organizations_available(user, group_type='organization'):
    context = {'model': model, 'session': model.Session, 'user': user}
    userobj = model.User.get(user)

    ckan_lang = str(current_locale())
    ckan_lang_fallback = str(fallback_locale())

    DISPLAY_NAME = 'display_name'

    get_action_name = '{0}_list'.format(group_type)
    all_organizations = logic.get_action(get_action_name)(context, {'all_fields': True})
    organizations = []

    if authz.is_sysadmin(user):
        organizations = all_organizations
    elif userobj:
        user_linked_organizations_id = [organization.id for organization in userobj.get_groups() if
                                        organization.type == group_type]
        organizations = [organization for organization in all_organizations if
                         organization['id'] in user_linked_organizations_id]

    group_translations = translate(
        [organization.get(DISPLAY_NAME) for organization in organizations],
        ckan_lang, ckan_lang_fallback)

    # Translate the groups' display name

    # Functional style, little less efficient
    # def update_display_name(group):
    #    group[DISPLAY_NAME] = group_translations[group[DISPLAY_NAME]]
    #    return group
    #
    # groups_with_translated_name = map(lambda x: update_display_name(x), groups)

    # Loop style
    groups_with_translated_name = []
    for gr in organizations:
        gr[DISPLAY_NAME] = group_translations[gr[DISPLAY_NAME]]
        groups_with_translated_name.append(gr)

    return groups_with_translated_name


def sort_array(array, key):
    array.sort(key=operator.itemgetter(key))
    return array


def get_resources_num_res(resources):
    return [(resource.get('num'), resource.get('res')) for resource in resources]


def names_from_tags(tags):
    if not tags:
        tags = []
    if isinstance(tags, unicode):
        return [tags]
    tags_name = []
    for tag in tags:
        if ('name' in tag):
            tags_name.append(tag['name'])
        if isinstance(tag, basestring):
            tags_name.append(tag)
    return tags_name


def id_from_tags(tags):
    if isinstance(tags, unicode):
        return [tags]
    tags_id = []
    for tag in tags:
        if ('id' in tag):
            tags_id.append(tag['id'])
    return tags_id


def starts_with_tel(string):
    return string.startswith('tel:')


def get_catalog_url():
    return config.get('ckan.catalog_url', 'http://data.europa.eu/euodp/')


def get_dataset_url():
    import urlparse
    domain = config['ckan.site_url']
    path = 'dataset/%s' % c.pkg_dict.get('name', c.pkg_dict['id'])
    result = urlparse.urljoin(domain, path)
    c.dataset_url = result

    return result


_RESOURCE_DROPDOWN = None


def resource_dropdown_list():
    global _RESOURCE_DROPDOWN
    if not _RESOURCE_DROPDOWN:
        file_location = config.get(
            'ckan.resource_dropdown',
            CKAN_PATH + '/ckanext-ecportal/data/resource_dropdown.json'
        )
        with open(file_location) as resource_file:
            # load then dump to check if its valid early
            _RESOURCE_DROPDOWN = json.loads(resource_file.read())
    return _RESOURCE_DROPDOWN


def resource_dropdown():
    return json.dumps(resource_dropdown_list())


def get_domain_id(name):
    k = name.rfind("_")
    substring = name[:k + 1]
    if substring == "eurovoc_domain_":
        return name[k + 1:]


def get_extra_fields(resource):
    from ckanext.ecportal.forms import ECPortalDatasetForm
    list_lang = config.get('ckan.locales_offered', [])
    # get schema for resources
    ecd = ECPortalDatasetForm()
    schema_resource = ecd.show_package_schema()['resources']
    filtered_resource = []
    # return filter(lambda l: l != default_licence, c.licences)
    for key in resource.keys():
        is_extra_field = True
        key_splitted = key.split('-')
        if len(key_splitted) == 2 and key_splitted[0] in translatable_resource_field and key_splitted[1] in list_lang:
            is_extra_field = False
        if key not in schema_resource.keys() and is_extra_field:
            list_item = dict()
            list_item['key'] = key
            list_item['value'] = resource[key]
            filtered_resource.append(list_item)
    # keep those not in the schema & return them
    return filtered_resource;


def remove_url_param_for_group_read(key, domain, controller=None, value=None, replace=None, extras=None, alternative_url=None):
    from urllib import urlencode

    if isinstance(key, basestring):
        keys = [key]
    else:
        keys = key

    params_nopage = [(k, v) for k, v in request.params.items() if k != 'page']
    params = list(params_nopage)
    if value:
        params.remove((keys[0], value))
    else:
        for key in keys:
            [params.remove((k, v)) for (k, v) in params[:] if k == key]
    if replace is not None:
        params.append((keys[0], replace))

    if alternative_url:
        if not params:
            return alternative_url
        params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v)) for k, v in params]
        return alternative_url + u'?' + urlencode(params)

    url = ckanhelpers.url_for(controller=controller, action='read', id=domain)
    if not params:
        return url
    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params]
    return url + u'?' + urlencode(params)


def add_url_param_for_group_read(domain, alternative_url=None, controller=None, action=None, extras=None,
                                 new_params=None):
    from urllib import urlencode

    params_nopage = [(k, v) for k, v in request.params.items() if k != 'page']
    params = set(params_nopage)
    if new_params:
        params |= set(new_params.items())
    if alternative_url:
        if not params:
            return alternative_url
        params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v)) for k, v in params]
        return alternative_url + u'?' + urlencode(params)

    url = ckanhelpers.url_for(controller=controller, action='read', id=domain)
    if not params:
        return url
    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params]
    return url + u'?' + urlencode(params)


def filter_groups_by_type(list, type):
    return filter(lambda t: t.uri == type, list.values())


def is_sysadmin(user):
    return authz.is_sysadmin(user)


def getSurveyLinkTarget():
    baseURL = config.get('survey.base.url')
    surveyName = config.get('survey.name')
    linkTarget = "%s/%s-%s" % (baseURL.rstrip('/'), surveyName.lstrip('/'), str(current_locale()).upper())
    params = {'referencedPage': request.url}
    url = add_parameters_to_url(linkTarget, params)
    return url


def add_parameters_to_url(linkTarget, params):
    url_parts = list(urlparse.urlparse(linkTarget))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)
    return url


def get_value_from_config(key, default):
    value = config.get(key)
    if value is not None:
        return value
    log.warn('Could not find key ' + key + ' in .ini file')
    return default


def get_array_json_from_config(key, default):
    value = config.get(key)
    if value is not None:
        array = value.split(' ')
        array_json = json.dumps(array, escape_forward_slashes=False)
        return array_json
    log.warn('Could not find key ' + key + ' in .ini file')
    return default


def unicode2string(unicodeString):
    if isinstance(unicodeString, list):
        encoded = unicodeString[0].encode('utf8')
    else:
        encoded = unicodeString.encode('utf8')
    return encoded


def is_metadatatool_plugin_activated():
    return 'rdft' in _PLUGINS


def getExternalLinkURL():
    return "/euodp%s" % (root_url())


def get_available_locales():
    locales = i18n.get_available_locales()
    for locale in locales:
        if locale.language == 'zh':
            log.debug('Locales: %s' % locale)
            locales.remove(locale)
    return locales


def get_available_locales_as_string():
    return [locale.language for locale in get_available_locales()]

_RESOURCE_MAPPING_JSON = None


def resource_mapping_json():
    global _RESOURCE_MAPPING_JSON
    if not _RESOURCE_MAPPING_JSON:
        _RESOURCE_MAPPING_JSON = resource_mapping()

    return json.dumps(_RESOURCE_MAPPING_JSON)


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v)) for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)


def get_skos_hierarchy(max_element=None):
    ''' use for the display the skos hierarchy on the front page'''
    # group = model.Group.get("com")
    # hierarchy = group.get_children_groups(type=group.type)


    context = {'model': model, 'session': model.Session,
               'user': c.user, 'for_view': True,
               'with_private': False}

    start = time.time()
    result = tk.get_action('get_skos_hierarchy')(context, max_element)
    end = time.time() - start
    log.info('Build skos hierarchiy took {0} s'.format(end))

    return result


def get_last_word(string, token):
    return string.rsplit(token, 1)[1]


def get_random_number(start=1, stop=100, step=1):
    return random.randrange(start, stop, step)


def get_langs_for_resource(resource_dict):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author}
    download_url = resource_dict.get("download_url")
    if not isinstance(download_url, list) or len(download_url) <= 1:
        return

    langs = []
    for resource in download_url:
        resource_lang = ''
        resource_tab_link = resource.rsplit("_", 1)
        if len(resource_tab_link)>1 :
            resource_lang = resource_tab_link[1][:2].lower()
        if resource_lang and resource_lang in i18n.get_locales_dict().keys() and resource_lang != fallback_locale():
            langs.append(resource_lang)

    return langs


def get_translated_field(resource_dict, lang, field, recursive_done=False):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author}
    resource = ''
    for resource in resource_dict.get(field, []):
        resource_language = resource.rsplit("_",1)
        if len(resource_language)>1 :
            resource_language = resource_language[1][:2].lower()
        if resource_language in get_available_locales_as_string():
            if resource_language == lang:
                return resource

    if not recursive_done:
        return get_translated_field(resource_dict, fallback_locale().language, field, True)
    return resource


    #return tk.get_action('get_translated_field')(context, {'lang': lang, 'field': field, 'data_dict': resource_dict})


def get_translated_field_without_fallback(resource_dict, lang, field):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author}
    return tk.get_action('get_translated_field')(context, {'lang': lang, 'field': field, 'data_dict': resource_dict,
                                                           'remove_default': True})


def get_english_resource_url(resource_dict):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author}

    for resource in resource_dict.get("download_url"):
        return resource if resource.rsplit("_",1)[1][:2] == fallback_locale() else ""


def resource_display_name(resource_dict):
    name = resource_dict.get('title', None)
    description = resource_dict.get('description', None)
    if name and not 'Default_Title' in name:
        return name
    elif description:
        description = description.split('.')[0]
        max_len = 60
        if len(description) > max_len:
            description = description[:max_len] + '...'
        return description
    else:
        return _("Unnamed resource")


def is_multi_languaged_resource(resource_dict):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author}
    download_url = resource_dict.get("download_url")
    if not isinstance(download_url, list) or len(download_url) <= 1:
        return False
    else:
        result = get_langs_for_resource(resource_dict)
        if not result:
            return False
    return True



def get_selected_datasets_for_user():
    return


def wait_for_solr_to_update():
    '''
    Stadard wait time for solr to process update
    '''
    time.sleep(2)


def format_error_message(error):
    result = []
    if not isinstance(error, list):
        return error.split(',')[0]
    for message in error:
        result.append(message.split(',')[0])

    return result


def format_error_message_for_ingestion_report(errors):
    rules = configuration.buildGroups()[0]
    rules.update(configuration.buildGroups()[1])
    rules.update(configuration.buildGroups()[2])

    result = {'dataset': [],
              'resources': []}
    for level in errors.itervalues():
        for key, error in level.iteritems():
            if 'resources' != key:
                rule = {}
                rule['id'] = 0
                if not isinstance(error, list):
                    rule['short'] = error.split(',')[0]
                    rule['long'] = error.split(',')[-1]
                    temp = [value['id'] for value in rules.itervalues() if _(value['message']) == rule['short']]
                    if len(temp) > 0:
                        rule['id'] = temp[0]
                for message in error:
                    rule['short'] = message.split(',')[0]
                    rule['long'] = message.split(',')[-1]
                    temp = [value['id'] for value in rules.itervalues() if _(value['message']) == rule['short']]
                    if len(temp) > 0:
                        rule['id'] = temp[0]
                result['dataset'].append(rule)
            else:
                res_id = ''
                for  resource in error:
                    res_list = []
                    for field, res_error in resource.iteritems():
                        if 'uri' == field:
                            res_id = res_error
                            continue
                        rule = {}
                        rule['id'] = 0

                        if not isinstance(res_error, list):
                            rule['short'] = field
                            rule['long'] = res_error
                            temp = [value['id'] for value in rules.itervalues() if _(value['message']) == rule['short']]
                            if len(temp) > 0: rule['id'] = temp[0]
                        for message in res_error:
                            rule['short'] = field
                            rule['long'] = message
                            temp = [value['id'] for value in rules.itervalues() if _(value['message']) == rule['short']]
                            if len(temp) > 0: rule['id'] = temp[0]
                        res_list.append(rule)
                    res_list = sorted(res_list, key=lambda k: k['id'])
                    result['resources'].append((res_id, res_list))

    result['dataset'] = sorted(result['dataset'], key=lambda k: k['id'])
    return result


def resources_type_list_from_resource_type(resource_type):
    from ckanext.ecportal.controllers.package import ECPORTALPackageController
    dataset = ECPORTALPackageController()
    all = dataset.RESOURCES_TYPES
    try:
        distribution_list = [a for a, b in dataset.RESOURCES_TYPES_DISTRIBUTION]
        documentation_list = [a for a, b in dataset.RESOURCES_TYPES_DOCUMENTATION]
        vizualisation_list = [a for a, b in dataset.RESOURCES_TYPES_VISUALIZATION]
    except:
        distribution_list = []
        documentation_list = []
        vizualisation_list = []

    if resource_type in distribution_list:
        return dataset.RESOURCES_TYPES_DISTRIBUTION
    elif resource_type in documentation_list:
        return dataset.RESOURCES_TYPES_DOCUMENTATION
    elif resource_type in vizualisation_list:
        return dataset.RESOURCES_TYPES_VISUALIZATION
    else:
        return all or []

def resources_type_name_from_resource_type(resource_type):
    from ckanext.ecportal.controllers.package import ECPORTALPackageController
    dataset = ECPORTALPackageController()

    newone = next(('distribution' for a,b in dataset.RESOURCES_TYPES_DISTRIBUTION if resource_type == a),None)

    if not newone:
        newone = next(('documentation' for a,b in dataset.RESOURCES_TYPES_DOCUMENTATION if resource_type == a),None)

    if not newone:
        newone = next(('visualization' for a,b in dataset.RESOURCES_TYPES_VISUALIZATION if resource_type == a),None)
    if not newone:
        newone = dataset.RESOURCES_TYPES

    return newone
    # try:
    #     distribution_list = [a for a, b in dataset.RESOURCES_TYPES_DISTRIBUTION]
    #     documentation_list = [a for a, b in dataset.RESOURCES_TYPES_DOCUMENTATION]
    #     vizualisation_list = [a for a, b in dataset.RESOURCES_TYPES_VISUALIZATION]
    # except:
    #     distribution_list = []
    #     documentation_list = []
    #     vizualisation_list = []
    #
    # if resource_type in distribution_list:
    #     return "distribution"
    # elif resource_type in documentation_list:
    #     return "documentation"
    # elif resource_type in vizualisation_list:
    #     return "visualization"
    # else:
    #     return all or []


def get_athorized_groups(dataset_count=True):
    context = {'model': model, 'session': model.Session, 'for_view': True,
               'user': tk.c.user or tk.c.author}

    groups = logic.get_action('group_list_authz')(context, {})
    groups = [group for group in groups if 'group' == group.get('type', '')]
    if dataset_count:
        for group in groups:

            count = groups_util.get_number_of_datasets_for_group(group.get('name'))
            group['packages'] = count


    groups = sorted(groups, key=lambda x: x['display_name'])
    return groups


def correct_ATTO_message(message):
    msg = message
    if "ecodp.common.ckan.site_title" in message:
        correct_message = message.replace("ecodp.common.ckan.site_title", _("ecodp.common.ckan.site_title"))
        msg = correct_message
    return msg
    correct_message = ""
    return correct_message


def get_count_dataset():
    count_datasets = 0
    try:
        # package search
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj, 'for_view': True}
        data_dict = {
            'q': '*:*',
        }
        result = logic.get_action('package_search')(
            context, data_dict)
        count_datasets = result['count']
    except search.SearchError:
        count_datasets = 0
    return count_datasets


def merge_error_dictsOld(a, b, path=None, update=True):
    """
    Generic function to merge two complex dicts
    "http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge"
    :param a:
    :param b:
    :param path:
    :param update:
    :return:
    """

    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_error_dictsOld(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx, val in enumerate(b[key]):
                    a[key][idx] = merge_error_dictsOld(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
            elif update:
                a[key] = b[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def merge_error_dicts(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    import collections
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            merge_error_dicts(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct


def has_more_facets_(facet, limit=None, exclude_active=False):
    '''


    '''
    facets = []
    for facet_item in c.search_facets.get(facet)['items']:
        if not len(facet_item['name'].strip()):
            continue
        if not (facet, facet_item['name']) in request.params.items():
            facets.append(dict(active=False, **facet_item))
        elif not exclude_active:
            facets.append(dict(active=True, **facet_item))
    if c.search_facets_limits and limit is None:
        limit = c.search_facets_limits.get(facet) + 1
    if limit is not None and len(facets) > limit:
        return True
    return False


def get_external_class(url):
    domain = config['ckan.site_url']  # check it
    log.warning(" domain is %s,  url is %s" % (domain, url))
    if (not domain in url):
        return "class = external-link"
    else:
        return ""


def get_new_uri_with_class(uri_link):
    # extract the link

    href_elem = re.match('.*href="(.*)" rel', uri_link).group(1)
    # href_elem = uri_link
    external_class = get_external_class(href_elem)
    new_link = uri_link.replace("href", external_class + " href")
    return new_link


def get_package_count():
    start = time.time()
    key_cache = ''
    if c.user:
        key_cache = "global_package_count_{0}".format(c.user)
    else:
        key_cache = "global_package_count"
    package_count = cache.get_from_cache(key_cache, pool=cache.MISC_POOL)
    if not package_count:
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj, 'for_view': True}
        data_dict = {
            'q': '*:*',
            'facet.field': g.facets,
            'rows': 4,
            'start': 0,
            'sort': 'views_recent desc',
            'fq': 'capacity:"public"'
        }
        package_count = 0
        try:
            query = logic.get_action('package_search')(
            context, data_dict)
        except Exception as e:
            log.error("Search error {0}".format(e.message))
            import traceback
            log.error(traceback.print_exc())
            return 0
        search_facets = query['search_facets'] or []
        package_count = query['count'] or 0
        cache.set_value_in_cache(key_cache, package_count, pool=cache.MISC_POOL)
    duration = time.time() - start
    log.info("Build package_count took {0}".format(duration))
    return package_count


def get_controller_category(controller):
    from ckanext.ecportal.plugin import ODP_CONTROLLERS
    controller_name = controller.controller
    if controller_name not in ODP_CONTROLLERS:
        return controller_name
    controller_base_name = controller_name.split(':')[0].split('.')[-1]
    return controller_base_name


def has_accepted_cookies():
    cookies = Cookie.SimpleCookie(request.headers.environ.get("HTTP_COOKIE")).values()
    for cookie in cookies:
        if cookie.key == "cookie-agreed":
            return True
    return False


def check_access(action, data_dict=None):
    context = {'model': model,
               'user': c.user or c.author,
               'package': c.package or None}
    if not data_dict:
        data_dict = {}
    try:
        logic.check_access(action, context, data_dict)
        authorized = True
    except logic.NotAuthorized:
        authorized = False

    return authorized


def check_access_create_catalog():
    context = {'model': model,
               'user': c.user or c.author,
               'package': c.package or None}

    data_dict = {}
    try:
        authorized = True
    except logic.NotAuthorized:
        authorized = False

    return authorized


def translate_controlled_vocabulary(graph, vocabulary_uri, model_property, rdf_type):
    #translations = _get_translation([graph], vocabulary_uri, model_property, current_locale().language,
    #                                {'0': SchemaGeneric(rdf_type)})
    factory = ControlledVocabularyFactory()
    translations = factory.get_translation_from_uri(vocabulary_uri, current_locale().language)
    return translations
    #if translations:
    #    return translations[0]


def get_all_languages():
    return c.languages

#def get_all_languages():
#    return retrieve_all_languages(current_locale().language)


def get_all_status():
    return c.status


def get_all_formats():
    return c.formats


def get_all_eurovoc_domains():
    return c.domains_eurovoc


def get_all_themes():
    return c.domains_eurovoc


def get_all_licenses():
    return c.license


def get_all_licenses():
    return retrieve_all_licenses(current_locale().language)


def is_dict_empty(data_dict):
    if data_dict != None and len(data_dict)>0:
        return False
    else:
        return True


def get_organization(data_dict):
        '''
        Retrieve the name of an organization
        '''
        query = ""

        if "id" in data_dict:
                query = model.Session.query(model.Group.name, model.Group.title). \
                filter(model.Group.is_organization == True). \
                filter(model.Group.state != 'deleted'). \
                filter(model.Group.id == data_dict.get("id"))
        elif "name" in data_dict:
                query = model.Session.query(model.Group.name, model.Group.title). \
                filter(model.Group.is_organization == True). \
                filter(model.Group.state != 'deleted'). \
                filter(model.Group.name == data_dict.get("name"))

        user_orgs_ids = map(lambda tup: tup, query.all()[0])
        return user_orgs_ids


def load_json_ld(file_path, **vars):
    """
    Generate json-ld script by the file name and its variables if necessary
    :param str: file_path the path of the json+ld template file
    :param vars: Generic parameters required for the json_ld file
    :return str: The generated JSON-LD script tag.
    """
    with open(file_path) as file_:
        template = Template(file_.read())
    return template.render(vars)


def load_breadcrumb_item_json_ld(pos, name, url):
    """
    Generate json-ld item for breadcrumb list
    :return: a JSON item to put into a breadcrumb list (JSON-LD)
    """
    DATA_FOLDER = config.get("ckan.data_folder",
                             CKAN_PATH + '/ckanext-ecportal/data')
    file_path = DATA_FOLDER + '/breadcrumb_item.template.json'
    return load_json_ld(file_path, pos=pos, name=name, url=url)

def get_users_organizations_ids(user):
        '''
        Retrieve all organizations of which the given user is a member
        '''

        query = model.Session.query(model.Group.id). \
            join(model.Member, model.Member.group_id == model.Group.id). \
            filter(model.Group.is_organization == True). \
            filter(model.Group.state != 'deleted'). \
            filter(model.Member.table_name == 'user'). \
            join(model.User, model.User.id == model.Member.table_id). \
            filter(model.User.name == user)

        user_orgs_ids = map(lambda tup: tup[0], query.all())
        return user_orgs_ids


def load_json_ld(file_path, **vars):
    """
    Generate json-ld script by the file name and its variables if necessary
    :param str: file_path the path of the json+ld template file
    :param vars: Generic parameters required for the json_ld file
    :return str: The generated JSON-LD script tag.
    """
    with open(file_path) as file_:
        template = Template(file_.read())
    return template.render(vars)

def load_opoce_json_ld():
    """
    Generate json-ld script by the file name and its variables if necessary
    :return str: The generated JSON-LD script tag.
    """
    DATA_FOLDER = config.get("ckan.data_folder", CKAN_PATH + '/ckanext-ecportal/data')
    file_path = DATA_FOLDER + '/opoce_json-ld.template.json'
    return load_json_ld(file_path, opoce=_('ecodp.opoce'), locale=current_locale())




