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
Created on Nov 23, 2015

@author: ecodp
'''
import os
import requests
import json
import psycopg2
import time
import logging
import ConfigParser
from logging.handlers import TimedRotatingFileHandler
from ConfigParser import SafeConfigParser
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

# create logger
logger = logging.getLogger(__name__)
api_key = None
ckan_url = None
dbname = None
dbuser = None
dbpassword = None


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = TimedRotatingFileHandler(CKAN_PATH + '/logs/dnc.log',when='midnight',  backupCount=30)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info("Script to insert structured data of existing resources to datastore started")


def query_resources_in_db():
    logger.debug("Asking database for text columns")
    try:
        conn = psycopg2.connect("dbname=%s user=%s host=%s password=%s" % (dbname, dbuser, dbhost, dbpassword))
    except :
        logger.exception( "Unable to connect to the database")

    cur = conn.cursor()
    cur.execute("select * from information_schema.columns where table_schema = 'public' and data_type in ('text', 'character varying')")
    rows = cur.fetchall()

    return rows

parser = SafeConfigParser()
confFile = str(os.getcwd())+'/domain_name_change.ini'
logger.info("reading properties file:%s" % confFile)
parser.read(confFile)
dbname = parser.get('global', 'dbname')
dbuser = parser.get('global', 'dbuser')
dbpassword = parser.get('global', 'dbpassword')
dbhost = parser.get('global', 'dbhost')
oldnamespace = parser.get('global', 'oldnamespace')
newnamespace = parser.get('global', 'newnamespace')
try:
    rows = query_resources_in_db()
    conn = psycopg2.connect("dbname=%s user=%s host=%s password=%s" % (dbname, dbuser, dbhost, dbpassword))
    size = len(rows)
    count = 0
    for row in rows:
        count += 1
        logger.info("%s/%s %s %s" % (count, size, row[2], row[3]))
        executor = conn.cursor()
        executor.execute(u'update "%s" set "%s" = REPLACE("%s", \'%s\', \'%s\')' % (row[2], row[3], row[3], oldnamespace, newnamespace))

    conn.commit()
except:
        logger.exception( "Unable to connect to the database")
        conn.rollback()

finally:
        logger.info("Closing database connection")
        if conn:
            conn.close()