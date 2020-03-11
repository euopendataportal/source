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

import json

import requests

from ckan.controllers.organization import OrganizationController
from ckan.common import OrderedDict, c, g, request, _
from urllib import urlencode
from pylons import config

import time
import logging
import ckan.model as model
import ckan.lib.base as base
import ckan.logic as logic
import ckan.new_authz as new_authz
import ckan.plugins as plugins
import ckan.lib.helpers as h
import ckan.lib.search as search
import ckan.lib.maintain as maintain
import ckanext.ecportal.lib.page_util as page_util
import ckanext.ecportal.lib.uri_util as uri_util
from ckanext.ecportal.helpers import resource_display_name
from ckanext.ecportal.configuration.configuration_constants import DATASET_URI_PREFIX
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import CorporateBodiesUtil

render = base.render
abort = base.abort
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
log = logging.getLogger(__name__)
ORGANIZATION_CONTROLLER = 'ckanext.ecportal.controllers.organization:ECODPOrganizationController'


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring)
    else str(v))
            for k, v in params]


class ECODPOrganizationController(OrganizationController):

    def _url_for(self, *args, **kw):
        '''
        Overwrite to use the publisher link, not organization (as derived from the core's group controller
        otherwise.
        '''
        if 'controller' in kw:
            kw['controller'] = 'ckanext.ecportal.controllers.organization:ECODPOrganizationController'
        return h.url_for(*args, **kw)

    def index(self, max_element=None):
        group_type = self._guess_group_type()

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'with_private': False}
        if c.user:
            context['with_private'] = True

        locale = request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        start = time.time()
        result = get_action('get_skos_hierarchy')(context, max_element)
        duration = time.time() - start

        factory = ControlledVocabularyFactory()
        publ_mdr = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.CORPORATE_BODY) #type: CorporateBodiesUtil

        for top_level, item in result.items():
            translation = publ_mdr.get_translation_for_language(top_level, locale)
            item['name'] = top_level.split('/')[-1].lower()
            item['label'] = translation
            interim = []
            for child in item.get('children', []):
                translation = publ_mdr.get_translation_for_language(child[0], locale)
                interim.append((child[0].split('/')[-1].lower(), translation, child[1]))

            item['children'] = sorted(interim, key=lambda child: child[1])

        log.info("get SKOS hierachy took {0}".format(duration))
        c.items = result
        return render(self._index_template(group_type))

    def _read(self, id, limit):
        ''' This is common code used by both read and bulk_process'''
        group_type = self._get_group_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        q = c.q  # = request.params.get('q', '')
        log.info('Organization read q: %s in organization: %s' % (q, c.group_dict.get('id', '')))
        if q != u'':
            result = ''
            if request.params.get('ext_boolean') == 'any':
                result = build_search_for_any_words(q)
                q = result
            elif request.params.get('ext_boolean') == 'exact':
                result = '"%s"' % (q)
                q = result
                log.info("%s" % (request.params.get('ext_boolean')))

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

        new_params_nopage = [];
        for key, value in params_nopage:
            if key == 'eurovoc_domains':
                new_params_nopage.append(('groups', value))
            else:
                new_params_nopage.append((key, value))

        # todo check why it is added
        # params_nopage = new_params_nopage;

        # sort_by = request.params.get('sort', 'name asc')
        sort_by = request.params.get('sort', None)

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

        def drill_down_url(**by):
            return h.add_url_param(alternative_url=None,
                                   controller='group', action='read',
                                   extras=dict(id=c.group_dict.get('name')),
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            if c.group_dict.get('is_organization'):
                # ORGANIZATION_CONTROLLER
                return h.remove_url_param(key, value=value, replace=replace,
                                          controller=ORGANIZATION_CONTROLLER, action='read',
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
                        # todo: facet group eurovoc doamin check why we replace eurovoc_domain with groups
                        # param = 'groups' if (param == 'eurovoc_domains') else param;
                        q += ' %s:"%s"' % (param, value)
                    else:
                        search_extras[param] = value

            # Search within group add group id herel
            if c.group_dict.get('is_organization'):
                q += ' owner_org:"%s"' % c.group_dict.get('id')
            elif c.group_dict.get('name') not in q:
                q += ' groups:"%s"' % c.group_dict.get('name')

            fq = 'capacity:"public"'
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

            context_ = dict((k, v) for (k, v) in context.items() if k != 'schema')
            query = get_action('package_search')(context_, data_dict)

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
            maintain.deprecate_context_item('facets',
                                            'Use `c.search_facets` instead.')

            c.search_facets = query['search_facets']
            c.search_facets_limits = {}
            for facet in c.facets.keys():
                limit = int(request.params.get('_%s_limit' % facet,
                                               g.facets_default_number))
                c.search_facets_limits[facet] = limit
            c.page.items = query['results']

            c.sort_by_selected = sort_by

        except search.SearchError, se:
            log.error('Organization search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.page = page_util.Page(collection=[])
            c.search_url_params = ''
        except ValueError, se:
            log.error('Organization search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.page = page_util.Page(collection=[])
            c.search_url_params = ''

        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)

    def broken_links(self):
        """
        Provides for each datasets of each organisations those number of broken links.
        :return:
        """
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        display_all = False

        try:
            display_all = request.params.get('display_all') == 'True'
        except Exception, e:
            pass

        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        c.display_all=display_all
        log.info('Started to display broken links: display_all={0}'.format('True' if display_all else 'False'))
        return base.render('organization/broken_links.html')

    def get_broken_links(self):
        """
        Get organisations with their datasets and dead links counts.
        :param str or None last_id: Identifier of the last displayed organisation (used for the query offset).
        :return: The list of organisations with all details about dead links.
        """

        display_all = False

        try:
            display_all = request.params.get('display_all') == 'True'
        except Exception, e:
            pass

        offset = 0
        if not display_all:
            try:
                offset = int(request.params.get('last_id'))+1
            except Exception, e:
                pass

        organisations_limit = int(config.get("ckan.linkchecker.organisations.limit", 2))

        context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'for_view': True,
                       'with_private': False}

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin
        start = time.time()
        organisations = self._action('organization_list')(context, {'all_fields': True, 'sort': 'name asc'})[offset:]
        log.info('Broken links get organizations took {0}s ({1} organizations fetched)'.format(time.time()-start, len(organisations)))
        context_ = dict((k, v) for (k, v) in context.items() if k != 'schema')

        output = []
        start = time.time()
        for index, organisation in enumerate(organisations):
            organisation['datasets'] = filter(lambda dataset: dataset.get('deadLinks', 0) > 0, _get_organisation_datasets(context_, organisation['id']))
            organisation['deadLinks'] = sum(dataset.get('deadLinks', 0) for dataset in organisation['datasets'])
            if organisation.get('deadLinks', 0) > 0:
                organisation['index'] = offset+index
                output.append(organisation)
            if not display_all:
                if len(output) >= organisations_limit:
                    break
        brokenlinks_count = sum(organisation.get('deadLinks', 0) for organisation in organisations)
        log.info('Broken links for loop took {0}s ({1} deadLinks fetched)'.format(time.time()-start, brokenlinks_count))
        start = time.time()
        reordered_org = sorted(output, key=lambda k: k['name'])
        log.info('Broken links reordered result took {0}s'.format(time.time()-start))

        noBrokenLinks_val = (offset == 0 and len(output) == 0)

        return base.render_snippet('organization/snippets/broken_links_list.html', organizations=reordered_org, noBrokenLinks=noBrokenLinks_val)


def _get_organisation_datasets(context, owner):
    """
    Get the list of datasets from an organisation.
    :param owner: The organisation's identifier "owner_org" related to the excepted datasets.
    :return: list of datasets related to the organisation.
    """
    dead_links = {}
    try:
        publisher = model.Group.get(owner)
        publisher_uri = uri_util.create_publisher_uri(publisher.name)
        dead_links = get_organisation_broken_links(publisher_uri)
    except Exception, e:
        log.error(e.message)
        pass

    datasets = []
    if len(dead_links) < 1:
        return datasets

    offset = 0
    limit = 1000

    # Fetch All organisation's datasets
    while True:
        query = get_action('package_search')(context, {'q': 'owner_org:' + owner, 'sort': 'id asc', 'rows': limit, 'start': offset*limit})

        if len(query['results']) <= 0:
            break

        datasets.extend(query['results'])

        if len(datasets) >= query['count']:
            break

        offset = offset + 1

    for dataset in datasets:
        dataset['links'] = []
        dataset['uri'] = DATASET_URI_PREFIX + '/' + dataset['id']
        if dataset['uri'] in dead_links:
            for resource in dataset.get('resources', []):
                for link in resource.get('access_url', []):
                    dataset['links'].append((link, resource_display_name(resource)))
                for link in resource.get('download_url', []):
                    dataset['links'].append((link, resource_display_name(resource)))
        _provide_datatsets_deadlinks_counts(dataset, dead_links)

    return datasets


def get_organisation_broken_links(uri):
    """
    Get all broken links from an organisation.
    :param str uri: the URI of the organisation.
    :return dict: Map with datasets' URI as keys and list of broken links as values.
    """

    try:
        request = requests.get(config.get('ckan.linkchecker.states.url', 'http://localhost:8080/organisation/dead-links'), headers={'Content-Type': 'application/json'}, params={"uri": uri}, verify=False)
    except Exception, e:
        raise Exception('Failed to check links: {0}'.format(e.message))

    if request.status_code == 200:
        result = json.loads(request.content)
        if u'datasets' in result:
            return result['datasets']
        else:
            raise Exception('Failed to check links: {0}'.format(request.content))
    else:
        raise Exception('Failed to check links: {0}'.format(request.content))


def _provide_datatsets_deadlinks_counts(dataset, links):
    """
    Add for a dataset the number of dead links.
    :param dict dataset: The dataset
    :param list links: The map of broken links.
    """
    if dataset['uri'] in links:
        dataset['links'] = filter(lambda tuple: tuple[0] in links[dataset['uri']]['links'], dataset['links'])

    dataset['deadLinks'] = len(dataset['links'])
    dataset['links'] = list(set(dataset['links']))


def build_search_for_any_words(search):
    result = ''
    for token in search.split():
        if result == '':
            result = '(%s' % (token)
        else:
            result = '%s OR %s' % (result, token)

    return result + ')'
