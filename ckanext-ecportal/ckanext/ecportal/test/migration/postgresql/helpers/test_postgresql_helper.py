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

from operator import and_
from unittest import TestCase

from sqlalchemy.orm import sessionmaker

from ckanext.ecportal.migration.postgresql.dto.postgresql_dtos import Dashboard, TermTranslation, Package, \
    PackageExtra, Tag, PackageTag
from ckanext.ecportal.migration.postgresql.helpers import postgresql_helper
from ckanext.ecportal.migration.postgresql.helpers.postgresql_helper import get_connection
from ckanext.ecportal.test.configuration.configuration_constants import TEST_CONFIG_FILE_PATH, \
    POSTGRES_CONNECTION_STRING
from ckanext.ecportal.virtuoso.basic_queries_constants import SHOW_TABLES

COUNT_ALL_DATASETS_QUERY = "select  case when private then 'private' else 'public' end as datasets, count(private) from package where state = 'active' group by private;"


class TestPostgresqlHelper(TestCase):
    def test_get_connection(self):
        connection = get_connection(POSTGRES_CONNECTION_STRING)
        cur = connection.cursor()
        cur.execute(SHOW_TABLES)
        rows = cur.fetchall()  # type: list
        assert rows is not None
        assert len(rows) is 116
        connection.close()
        assert connection is not None

    def test_sqlalchemy(self):
        engine = postgresql_helper.get_engine(TEST_CONFIG_FILE_PATH)
        connection = engine.connect()
        assert connection is not None

        Session = sessionmaker(bind=engine)
        session = Session()
        result = session.query(Dashboard).all()  # type: Dashboard

        assert result[0].user_id is not None
        pass

    def test_sqlalchemy_connection(self):
        session = postgresql_helper.get_query_session(TEST_CONFIG_FILE_PATH)
        assert session is not None

        result = session.query(Dashboard).all()  # type: Dashboard

        assert result[0].user_id is not None
        pass

    def test_find_any(self):
        condition = TermTranslation.term == "EuroVoc, the EU's multilingual thesaurus"
        titles = postgresql_helper.find_any_in_database(config_file_path=TEST_CONFIG_FILE_PATH,
                                                        condition=condition,
                                                        table=TermTranslation)
        assert titles is not None

        packages = postgresql_helper.find_any_in_database(config_file_path=TEST_CONFIG_FILE_PATH,
                                                          table=Package)
        assert packages is not None

    def test_find_any_in_tables_database(self):
        filter_package_name = Package.name == "ted-1"
        filter_package_state = Package.state == "active"
        filter_package_extra_key = PackageExtra.key == "contact_email"
        condition = and_(and_(filter_package_name, filter_package_state),
                         filter_package_extra_key)

        order_by_clause = [Package.name]

        postgresql_helper.find_any_in_tables_database(TEST_CONFIG_FILE_PATH,
                                                      condition,
                                                      [Package, PackageExtra],
                                                      [Package.name, PackageExtra.value],
                                                      order_by_clause=order_by_clause)

    def test_find_any_in_tables(self):
        titles = postgresql_helper.find_any_in_tables_database(config_file_path=TEST_CONFIG_FILE_PATH,
                                                               tables=[Package],
                                                               result_clause=[Package.title])
        assert titles is not None

        packages = postgresql_helper.find_any_in_database(config_file_path=TEST_CONFIG_FILE_PATH,
                                                          table=Package)
        assert packages is not None

    def test_find_any_for_result_clause(self):
        titles = postgresql_helper.find_any_in_tables_database(config_file_path=TEST_CONFIG_FILE_PATH,
                                                               result_clause=[Package, PackageExtra])
        assert titles is not None

        packages = postgresql_helper.find_any_in_database(config_file_path=TEST_CONFIG_FILE_PATH,
                                                          table=Package)
        assert packages is not None

    def test_get_all_active_datasets(self):
        packages = postgresql_helper.get_all_active_packages(TEST_CONFIG_FILE_PATH)  # type: list[Package]
        assert packages is not None
        assert len(packages) == 10945

    def test_execute_query(self):
        number_datasets_per_graphs = postgresql_helper.execute_query(COUNT_ALL_DATASETS_QUERY, TEST_CONFIG_FILE_PATH)
        assert number_datasets_per_graphs is not None
        number_datasets_public_graph = number_datasets_per_graphs[0][1]
        assert number_datasets_public_graph > 0
        number_datasets_private_graph = number_datasets_per_graphs[1][1]
        assert number_datasets_private_graph > 0

    def test_find_keyword(self):
        condition = \
            and_(
                and_(
                    and_(Package.id == PackageTag.package_id, Tag.vocabulary_id == None),
                    PackageTag.state == 'active'),
                PackageTag.tag_id == Tag.id
            )
        postgresql_helper.find_any_in_tables_database(TEST_CONFIG_FILE_PATH, condition, [], [Package.name, Tag.name])



    def test_find_any_in_tables_database(self):
        filter_package_name = Package.name == "ted-1"
        filter_package_state = Package.state == "active"
        filter_package_extra_key = PackageExtra.key == "contact_email"
        condition = and_(and_(filter_package_name, filter_package_state),
                         filter_package_extra_key)

        order_by_clause = [Package.name]

        postgresql_helper.find_any_in_tables_database(TEST_CONFIG_FILE_PATH,
                                                      condition,
                                                      [Package, PackageExtra],
                                                      [Package.name, PackageExtra.value],
                                                      order_by_clause=order_by_clause)