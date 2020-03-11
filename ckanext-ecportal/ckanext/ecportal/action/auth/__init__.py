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
Helper functions to be used in the auth check functions
'''

import ckan.logic as logic


def _get_object(context, data_dict, name, class_name):
    # return the named item if in the data_dict, or get it from
    # model.class_name
    try:
        return context[name]
    except KeyError:
         raise logic.NotFound



def get_package_object(context, data_dict=None):
    return _get_object(context, data_dict, 'package', 'Package')
