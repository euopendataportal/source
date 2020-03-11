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
import time
import unittest

from rdflib import Graph

from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
from ckanext.ecportal.virtuoso.utils_triplestore_crud_core import VirtuosoCRUDCore

logging.basicConfig(level=logging.DEBUG)

vsc = VirtuosoCRUDCore()


class TestPeromanceTS(TestWithVirtuosoConfiguration):
    def setUp(self):
        sparql_query = "DROP SILENT GRAPH <insertPerformance>"
        vsc.execute_update_query(sparql_query)

    def test_performance_update(self):
        try:
            # Dataset - example_withoutError
            path_file = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/" \
                        "test/data/Dataset-example_withoutError.rdf"
            g = Graph()
            g.parse(path_file, format="xml")
            ttl_str = g.serialize(format="nt")
            start = time.time()
            for i in xrange(1, 100):
                sparql_query = "clear graph <insertPerformance> INSERT INTO <insertPerformance> {{  {0} }}  ".format(
                    ttl_str)
                result = vsc.execute_update_query(sparql_query)
            duration = time.time() - start
            logging.info("Log Duration of update SPARQL {0}".format(duration))
            self.assertTrue(4.0 <= duration <= 7.2, "Virtuoso Performance: Pb with Update")



        except BaseException as e:
            pass

    def test_performance_update2(self):
        try:
            # Dataset - example_withoutError
            path_file = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/" \
                        "test/data/Dataset-example_withoutError.rdf"
            g = Graph()
            g.parse(path_file, format="xml")
            ttl_str = g.serialize(format="nt")
            start = time.time()
            for i in xrange(1, 100):
                sparql_query = "clear graph <insertPerformance> INSERT INTO <insertPerformance> {{  {0} }}  ".format(
                    ttl_str)
                result = vsc.execute_update_query(sparql_query)
            duration = time.time() - start
            logging.info("Log Duration of update SPARQL {0}".format(duration))
            self.assertTrue(4.0 <= duration <= 7.2, "Virtuoso Performance: Pb with Update")



        except BaseException as e:
            pass

    def test_performance_select(self):
        path_file = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/" \
                    "test/data/Dataset-example_withoutError.rdf"
        g = Graph()
        g.parse(path_file, format="xml")
        ttl_str = g.serialize(format="nt")
        sparql_query = "clear graph <insertPerformance> INSERT INTO <insertPerformance> {{  {0} }}  ".format(ttl_str)
        result = vsc.execute_update_query(sparql_query)
        start = time.time()

        for i in xrange(1, 100):
            sparql_query = "select * from <insertPerformance> where {<http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2> ?s ?o}"
            # sparql_query= "select * from <insertPerformance> where {?s ?p ?o filter (?s=<http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2>)}"
            result = vsc.execute_select_query_auth(sparql_query)
        duration = time.time() - start
        logging.info("Duration of SELECT SPARQL {0}".format(duration))
        self.assertTrue(0.5 <= duration <= 1.4, "Virtuoso Performance: Pb with SELECT Duration= {0}".format(duration))


if __name__ == '__main__':
    unittest.main()
