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

import ckan.lib.navl.dictization_functions
import logging
import sqlalchemy

import ckan.plugins as plugins
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.lib.dictization.model_dictize as model_dictize

from solr import SolrException
from ckan.lib.search.common import make_connection, SearchError
from pylons import config
from ckan.common import _, json


check_access = logic.check_access
render = base.render
abort = base.abort
redirect = base.redirect
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

log = logging.getLogger(__name__)
_validate = ckan.lib.navl.dictization_functions.validate
_check_access = logic.check_access
_and_ = sqlalchemy.and_

QUERY_FIELDS = "name^4 title^4 tags^2 groups^2 text"


def change_selected_datasets( context, data_dict):
    '''
    This function stores the change of selected datasets on the dashboard
    :param context:
    :param data_dict:
    :return:
    '''


    return

def unselect_all_dataset( context, data_dict):

    if not context['user']:
        return 0


    return 0
