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

from pylons import request, response

import ckan.plugins as plugins


class ECODPLogoutPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IAuthenticator)

    def identify(self):
        pass

    def login(self):
        '''called at login.'''
        pass

    def abort(self, status_code, detail, headers, comment):
        '''called on abort.  This allows aborts due to authorization issues
        to be overriden'''
        return (status_code, detail, headers, comment)

    def logout(self):

        request.cookies.pop('selected_datasets', None)
        response.set_cookie('selected_datasets', max_age=0)
        return