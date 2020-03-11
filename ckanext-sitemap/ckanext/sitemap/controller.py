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
Controller for sitemap
'''
import logging

import sys
import traceback
import os, time
import shutil
from ckan.lib.base import BaseController
from ckan.lib.helpers import url_for
import ckan.plugins as p
import ckan.lib.i18n as i18n
from lxml import etree
from pylons import config, response
import pylons.config as config

import urlparse
import psycopg2

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

init_dataset_number = 2000
init_sitemap_cache = '3'

log = logging.getLogger(__file__)
ckan_dataset_number = int(config.get('ckan.sitemap.dataset.number', init_dataset_number))
validity_duration = int(config.get('sitemap.cache.time',init_sitemap_cache)) #number of days
one_day = 86400


class SitemapController(BaseController):


    def _current_locale(self):
        return p.toolkit.request.environ['CKAN_LANG'] \
               or config.get('ckan.locale_default', 'en')

    def _generate_sitemap(self, conn, locale):
        # Connect to database and get all needed data
        try:
            cur = conn.cursor()
            cur.execute(
                "select distinct pr.name, rr.id, pr.metadata_modified as pr_date, COALESCE(rr.last_modified, rr.created) as rr_date "+
                "from package pr "+
                "join resource_group rg on rg.package_id = pr.id "+
                "join resource rr on rr.resource_group_id = rg.id "+
                "where rr.state = 'active' and pr.state = 'active' "+
                "order by 1"
            )
            rows = cur.fetchall()
            return self._construct_xml_tree(rows, locale)
        except Exception:
            log.error("Error while connecting to database")
            raise


    def _construct_xml_tree(self, rows, locale):
        file_number = 0
        count = 0
        dirpath = config.get('cache_dir','/applications/ecodp/users/ecodp/ckan/var/cache')
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        # Iterate over fetched data an construct the xml tree
        while count<len(rows):
            file_name = '/sitemap_' + locale + '_' + str(file_number) + '.xml'


            log.info("Generating %s" % file_name)
            print "Generating %s" % file_name

            filepath = dirpath + file_name
            iteration = 1
            currentPackage = ''
            root = etree.Element("urlset", nsmap={None: SITEMAP_NS})
            for row in rows[count:]:
                packageName = row[0]
                resourceId = row[1]
                packageDate = row[2]
                resourceDate = row[3]
                if currentPackage != packageName:
                    url = etree.SubElement(root, 'url')
                    loc = etree.SubElement(url, 'loc')
                    pkg_url = url_for(controller='package', action="read", id = packageName).replace("euodp/", "")
                    path = config.get('ckan.site_url').rsplit('/', 1)[-1]
                    path = '/'+path
                    if pkg_url.startswith(path):
                        server_url = config.get('ckan.site_url')[:-len(path)]
                    else:
                        server_url = config.get('ckan.site_url')
                    loc.text = server_url + pkg_url
                    lastmod = etree.SubElement(url, 'lastmod')
                    lastmod.text = packageDate.strftime('%Y-%m-%d')
                    changefreq = etree.SubElement(url, 'changefreq')
                    changefreq.text = 'monthly'



                currentPackage = packageName
                url = etree.SubElement(root, 'url')

                loc = etree.SubElement(url, 'loc')
                rsc_url = url_for(controller="package", action="resource_read", id = packageName, resource_id = resourceId).replace("euodp/", "")
                if rsc_url.startswith(path):
                    server_url = config.get('ckan.site_url')[:-len(path)]
                else:
                    server_url = config.get('ckan.site_url')
                loc.text = server_url + rsc_url
                lastmod = etree.SubElement(url, 'lastmod')
                lastmod.text = resourceDate.strftime('%Y-%m-%d')

                changefreq = etree.SubElement(url, 'changefreq')
                changefreq.text = 'monthly'

                if iteration >= ckan_dataset_number:
                    break
                iteration+=1
                count+=1

            with open(filepath, 'w') as f:
                count+=1
                f.write(etree.tostring(root, pretty_print=True))

            file_number += 1

    def _render_sitemap_current_language(self):
        response.headers['Content-type'] = 'text/xml'
        self._render_sitemap(self._current_locale())


    def _render_sitemap(self, locale):
        dirpath = config.get('cache_dir','/applications/ecodp/users/ecodp/ckan/var/cache')
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        count = 0
        size_files = 0
        file_name = '/sitemap_' + locale +'.xml'
        child_file_name = '/sitemap_' + locale + '_' + str(count) +'.xml'
        filepath = dirpath + file_name
        child_file_path = dirpath + child_file_name

        generation_needed = self.__recreate_file(filepath)

        if generation_needed:
            try:
                conn = self.__get_connection()
                self._generate_sitemap(conn, locale)
            except Exception:
                log.error(traceback.print_exc())
            finally:
                log.info("Closing database connection")
                if conn:
                    conn.close()
        else:
            log.info("File already generated and saved in cache")

        if generation_needed:

            root = etree.Element("sitemapindex", nsmap={None: SITEMAP_NS})

            while os.path.isfile(child_file_path):

                sitemap = etree.SubElement(root, 'sitemap')
                loc = etree.SubElement(sitemap, 'loc')
                server_url = config.get('ckan.site_url')
                if config.get('ckan.root_path', None):
                    path = '/data'
                else:
                    path = ''
                loc.text = server_url+path+'/sitemap_' + locale + '_' + str(count) +'.xml'

                count+=1
                child_file_path = dirpath + '/sitemap_' + locale + '_' + str(count) +'.xml'

            file_content = etree.tostring(root, pretty_print=True)
            with open(filepath, 'w') as f:
                f.write(file_content)
            f.close()
            return file_content
        else:
            with open(filepath, 'r') as f:
                return f.read()


    def view(self):
        return self._render_sitemap()

    def one_result(self, lang, number):
        response.headers['Content-type'] = 'text/xml'
        locale = self._current_locale()
        dirpath = config.get('cache_dir','/applications/ecodp/users/ecodp/ckan/var/cache')
        filepath = dirpath + '/sitemap_' + lang + '_' + number +'.xml'
        if not self.__recreate_file(filepath):
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filepath)
            with open(filepath, 'r') as f:
                response.headers['Content-Length']=size
                shutil.copyfileobj(f, response)
                return
        return self._render_sitemap()


    def __get_connection(self):
        dbParams = urlparse.urlparse(config.get('sqlalchemy.url'))
        log.info("Openinging database connection for sitemap")
        conn = psycopg2.connect(
            database = dbParams.path[1:],
            user = dbParams.username,
            password = dbParams.password,
            host = dbParams.hostname
        )
        return conn


    def __recreate_file(self, filepath):

        if not os.path.isfile(filepath):
            return True

        valid_cache_time= time.time() - validity_duration*one_day
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filepath)
        return  valid_cache_time > ctime

    def reload_all_sitemaps(self):
        global ckan_dataset_number
        global validity_duration
        ckan_dataset_number = int(config.get('ckan.sitemap.dataset.number', init_dataset_number))
        validity_duration = int(config.get('sitemap.cache.time',init_sitemap_cache)) #number of days

        locales = i18n.get_locales_dict()
        for key, value in locales.iteritems():
            log.info("Checking sitemap for language %s" % key)
            if key != 'zh':
                self._render_sitemap(key)
