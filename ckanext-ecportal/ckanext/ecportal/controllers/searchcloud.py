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

import datetime
import ckan.lib.base as base
import ckan.plugins.toolkit as tk
import json
import ckanext.ecportal.searchcloud as searchcloud
import ckan.model as model
import ckan.new_authz as new_authz

from pylons import response

class SearchCloudException(Exception):
    pass


class ECPortalSearchCloudAdminController(base.BaseController):
    '''
    Allow a sysadmin to download the latest list of terms
    '''
    # Can't do this check in __before__ as tk.c.user is not yet set up
    def _sysadmin_or_abort(self):
        user = tk.c.user
        if not user:
            return base.abort(401, 'Not signed in')
        is_admin = new_authz.is_sysadmin(unicode(user))
        if not is_admin:
            return base.abort(
                401,
                'You are not authorized to access search cloud administation'
            )

    def index(self):
        self._sysadmin_or_abort()
        return tk.render('searchcloud/index.html')

    def _parse_json(self, json_data):
        try:
            rows = json.loads(json_data)
        except:
            raise SearchCloudException(
                'JSON file could not be parsed. Please ensure file is valid'
                ' JSON and pay careful attention to trailing commas.'
            )
        else:
            values = []
            if not isinstance(rows, list):
                raise SearchCloudException(
                    'JSON file does not contain a list of terms. Expected the'
                    ' same format as the download.'
                )
            for i, row in enumerate(rows):
                if not isinstance(row, list):
                    raise SearchCloudException(
                        ('Row %i has a value %r. It is not a list of'
                         ' [search_string, count]. Expected the same format'
                         ' as the download.') % (i, row,)
                    )
                try:
                    count = int(row[1])
                except:
                    raise SearchCloudException(
                        'Could not parse the count for row %s' % (i,)
                    )
                else:
                    if not row[0].strip():
                        raise SearchCloudException(
                            "Row %i doesn't contain a search string" % (i,)
                        )
                    values.append([row[0].strip(), count])
            return values

    def upload(self):
        self._sysadmin_or_abort()
        if tk.request.method == 'GET':
            return tk.render('searchcloud/upload.html')
        else:
            file_field = tk.request.POST['searchcloud']
            try:
                data = file_field.value.decode('utf8')
                rows = self._parse_json(data)
            except (UnicodeDecodeError, SearchCloudException) as e:
                tk.c.error = str(e)
                return tk.render('searchcloud/error.html')
            else:
                tk.c.json = searchcloud.approved_to_json(rows)
                tk.c.data = data
                return tk.render('searchcloud/preview.html')

    def save(self):
        self._sysadmin_or_abort()
        data = tk.request.POST['searchcloud']
        try:
            rows = self._parse_json(data)
        except SearchCloudException, e:
            tk.c.error = str(e)
            return tk.render('searchcloud/error.html')
        else:
            searchcloud.update_approved(model.Session, rows)
            # Save our changes
            model.Session.commit()
            return tk.render('searchcloud/saved.html')

    def download(self):
        self._sysadmin_or_abort()
        data = searchcloud.get_latest(model.Session)
        # We don't know when the script is run, so let's assume just
        # after midnight and use today's date
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        response.charset = 'utf8'
        response.content_type = 'application/json'
        response.headers['Content-Disposition'] = \
            'attachment; filename="ecodp-searchcloud-latest-%s.json"' % date
        return json.dumps(data, indent=4)
