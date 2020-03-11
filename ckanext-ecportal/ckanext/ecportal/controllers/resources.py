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

import ckan.controllers.package as ckan_package
from ckan.lib.base import request
from pylons import config
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_func

from ckan.lib.base import model, abort, render
from ckan.logic import get_action, check_access
from pylons.i18n import _
import ckan.plugins.toolkit as tk
import ujson as json
from ckan.logic import NotFound, NotAuthorized

from ckanext.ecportal.lib.controlled_vocabulary_util import Distribution_controlled_vocabulary, Documentation_controlled_vocabulary

log = logging.getLogger(__name__)


class ECPortalEditResourceController(ckan_package.PackageController):

    RESOURCES_TYPES = [
		[Documentation_controlled_vocabulary.DOCUMENTATION_MAIN, _('Documentation: Main')],
        [Documentation_controlled_vocabulary.DOCUMENTATION_RELATED, _('Documentation: Related')],
        [Documentation_controlled_vocabulary.WEBPAGE_RELATED, _('Documentation: Webpage')],
        [Distribution_controlled_vocabulary.FEED_INFO, _('Distribution: Feed')],
        [Distribution_controlled_vocabulary.WEB_SERVICE, _('Distribution: Web Service')],
        [Distribution_controlled_vocabulary.DOWNLOADABLE_FILE, _('Distribution: Download')],
        [Distribution_controlled_vocabulary.VISUALIZATION, _('Visualization')]
	];
    def editresources(self, id, data=None, errors=None, error_summary=None):
        c = tk.c
        package_type = self._get_package_type(id)
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'extras_as_string': True,
                   'save': 'save' in request.params,
                   'moderated': config.get('moderated'),
                   'pending': True}

        if context['save'] and not data:
            return self._save_edit(id, context)
        try:
            context['for_edit'] = False
            old_data = get_action('package_show')(context, {'id': id})
            c.pkg_dict = old_data
            # old data is from the database and data is passed from the
            # user if there is a validation error. Use users data if there.
            data = data or old_data
        except NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % '')
        except NotFound:
            abort(404, _('Dataset not found'))

        c.pkg = context.get("package")
        c.resources_json = json.dumps(data.get('resources', []))

        try:
            check_access('package_update', context)
        except NotAuthorized, e:
            abort(401, _('User %r not authorized to edit %s') % (c.user, id))

        errors = errors or {}
        data['resources_types'] = self.RESOURCES_TYPES;
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary}
        c.errors_json = json.dumps(errors)

        self._setup_template_variables(context, {'id': id},
                                       package_type=package_type)
        c.related_count = c.pkg.related_count

        # TODO: This check is to maintain backwards compatibility with the
        # old way of creating custom forms. This behaviour is now deprecated.
        if hasattr(self, 'package_form'):
            c.form = render(self.package_form, extra_vars=vars)
        else:
            c.form = render(self._package_form(package_type=package_type),
                            extra_vars=vars)

        return render('package/editresources.html')

    def download_ressource(self, data=None, errors=None, error_summary=None):
        from ckan.lib.search import rebuild
        '''
        This function is called when a download of a resource is done.
        It increment a counter for this resource.
        '''
        data = self.__transform_to_data_dict(request.POST)

        model.Session.execute('''
        WITH upsert AS (
        UPDATE resource_download_count SET resource_count=resource_count+1 WHERE resource_id = :id  RETURNING *) 
        INSERT INTO resource_download_count (resource_id, resource_count, dataset_id) 
        SELECT :id, 1 , :ds_id WHERE NOT EXISTS (SELECT * FROM upsert);
        commit;
        ''', {'id': data['rs_uri'],
              'ds_id': data['ds_uri']})
        #rebuild(package_id=pkg_id)
        return 'OK'


    def __transform_to_data_dict(self, reqest_post):
        '''
        Transform the POST body to data_dict usable by the actions ('package_update', 'package_create', ...)
        :param the POST body of the request object
        :return: a dict usable by the actions
        '''

        # Initialize params dictionary
        data_dict = logic.parse_params(reqest_post)

        for key in data_dict.keys():
            if 'template' in key:
                data_dict.pop(key, None)

        # Transform keys like 'group__0__key' to a tuple (like resources, extra fields, ...)
        try:
            data_dict = logic.tuplize_dict(data_dict)
        except Exception, e:
            log.error(e.message)

        # Collect all tuplized key groups in one key containing a list of dicts
        data_dict = dict_func.unflatten(data_dict)
        data_dict = logic.clean_dict(data_dict)

        return data_dict