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

import ckan.lib.cli as cli
from ckanext.sitemap.controller import SitemapController

log = logging.getLogger(__name__)

class InitSitemapFiles(cli.CkanCommand):
    '''Perform commands to load the sitemap files

    Usage::

        paster sitemap reload

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):

        super(InitSitemapFiles, self).__init__(name)

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print InitSitemapFiles.__doc__
            return

        self._load_config()
        cmd = self.args[0]

        if cmd == 'reload':
            sitemap = SitemapController()
            sitemap.reload_all_sitemaps()
        else:
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return