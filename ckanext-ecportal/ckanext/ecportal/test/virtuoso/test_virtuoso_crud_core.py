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

import logging, codecs
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
logging.basicConfig(level=logging.DEBUG)
from ckanext.ecportal.virtuoso.utils_triplestore_crud_core import VirtuosoCRUDCore
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers

vsc = VirtuosoCRUDCore()
vsh = TripleStoreCRUDHelpers()

# build the data for the test

class TestVirtuosoCRUDCore(TestWithVirtuosoConfiguration):

    def setUp(self):
        vsc = VirtuosoCRUDCore()
        a= 10
        vsc = VirtuosoCRUDCore()
        sparql_query = """
            drop silent graph <graphToDrop>
            drop silent graph <graphpublic>
            drop silent graph <testGraph>
            drop silent graph <createdGraph>
            drop silent graph <testPerformance>
            drop silent graph <transac_g1>
            create silent graph <transac_g1>
            
            drop silent graph <transactional_tmp_g>
            create silent graph <transactional_tmp_g>
            
            
            create silent graph <graphToDrop>
            create silent graph <testGraph>
            create silent graph <testPerformance>
            create silent graph <graphpublic>
            
            INSERT DATA {graph <testGraph> {<ss><pp><oo>}}
            INSERT DATA {graph <transac_g1>{<exit> <before> <transaction>}}
            """
        vsc.execute_update_query(sparql_query)


    def test_execute_select_query(self):

        count = vsc.execute_select_query("select * where { ?s ?p ?o} limit 5").__len__()
        self.assertEqual(count, 5, "Select SPARQL is not working")
        logging.info("SELECT query OK")

    def test_execute_select_query_auth(self):
        count = vsc.execute_select_query_auth("select * where { ?s ?p ?o} limit 5").__len__()
        self.assertEqual(count, 5, "Select SPARQL is not working")

    def test_execute_update_query(self):
        # vsc.execute_update_query("insert data into graph <gg> {<gsecure><gsecure><gsecure>} ")
        result = vsc.execute_update_query("insert into <testGraph> {<t><t><t>} insert into <testGraph> {<t><t><t2>}")
        self.assertTrue(result, "Update execute_query ERROR")
        result = vsc.execute_update_query("insert into <testGraph> {<t><t><t>}")
        self.assertFalse(result, "BAD request accepted: ERROR")

        # test utf 8 query
        with codecs.open('/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal'
                  '/test/data/exampleUTF8.txt', 'r',encoding='utf8') as datasets:
            data = datasets.read().replace('\n', 'br')
            # print data
        # sparql_query = "insert into <testGraph> {{<t><t><t>}} insert into <testGraph> {{<t><t> \"{0}\"}}".format(data)
        # result = vsc.execute_update_query(sparql_query)
        # pass
        # print result


    def test_execute_update_query_perf(self):

        ttl_insert = ""
        ttl_delete = "<t><t><t>"
        nbr_triples = 1425
        for i in xrange(nbr_triples):
            triple = '<sdsfdsfsds>   <efgfsdfsxcwxcdgp>   <odfdsfdsccxcfsdfsdfo{0}>. \r\n'.format(i)
            ttl_insert = ttl_insert + triple

        sparql_query = "WITH GRAPH <graphpublic> INSERT {{ {0} }}".format(ttl_insert)

        r = vsc.execute_update_query(sparql_query)

        after_update = vsc.execute_select_query_auth("SELECT * FROM <graphpublic> WHERE {?S ?p ?o}")
        len_au = len(after_update)
        self.assertTrue(len_au == nbr_triples)
        pass

    def test_transactional_query(self):

        graph_name = "transac_g1"
        ttl_insert = ""
        nbr_triples = 100
        max_size_chunk = 10

        for i in xrange(nbr_triples):
            triple = "<t>   <p>   'o_{0}'.\n".format(i)
            ttl_insert = ttl_insert + triple
        ttl_insert = ttl_insert + ' '


        import time
        debut = time.time()
        r = vsh.insert_big_ttl_with_transaction()
        duration = time.time() - debut

        after_update = vsc.execute_select_query_auth("SELECT * FROM <{0}> WHERE {{?s ?p ?o}}".format(graph_name))
        len_au = len(after_update)
        self.assertTrue(len_au == nbr_triples +1)
        print "Duration is {0}".format(duration)




