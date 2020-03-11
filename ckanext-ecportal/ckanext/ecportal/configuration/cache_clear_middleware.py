# -*- coding: utf-8 -*-
# Copyright (C) 2018  Publications Office of the European Union

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>

import logging

import ckan.plugins as plugins
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

log = logging.getLogger(__name__)
CKAN_CACHE_DIR = CKAN_PATH + '/var/cache/'

class ECPortalCacheClearMiddelware(plugins.SingletonPlugin):
    plugins.implements(plugins.IMiddleware)

    def make_middleware(self, app, config):
        '''Return an app configured with this middleware
        Delete the cache of the beaker lib
        '''

        def safe_remove_cahce_file():
            '''
            Delete the files of the cache
            :return:
            '''
            from ckanext.ecportal.lib.cache.cache_util import CacheUtil
            CacheUtil().invalidate_cache()
            log.info("Remove cache files")
        safe_remove_cahce_file()
        return app

