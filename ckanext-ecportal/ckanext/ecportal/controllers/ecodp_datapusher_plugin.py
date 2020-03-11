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

import ckan.plugins as p
import ckan.lib.base as base
import ckan.lib.helpers as core_helpers
import ckanext.datapusher.logic.action as action
import ckanext.datapusher.logic.auth as auth
import ckanext.datapusher.helpers as helpers
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_distribution_schema import DistributionSchemaDcatApOp, DocumentSchemaDcatApOp

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

DEFAULT_FORMATS = ['csv', 'xls', 'application/csv', 'application/vnd.ms-excel']


class DatastoreException(Exception):
    pass


class ECODPDatapusherPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceUrlChange)
    p.implements(p.IDomainObjectModification, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IRoutes, inherit=True)

    legacy_mode = False
    resource_show_action = None

    def configure(self, config):
        self.config = config

        datapusher_formats = config.get('ckan.datapusher.formats', '').lower()
        self.datapusher_formats = datapusher_formats.split() or DEFAULT_FORMATS

        for config_option in ('ckan.site_url', 'ckan.datapusher.url',):
            if not config.get(config_option):
                raise Exception(
                    'Config option `{0}` must be set to use the DataPusher.'
                    .format(config_option))

    def notify(self, entity, operation=None):
        if isinstance(entity, DistributionSchemaDcatApOp) or isinstance(entity, DocumentSchemaDcatApOp):
            # if operation is None, resource URL has been changed, as
            # the notify function in IResourceUrlChange only takes
            # 1 parameter
            context = {'model': model, 'ignore_auth': True,
                       'defer_commit': True}

            if not entity.format_dcterms:
                return

            if entity.format_dcterms['0'].uri.split('/')[-1].lower() in self.datapusher_formats:
                try:
                    p.toolkit.get_action('datapusher_submit')(context, {
                        'resource_id': entity.uri
                    })
                except p.toolkit.ValidationError, e:
                    # If datapusher is offline want to catch error instead
                    # of raising otherwise resource save will fail with 500
                    log.critical(e)
                    pass

    def before_map(self, m):
        m.connect(
            'resource_data', '/dataset/{id}/resource_data/{resource_id}',
            controller='ckanext.datapusher.plugin:ResourceDataController',
            action='resource_data', ckan_icon='cloud-upload')
        return m

    def get_actions(self):
        return {'datapusher_submit': action.datapusher_submit,
                'datapusher_hook': action.datapusher_hook,
                'datapusher_status': action.datapusher_status}

    def get_auth_functions(self):
        return {'datapusher_submit': auth.datapusher_submit,
                'datapusher_status': auth.datapusher_status}

    def get_helpers(self):
        return {
            'datapusher_status': helpers.datapusher_status,
            'datapusher_status_description':
            helpers.datapusher_status_description,
        }
