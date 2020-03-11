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

import ckan.plugins.toolkit as tk



ign_missing = tk.get_validator('ignore_missing')
url_validator = tk.get_validator('url_validator')
to_extras = tk.get_converter('convert_to_extras')
from_extras = tk.get_converter('convert_from_extras')
not_empty = tk.get_validator('not_empty')

def dcat_ap_modify_package_schema():
    '''
    Use this function to specify the schema for create and update dataset funktions (UI/API)
    :return:
    '''
    schema = {}
    return schema


def dcat_ap_modify_resource_schema():
    '''
    Use this function to specify the schema for create and update resource funktions (UI/API)
    :return:
    '''

    schema = {}
    return schema

def dcat_ap_show_package_schema():
    '''
    Use this function to adapt the schema before it is shown to the USER (UI/API)
    :return:
    '''
    schema = {}

    return schema


def dcat_ap_show_resource_schema():
    '''
    Use this function to adapt the schema before it is shown to the USER (UI/API)
    :return:
    '''
    schema = {}

    return schema