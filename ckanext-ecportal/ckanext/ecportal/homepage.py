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
import ujson as json
import sqlalchemy.exc
import pylons.config
import pylons
import urllib

import pylons.config as ecportal_config
import ckan.model as model
import ckan.plugins as p
import ckan.config.routing as routing
import ckanext.multilingual.plugin as multilingual
import ckan.plugins.toolkit as tk
import ckan.logic as logic



import ckanext.ecportal.searchcloud as searchcloud
import ckanext.ecportal.helpers as helpers
import ckanext.ecportal.unicode_sort as unicode_sort
import time

log = logging.getLogger(__file__)
UNICODE_SORT = unicode_sort.UNICODE_SORT

LANGS = ['en', 'fr', 'de', 'it', 'es', 'pl', 'ga', 'lv', 'bg',
         'lt', 'cs', 'da', 'nl', 'et', 'fi', 'el', 'hu', 'mt',
         'pt', 'ro', 'sk', 'sl', 'sv', 'hr']

KEYS_TO_IGNORE = ['state', 'revision_id', 'id',  # title done seperately
                  'metadata_created', 'metadata_modified', 'site_id',
                  'data_dict', 'rdf']

NUM_MOST_VIEWED_DOMAINS = int(ecportal_config.get('ckan.eurovoc_domains.hompage', 8))
domains = {}
domains_translations = None

class ECPortalHomepagePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable)
    p.implements(p.ITemplateHelpers)

    home_content = None
    maintenance = None
    eurostats_compatible_datasets = None

    def _read_json_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return json.loads(f.read())
        except IOError, e:
            log.warn('Cannot open homepage content JSON file {0}'.format(file_path))
            log.warn(e)
        except ValueError, e:
            log.warn('Cannot load homepage content JSON file {0}'.format(file_path))
            log.warn(e)

    def configure(self, config):
        content_path = config.get('ckan.home.content')
        if content_path:
            log.info('Reading homepage content from {0}'.format(content_path))
            self.home_content = self._read_json_file(content_path)

        maintenance_path = config.get('ckan.home.maintenance')
        if maintenance_path:
            log.info('Reading maintenance message from {0}'.format(maintenance_path))
            self.maintenance = self._read_json_file(maintenance_path)

        eurostats_compatible_datasets_path = config.get('ckan.eurostats.compatible.datasets')
        if eurostats_compatible_datasets_path:
            log.info('Reading eurostats widget compatibles datasets from {0}'.format(eurostats_compatible_datasets_path))
            self.eurostats_compatible_datasets = self._read_json_file(eurostats_compatible_datasets_path)

    def get_helpers(self):
        return {
                'homepage_content': self.homepage_content,
                'maintenance_message': self.maintenance_message,
                'eurostats_compatible_datasets': self.eurostats_compatible_datasets_list,
                'get_eurovoc_domains': get_eurovoc_domains,
                'get_eurovoc_domains_by_packages_with_cache': get_eurovoc_domains_by_packages_with_cache,
                'get_groups': get_groups
                }

    def eurostats_compatible_datasets_list(self):
        if self.eurostats_compatible_datasets:
            return {'datasets': self.eurostats_compatible_datasets.get('datasets')}

    def homepage_content(self, language='en'):
        if self.home_content:
            title = (self.home_content.get('title', {}).get(language) or self.home_content.get('title', {}).get('en'))
            body = (self.home_content.get('body', {}).get(language) or self.home_content.get('body', {}).get('en'))
            return {'title': title, 'body': p.toolkit.literal(body)}

    def maintenance_message(self, language='en'):
        if self.maintenance:
            message = (self.maintenance.get('message', {}).get(language) or self.maintenance.get('message', {}).get('en'))
            maintenance_class = self.maintenance.get('class', 'red')
            return {'message': message, 'class': maintenance_class}

def get_groups(sort = 'display_name'):
    '''retrieves the number of datasets associated with each tag for a given vocabulary.'''
    context = {'model': model, 'session': model.Session, 'for_view': True,
        'user': tk.c.user or tk.c.author}
    solr_sort = 'name' if sort == 'display_name' else sort
    data_dict = {"all_fields": "True", "sort": solr_sort, 'type':u'group'}
    groups = logic.get_action('group_list')(context, data_dict)
    if sort == 'display_name':
        groups = sorted(groups, key=lambda x: x['display_name'])
    return groups


def get_eurovoc_domains(sort = 'display_name', q=''):
    '''retrieves the number of datasets associated with each tag for a given vocabulary.'''
    context = {'model': model, 'session': model.Session, 'for_view': True,
        'user': tk.c.user or tk.c.author}
    solr_sort = 'name' if sort == 'display_name' else sort
    data_dict = {"all_fields": "True", "sort": solr_sort, 'type':u'eurovoc_domain', 'q':q}
    eurovoc_domains = logic.get_action('domain_list')(context, data_dict)
    if sort == 'display_name':
        eurovoc_domains = sorted(eurovoc_domains, key=lambda x: x['display_name'])
    for domain in eurovoc_domains:
        domain['uri'] = urllib.quote_plus('http://eurovoc.europa.eu/{0}'.format(domain.get('name').split('_')[-1]))
        domain['url'] = 'http://eurovoc.europa.eu/{0}'.format(domain.get('name').split('_')[-1])
    return eurovoc_domains

def get_eurovoc_domains_by_packages_with_cache(mode = 'all', locale='en'):
    ''' use for the display of domains on the front page'''
    start = time.time()

    global domains
    if locale not in domains.keys():
        domains[locale] = get_eurovoc_domains('packages')

    if  not  domains[locale]:
        request_locale = tk.request.environ['CKAN_LANG']
        tk.request.environ['CKAN_LANG'] = 'en'
        domains[locale] = get_eurovoc_domains('packages')
        tk.request.environ['CKAN_LANG'] = request_locale


    if mode == 'most_common':
        duration = time.time()-start
        log.info("BUILD eurovoc_domaine took {0}".format(duration))
        return domains[locale][:NUM_MOST_VIEWED_DOMAINS]
    elif mode == 'less_common':
        duration = time.time() - start
        log.info("BUILD eurovoc_domaine took {0}".format(duration))
        return domains[locale][NUM_MOST_VIEWED_DOMAINS:]
    else:
        return domains[locale]
