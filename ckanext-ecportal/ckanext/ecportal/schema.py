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

import ckan.lib.navl.validators as navl_validators
import ckan.logic.validators as core_validators

# changes from core:
# - username can be uppercase
# - email is not required


def default_user_schema(schema):
    schema.update({
        'name': [navl_validators.not_empty,
                 core_validators.user_name_validator,
                 unicode],
        'email': [navl_validators.default(u''),
                  unicode]
    })
    return schema


def default_update_user_schema(schema):
    schema.update({
        'name': [navl_validators.ignore_missing,
                 core_validators.user_name_validator,
                 unicode]
    })
    return schema
