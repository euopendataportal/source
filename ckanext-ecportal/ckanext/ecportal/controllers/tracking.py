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
import urllib2
import hashlib

import ckan.logic as logic
import ckan.lib.base as base
import ckan.model as model

from ckan.common import request, c, g, response

log = logging.getLogger(__name__)


class ECODPTrackingController(base.BaseController):


    def tracking(self):
        # do the tracking
        # get the post data
        payload = request.body
        parts = payload.split('&')
        data = {}
        for part in parts:
            k, v = part.split('=')
            data[k] = urllib2.unquote(v).decode("utf8")
        # start_response('200 OK', [('Content-Type', 'text/html')])
        response.headers['Content-Type'] ='text/html'

        # we want a unique anonomized key for each user so that we do
        # not count multiple clicks from the same user.
        if not request._headers:
            log.warn('Could not track request, no headers found')
            return
        try:
            key = ''.join([
                request._headers.environ['HTTP_USER_AGENT'],
                request._headers.environ['REMOTE_ADDR'],
                request._headers.environ.get('HTTP_ACCEPT_LANGUAGE', ''),
                request._headers.environ.get('HTTP_ACCEPT_ENCODING', ''),
            ])
        except Exception as e:
            import traceback
            log.error(traceback.print_exc())
            return

        key = hashlib.md5(key).hexdigest()
        # store key/data here
        sql = 'INSERT INTO tracking_raw (user_key, url, tracking_type) VALUES (:key, :url, :type); commit;'
        model.Session.execute(sql, {'key': key, 'url': data.get('url'), 'type': data.get('type')})
        return ['Tracked']
