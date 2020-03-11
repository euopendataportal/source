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
import time

from ckan.controllers.api import ApiController
from ckan.common import _

import ckan.logic as logic

from ckanext.ecportal.lib.webtrends.webtrends_util import SendWebtrendsThread as webtrends_util

log = logging.getLogger(__name__)
get_action = logic.get_action

ACTION_MAPPING = {'package_show': 'legacy_package_show',
                   'package_save': 'not_found',
                  'term_translation_update_many': 'legacy_term_translation_update_many'
                  }

class ECPORTALApiController(ApiController):

    def legacy_action(self, logic_function, ver=None):
        start = time.time()
        logic_function = ACTION_MAPPING.get(logic_function, logic_function)

        try:
            function = get_action(logic_function)
        except KeyError:
            log.error('Can\'t find logic function: %s' % logic_function)
            return self._finish_bad_request(
                _('Action name not known: %s') % logic_function)

        side_effect_free = getattr(function, 'side_effect_free', False)
        request_data = {}
        try:
            request_data = self._get_request_data(try_url_params=
                                                  side_effect_free)
        except ValueError, inst:
            log.error('Bad request data: %s' % inst)
            #return self._finish_bad_request(
            #    _('JSON Error: %s') % inst

        query_result = super(ECPORTALApiController, self).action(logic_function, ver)

        wt = webtrends_util(request_data)
        wt.send_query(logic_function, query_result)
        wt.start()
        log.info('API function {0} took {1} sec'.format(logic_function, time.time() - start))
        return query_result


    def action(self, logic_function, ver=None):

        start = time.time()
        try:

            function = get_action(logic_function)
        except KeyError:
            log.error('Can\'t find logic function: %s' % logic_function)
            return self._finish_bad_request(
                _('Action name not known: %s') % logic_function)

        request_data = {}
        side_effect_free = getattr(function, 'side_effect_free', False)
        try:
            request_data = self._get_request_data(try_url_params=
                                                  side_effect_free)
        except ValueError, inst:
            log.error('Bad request data: %s' % inst)
            return self._finish_bad_request(
                _('JSON Error: %s') % inst)
        if not isinstance(request_data, dict):
            # this occurs if request_data is blank
            log.error('Bad request data - not dict: %r' % request_data)
            return self._finish_bad_request(
                _('Bad request data: %s') %
                'Request data JSON decoded to %r but '
                'it needs to be a dictionary.' % request_data)
        # if callback is specified we do not want to send that to the search
        if 'callback' in request_data:
            del request_data['callback']

        query_result = super(ECPORTALApiController, self).action(logic_function, ver)

        wt = webtrends_util(request_data)
        wt.send_query(logic_function, query_result)
        wt.start()
        log.info('API function {0} took {1} sec'.format(logic_function, time.time() - start))
        return query_result