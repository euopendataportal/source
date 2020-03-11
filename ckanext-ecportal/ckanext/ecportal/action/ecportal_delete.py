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

import ckan.logic
import ckan.logic.action
import ckan.plugins as plugins
from sqlalchemy import or_
from ckanext.ecportal.lib.search.dcat_index import PackageSearchIndex
from ckanext.ecportal.model.identifier_mapping import DatasetIdMapping

import ckanext.ecportal.lib.cache.redis_cache as redis_cache
from ckan.common import _

NotFound = ckan.logic.NotFound
NotAuthorized = ckan.logic.NotAuthorized
_check_access = ckan.logic.check_access
_get_action = ckan.logic.get_action

package_index = PackageSearchIndex()


def package_delete(context, data_dict):
    '''Delete a dataset (package).

    You must be authorized to delete the dataset.

    :param id: the id or name of the dataset to delete
    :type id: string

    '''
    model = context['model']
    user = context['user']

    _get_action('package_show')(context, data_dict)

    entity = context['package']  # type: DatasetDcatApOp

    if entity is None:
        raise NotFound

    _check_access('package_delete', context, data_dict)

    if entity.has_doi_identifier():
        raise NotAuthorized('Cannot delete a dataset with a DOI.')

    rev = model.repo.new_revision()
    rev.author = user
    rev.message = _(u'REST API: Delete Package: %s') % entity.dataset_uri

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.delete(entity)

        item.after_delete(context, data_dict)


    result = entity.delete_from_ts()
    if result:
        mapping = DatasetIdMapping.by_internal_id(entity.dataset_uri.split('/')[-1])
        if mapping:
            mapping.delete_from_db()
        redis_cache.delete_value_from_cache(entity.dataset_uri)
        redis_cache.flush_all_from_db(redis_cache.MISC_POOL)
        package_index.remove_dict(entity)
        model.repo.commit()
        return True
    else:
        return False

def organization_delete(context, data_dict):
    return _group_or_org_delete(context, data_dict)


def _group_or_org_delete(context, data_dict, is_org=False):
    '''Delete a group.

    You must be authorized to delete the group.

    :param id: the name or id of the group
    :type id: string

    '''
    model = context['model']
    user = context['user']
    id = data_dict.get('id')

    if not id:
        raise NotFound('No id provided')
    group = model.Group.get(id)
    context['group'] = group
    if group is None:
        raise NotFound('Group was not found.')

    revisioned_details = 'Group: %s' % group.name

    if is_org:
        _check_access('organization_delete', context, data_dict)
    else:
        _check_access('group_delete', context, data_dict)

    # organization delete will delete all datasets for that org
    if is_org and data_dict.get('packages', 0) > 0:
        packages = ckan.logic.get_action('package_search')(context, {'owner_org': id})
        for pkg in packages:
            package_delete(context, {'id': pkg.id})

    rev = model.repo.new_revision()
    rev.author = user
    rev.message = _(u'REST API: Delete %s') % revisioned_details

    # The group's Member objects are deleted
    # (including hierarchy connections to parent and children groups)
    for member in model.Session.query(model.Member). \
            filter(or_(model.Member.table_id == id,
                       model.Member.group_id == id)). \
            filter(model.Member.state == 'active').all():
        member.delete()

    group.delete()

    if is_org:
        plugin_type = plugins.IOrganizationController
    else:
        plugin_type = plugins.IGroupController

    for item in plugins.PluginImplementations(plugin_type):
        item.delete(group)

    model.repo.commit()
