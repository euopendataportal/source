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

import ckan.new_authz as new_authz
import ckan.logic as logic

from ckan.common import _
from ckanext.ecportal.action.auth import (get_package_object)
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp, SchemaGeneric

@logic.auth_allow_anonymous_access
def package_show(context, data_dict):
    user = context.get('user')
    package = get_package_object(context, data_dict) # type: DatasetDcatApOp
    # draft state indicates package is still in the creation process
    # so we need to check we have creation rights.

    pkg_uri = None

    if isinstance(package, dict):
        pkg_uri = package.get('dataset').get('uri', None)
    else:
        pkg_uri = package.dataset_uri

    if pkg_uri is None:
        return {'success': True}
    else:
        # anyone can see a public package
        if package.privacy_state == 'public':
            return {'success': True}
        owner_org = package.schema.publisher_dcterms.get('0', ' / ').uri.split('/')[-1].lower()
        authorized = new_authz.has_user_permission_for_group_or_org(
            owner_org, user, 'read')
    if not authorized:
        return {'success': False, 'msg': _('User %s not authorized to read package %s') % (user, package.dataset_uri)}
    else:
        return {'success': True}


@logic.auth_allow_anonymous_access
def package_revision_list(context, data_dict):
    return package_show(context, data_dict)