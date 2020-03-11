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

'''
Customised authorization for the ecportal extension.
'''

import ckan.lib.base as base
import ckan.new_authz as authz
import ckan.logic as logic

from pylons import config
from ckan.common import _
from ckanext.ecportal.lib.ui_util import transform_dcat_schema_to_form_schema

abort = base.abort

def _sysadmins_only(context, action_string):
    user = context['user']

    if authz.Authorizer().is_sysadmin(unicode(user)):
        return {'success': True}

    return {'success': False,
            'msg': 'You are not authorized to {0}'.format(action_string)}


def group_create(context, data_dict=None):
    '''
    Only sysadmins can create Groups.

    All the Groups are created through the API using a paster command.  So
    there's no need for non-sysadmin users to be able to create new Groups.
    '''
    user = context['user']

    if not user:
        return {'success': False,
                'msg': 'User is not authorized to create groups'}

    if user and authz.is_sysadmin(user):
        return {'success': True}
    else:
        return {'success': False,
                'msg': 'User is not authorized to create groups'}

def group_edit(context, data_dict):
    return _sysadmins_only(context, 'edit groups')


@logic.auth_sysadmins_check
def package_update(context, data_dict):
    '''
    Customised package_update auth overrides default ckan behaviour.

    Packages that have been imported by the RDF importer should not be edited
    via the web interface.  But obviously, they need to be updateable via the
    API.

    RDF-imported packages are identified by having an 'rdf' field.
    '''
    # return {'success': True}
    is_sysadmin = context.get('auth_user_obj').sysadmin

    if is_sysadmin:
        return {'success': True}
    else:
        if data_dict:
            user_object = context.get('auth_user_obj')
            if user_object.get_groups('organization'):
                if not context.get('package'):
                    logic.get_action('package_show')(context, data_dict)

                dataset = context.get('package')
                organizations = logic.get_action('organization_list_for_user')(context, {'permission': 'manage_group'})
                for org in organizations:
                    if org.get('name') == dataset.schema.publisher_dcterms.get('0').uri.split('/')[-1].lower():
                        return {'success': True}

    return {'success': False}

        # authorised_by_core = publisher_auth.update.package_update(
        #     context, data_dict)
        # if authorised_by_core['success'] is False:
        #     return authorised_by_core
        # elif 'api_version' in context:
        #     return authorised_by_core
        # else:
        #     package = ckan_auth.get_package_object(context, data_dict)
        #     if 'rdf' in package.extras:
        #         return {
        #             'success': False,
        #             'msg': 'Not authorized to edit RDF-imported datasets by hand. '
        #                    'Please re-import this dataset instead.'
        #         }
        #     else:
        #         return authorised_by_core


def purge_publisher_datasets(context, data_dict):
    '''
    Only sysadmins can purge a publisher's deleted datasets.
    '''
    return _sysadmins_only(context, 'purge publisher datasets')


def purge_revision_history(context, data_dict):
    '''
    Only sysadmins can purge a publisher's revision history.
    '''
    return _sysadmins_only(context, 'purge revision history')


def purge_package_extra_revision(context, data_dict):
    '''
    Only sysadmins can remove old data from the package_extra_revision table.
    '''
    return _sysadmins_only(context, 'purge package extra revision')


def purge_task_data(context, data_dict):
    '''
    Only sysadmins can remove old task data.
    '''
    return _sysadmins_only(context, 'purge task data.')


def show_package_edit_button(context, data_dict):
    '''
    Custom ecportal auth function.

    This auth function is only used in one place: on the package layout
    template.  Its sole purpose is to determine whether to display the edit
    button for a given package.  This is determined by the core (default) ckan
    auth layer.  This allows the edit button to be displayed for RDF-imported
    datasets, even though the user won't have the rights to edit an
    RDF-imported dataset (see `package_update` auth above).  This allows the
    edit button to be displayed, but de-activated: giving the user feedback
    on how to update the dataset (ie - re-running the import).
    '''
    return package_update(context, data_dict)


def package_search_private_datasets(context, data_dict):
    '''
    Custom ecportal auth function.

    Used in ecportal package_search to see if a user has permission to
    view private datasets in group search listings.

    Only applies to sysadmins for now, as group members can already
    see private datasets in the search listing (sysadmins cannot).
    '''
    return _sysadmins_only(context, 'view private datasets')


def user_create(context, data_dict=None):
    '''
    Only allow sysadmins to create new Users
    '''
    return _sysadmins_only(context, 'create new users')


def rdft_package_update(context, data_dict):
    '''
    The ecportal extension does not allow ingested packages (i.e.: packages with an 'rdf' property) to be
    modified manually.
    So, we re-apply the standard behaviour of function 'package_update' for the metadatatool scope because
    we want to keep the ecportal restriction for the exportal dataset edit page but we don't want it for the
    metadatatool dataset edit page.

    Overwriting the 'package_update' action again would cause collision; it's not possible to overwrite the
    same action in more than 1 extension.
    So, we "mask" the 'package_update' functionality in the metadatatool with 'mdt_package_update'. Behind
    the scenes, CKAN's standard 'package_update' action is used.
    '''
    return package_update(context, data_dict)


@logic.auth_allow_anonymous_access
def openness(context, data_dict=None):

    if 'false' ==  config.get('ecodp.openness_enabled', 'False').lower():
        abort(404, _('ODP openness report is not activated'))

    return {'success': True}