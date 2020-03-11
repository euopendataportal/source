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
Sitemap plugin for CKAN
'''

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IRoutes

import ckan.config.routing as routing

class SitemapPlugin(SingletonPlugin):
    implements(IRoutes, inherit=True)

    def before_map(self, map):
        controller='ckanext.sitemap.controller:SitemapController'
        #with routing.SubMapper(map, controller=controller) as m:
        #    m.connect('sitemap', '/sitemap.xml', action='view')
        #    m.connect('sitemap', '/sitemap_{lang}_{number}.xml', action='one_result')
        #return map

