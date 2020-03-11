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

import ConfigParser
import logging
import urlparse

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from ckanext.ecportal.configuration.configuration_constants import CONFIGURATION_FILE_PATH
from ckanext.ecportal.migration.migration_constants import ACTIVE_STATE
from ckanext.ecportal.migration.postgresql.dto.postgresql_dtos import Package, PackageRevision

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

DEFAULT_POSTGRESQL_CONNECTION_STRING = "postgresql://ecodp:password@10.2.0.113:5432/ecodp"
POSTGRESQL_CONNECTION_STRING = "sqlalchemy.url"
MAIN_SECTION = "app:main"

engine = None
session = None


# Get connection to postgresql directly from the connection string and using psycopg2.
def get_connection(connection_string=DEFAULT_POSTGRESQL_CONNECTION_STRING):
    db_params = urlparse.urlparse(connection_string)
    connection = None
    try:
        logging.info("Opening database connection for sitemap")
        connection = psycopg2.connect(
            database=db_params.path[1:],
            user=db_params.username,
            password=db_params.password,
            host=db_params.hostname
        )
    except Exception as e:
        logging.error("Unable to connect to the database; reason: {0}".format(e.message))
        print
    return connection


# Get CKAN's database connection from
def get_engine(config_file_path=CONFIGURATION_FILE_PATH):
    global engine
    if not engine or engine is None:
        try:
            configuration = ConfigParser.ConfigParser()
            configuration.read(config_file_path)
            db_config_url = configuration.get(MAIN_SECTION, POSTGRESQL_CONNECTION_STRING)
            engine = create_engine(db_config_url)
            logging.info("Engine to postgresql is created")
        except Exception as e:
            logging.error("Database connection not found in config file; reason: {0}".format(e.message))
    return engine


def get_query_session(config_file_path=CONFIGURATION_FILE_PATH):
    get_engine(config_file_path)
    assert engine is not None
    connection = engine.connect()
    assert connection is not None

    global session
    if session is None:
        Session = sessionmaker(bind=engine)
        session = Session()
        logging.info("Session for postgresql has been created")

    return session


def find_any_in_database(config_file_path=CONFIGURATION_FILE_PATH,  # type: str
                         condition=None,  # type: bool
                         table=None,  # type: object
                         result_clause=None,  # type: list[object]
                         order_by_clause=None  # type: list[object]
                         ):
    result = find_any_in_tables_database(config_file_path, condition, [table], result_clause,
                                         order_by_clause)
    return result


def find_any_in_tables_database(config_file_path=CONFIGURATION_FILE_PATH,  # type: str
                                condition=None,  # type: bool
                                tables=None,  # type: list[object]
                                result_clause=None,  # type: list[object]
                                order_by_clause=None  # type: list[object]
                                ):
    if order_by_clause is None:
        order_by_clause = {}
    if result_clause is None:
        result_clause = []
    if tables is None:
        tables = []

    session = get_query_session(config_file_path)

    # Set tables to look into
    query = session.query(*tables)

    # Set result clause from list of column
    if len(result_clause) > 0:
        query = session.query(*result_clause)

    # Add conditions, aka filters in sqlalchemy
    if condition is not None:
        query = query.filter(condition)

    for element in order_by_clause:
        query = query.order_by(element)

    result = query.all()
    log_query_result(result)

    return result


def get_all_active_packages(config_file_path):
    session = get_query_session(config_file_path)
    logging.warning("Retrieve all packages from postgresql")
    active_packages = session.query(Package).filter(Package.state == ACTIVE_STATE).all()  # type: list[Package]
    return active_packages


def get_metadata_created_timestamp(package_id, config_file_path=CONFIGURATION_FILE_PATH):
    session = get_query_session(config_file_path)

    q = session.query(PackageRevision.revision_timestamp) \
        .filter(PackageRevision.id == package_id) \
        .order_by(PackageRevision.revision_timestamp.asc())
    ts = q.first()
    if ts:
        return ts[0]


def log_query_result(result):
    if result is None:
        logging.warning("Postgresql query failed")
    logging.info("Postgresql query successful")


def execute_query(query="", config_file_path=CONFIGURATION_FILE_PATH):
    engine = get_engine(config_file_path)
    connection = engine.connect()
    result = connection.execute(query).fetchall()
    return result


def rename_datastore_table(src_table_name, dest_table_name, config_file_path=CONFIGURATION_FILE_PATH):

    connection = get_connection('postgresql://ecodp:password@10.2.0.113/datastore_default')
    cur = connection.cursor()
    cur.execute('ALTER TABLE IF EXISTS %s RENAME TO %s;', (src_table_name, dest_table_name))
    connection.commit()
    cur.close()
    connection.close()


def execute_query_with_param(query="", config_file_path=CONFIGURATION_FILE_PATH, param=''):
    engine = get_engine(config_file_path)
    connection = engine.connect()
    result = connection.execute(text(query), domain_list=param).scalar()
    return result