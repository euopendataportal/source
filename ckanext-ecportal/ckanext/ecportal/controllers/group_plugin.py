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


import ckan.plugins as plugins
import ckanext.ecportal.lib.groups_util as util
import ckan.logic.action.update as update


class ECODPGroupPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IGroupController)

    def create(self, entity):
        #This hook in to 'group_create' action after the group is safed
        entity.revision.current  = True
        entity.save()
        util.add_all_users_to_new_group(entity)


        return

    def read(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def before_view(self, pkg_dict):
        return pkg_dict