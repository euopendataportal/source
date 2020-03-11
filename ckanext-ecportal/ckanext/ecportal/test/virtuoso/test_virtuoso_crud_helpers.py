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

from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
from ckanext.ecportal.virtuoso.predicates_constants import AUTHORITY_CODE_PREDICATE, IN_SCHEME_PREDICATE
from ckanext.ecportal.virtuoso.graph_names_constants import GRAPH_CORPORATE_BODY
from ckanext.ecportal.virtuoso.triplet import Triplet
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers, OBJECT_WITH_SPACES, SUBJECT_WITH_SPACES

logging.basicConfig(level=logging.DEBUG)

vsc = TripleStoreCRUDHelpers()
vsh = TripleStoreCRUDHelpers()

class TestVirtuosoCRUDHelpers(TestWithVirtuosoConfiguration):
    def setUp(self):
        sparql_query = """
            drop silent graph <graphToDrop>
            drop silent graph <testGraph>
            drop silent graph <createdGraph>
            drop silent graph <createdGraphCopy>
            create silent graph <graphToDrop>
            create silent graph <testGraph>
            INSERT DATA {graph <testGraph>
                {
                    <ss><pp><oo>. <ss><pp><old>. <ss><p1><op1>.
                    <ss><p2><op2>. <ss><p2><op221>. <ss2><pnew><old1>.
                    <ss2><pnew><old2>.<sall><pall><oall>.
                    <pers><pname> 'nameOfPers'@en.<pers><pname> 'nomDuPers'@fr.
                }
            }

            drop silent graph <graphpublic>
            drop silent graph <graphprivate>
            drop silent graph <source>
            create graph <graphpublic>
            create graph <graphprivate>
            create graph <source>
            drop graph <graphpublic>
            
            
            drop silent graph <transac_g1>
            create silent graph <transac_g1>
            INSERT DATA {graph <transac_g1>{<exit> <before> <transaction>}}
            
            drop silent graph <transactional_tmp_g>
            create silent graph <transactional_tmp_g>

            insert data {
                    graph <graphpublic>
                    {
                        <s><p><o1>.
                        <s1><p1><o1>.
                        <s2><p1><o1>.

                    }
                    }

            insert data {
                    graph <source>
                    {
                        <s><p><o1>.
                        <s1><p1><o1>.
                        <s2><p1><o1>.
                    }
                    }

            """
        vsc.execute_update_query(sparql_query)

    def test_create_graph(self):
        result = vsc.graph_create('createdGraph')
        self.assertTrue(result, "graph not created")

    def test_get_list_graphs(self):
        list_graphs = vsc.get_list_graphs()
        self.assertTrue(len(list_graphs) > 0, 'ERROR in get_list_graphs')

    def test_remove_graph(self):
        graph_name = 'graphToDrop'
        count_graph_before = len(vsc.get_list_graphs())
        vsc.graph_remove(graph_name)
        count_graph_after = len(vsc.get_list_graphs())
        print "Graph Before {0} , after {1}".format(count_graph_before, count_graph_after)
        self.assertNotEqual(count_graph_after, count_graph_before, "DROP GRAPH ERROR")

    def test_check_server_status(self):
        result = vsc.check_server_status()
        self.assertTrue(result, 'Check status of the server is not working')

    def test_execute_insert_ttl(self):
        count_before = len(vsc.execute_select_query_auth("SELECT * FROM <testGraph> {?S [][]}"))
        vsc.execute_insert_ttl("testGraph", "<in1><in2><in3>")
        count_after = len(vsc.execute_select_query_auth("SELECT * FROM <testGraph> {?S [][]}"))
        self.assertEquals((count_after - 1), count_before, "Insert sparql is not working.")
        logging.info(" Execute_insert_ttl: Count before {0} , after {1}".format(count_before, count_after))

    def test_execute_delete_ttl(self):
        test_graph = "testGraph"
        count_before = len(vsc.execute_select_query_auth("SELECT * FROM <testGraph> {?S [][]}"))
        vsc.execute_delete_ttl("testGraph", "<ss><pp><oo>")
        count_after = len(vsc.execute_select_query_auth("SELECT * FROM <testGraph> {?S [][]}"))
        self.assertEquals((count_after + 1), count_before, " delete triples is not working")
        logging.info("Execute delete: Count before {0} , after {1}".format(count_before, count_after))

    def test_execute_update_ttl(self):
        result = vsc.execute_update_ttl("testGraph", "<ss><pp><old>", "<ss><pp><new>", "")
        spo = vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {?S ?o <new>}")
        self.assertEquals(len(spo), 1, "Execute_update_ttl is not working")

    def test_graph_copy(self):
        result = vsc.graph_copy("testGraph", "testGraphCopy")
        count = len(vsc.execute_select_query_auth("SELECT * FROM <testGraphCopy> {?S ?p ?o}  "))
        self.assertNotEqual(count, 0, "copy graph is not working")

    def test_update_property_value(self):
        result = vsc.update_property_value("testGraph", "<ss2>", "<pnew>", "'newAfterUpdate'")
        ss = vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {?S <pnew> 'newAfterUpdate'}")
        count = len(ss)
        self.assertEqual(ss[0]['s']['value'], 'ss2', "update property value error")
        self.assertEqual(count, 1, "update property is not working.  Query is {0}".format(vsc._sparql_query))

    def test_get_all_properties_value(self):
        result = vsc.get_all_properties_value('testGraph', '<ss>')
        self.assertTrue(len(result) > 2)

    def test_get_property_values(self):
        # result = vsc.get_property_values()
        result = vsc.get_property_values('testGraph', '<ss>', '<p2>')
        self.assertTrue(len(result) > 1)

    def test_add_property_values(self):
        values = ["'spval1'", "'spval2'", "'spval3'"]
        before = vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {<ss> <p2> ?sv}")
        self.assertTrue(len(before) >= 0)
        vsc.add_property_values('testGraph', '<ss>', '<p2>', values)
        after = vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {<ss> <p2> ?sv}")
        self.assertEqual(len(after), len(before) + 3)

    def test_update_property_values(self):
        values = ["'update1'", "'update2'", "'update3'", "'update4'"]
        result = vsc.update_property_values("testGraph", "<ss2>", "<pnew>", values)
        count = len(vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {<ss2> <pnew> ?v}"))
        self.assertEqual(count, 4, "update property is not working.  Query is {0}".format(vsc._sparql_query))

    def test_set_all_properties_values(self):
        list_values = {}
        val = ["<val1>", "<val2>", "<val3>"]
        list_values["<prop1>"] = val
        list_values["<prop3>"] = ["55", "66"]
        before = vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {<sall> ?p ?o}")
        self.assertEqual(len(before), 1)
        result = vsc.set_all_properties_values('testGraph', '<sall>', list_values)
        after = vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {<sall> ?p ?o}")
        self.assertEqual(len(after), 5, "Set _all")

    def test_get_property_value_by_language(self):
        all_names = vsc.execute_select_query_auth("SELECT * FROM <testGraph> WHERE {<pers> <pname> ?NAME }")
        self.assertEqual(len(all_names), 2, 'Get_property_value_by_language: The number of names should be 2')
        result = vsc.get_property_value_by_language('testGraph', '<pers>', '<pname>', 'en')
        self.assertEqual(len(result), 1, 'Get_property_value_by_language: The number of names should be 1')

    def test_get_all_different_text_value_by_language_or_without(self):
        listv = vsc.get_all_different_text_value_by_language_or_without(["testGraph", "testGraph2"], "<pers>",
                                                                        "<pname>", "fr")
        self.assertEqual(len(listv), 1, 'get_all_different_text_value_by_language_or_without : Wrong number of return '
                                        'parameters')
        self.assertEqual(listv[0]['value']['value'], u'nomDuPers', 'get_all_different_text_value_by_language_or_without'
                                                                   ': Does not return the proper result')

    def test_execute_update_without_condition(self):
        ttl1 = "<s><p><o1>. <s1><p1><o1>."
        ttl2 = "<s><p><o3>. <s1><p1><o4>. <s1><p3><o5>"
        # before_update = vsc.execute_select_query_auth("select * from <graphpublic> where {?s ?p ?o}")
        # len_bu = len (before_update)

        r = vsc.execute_update_without_condition("graphpublic", "graphpublic", ttl1, ttl2)

        after_update = vsc.execute_select_query_auth("SELECT * FROM <graphpublic> WHERE {?S ?p ?o}")
        len_au = len(after_update)
        self.assertTrue(len_au == 4)

        # result = vsc.execute_select_query_auth("select * from <graphprivate> where {?s ?p ?o}")
        # len_private_au = len (result)

        r = vsc.execute_update_without_condition("source", "graphprivate", ttl1, ttl2)

        result = vsc.execute_select_query_auth("SELECT * FROM <source> WHERE {?S ?p ?o}")
        len_source_au = len(result)

        result = vsc.execute_select_query_auth("SELECT * FROM <graphprivate> WHERE {?S ?p ?o}")
        len_private_au = len(result)
        self.assertTrue(len_source_au == 1 and len_private_au == 3)

    def test_get_subjects_by_property_value(self):
        list_elem = vsc.get_subjects_by_property_value('http://eurovoc.europa.eu',
                                                       '<http://www.w3.org/2004/02/skos/core#inScheme>',
                                                       '<http://eurovoc.europa.eu/domains>')

        self.assertTrue(len(list_elem) == 21)

    def test_execute_ask_query_auth(self):
        self.assertFalse(vsc.check_if_spo_exists('http://eurovoc.europa.eu',
                                                 'http://publications.europa.eu/resource/authority/data-theme/TECH',
                                                 'http://www.w3.org/2004/02/skos/core#inScheme',
                                                 '<http://eurovoc.europa.eu/domains>'))
        self.assertTrue(vsc.check_if_spo_exists('http://publications.europa.eu/resource/authority/data-theme',
                                                'http://publications.europa.eu/resource/authority/data-theme/TECH',
                                                'http://www.w3.org/2004/02/skos/core#inScheme',
                                                '<http://publications.europa.eu/resource/authority/data-theme>'))

    def test_find_any_for_where_clauses(self):
        triple_store_CRUD_helper = TripleStoreCRUDHelpers()
        triplet_list = [Triplet(predicate=IN_SCHEME_PREDICATE, object=GRAPH_CORPORATE_BODY),
                        Triplet(predicate=AUTHORITY_CODE_PREDICATE), ]
        searched_fields = SUBJECT_WITH_SPACES + OBJECT_WITH_SPACES
        properties_values = triple_store_CRUD_helper.find_any_for_where_clauses(GRAPH_CORPORATE_BODY, triplet_list,
                                                                                searched_fields)
        assert properties_values is not None
        assert len(properties_values) > 0

    def test_execute_update_without_condition_perf(self):
        ttl_insert=""
        ttl_delete = "<t><t><t>"
        nbr_triples = 1426
        for i in range(1,nbr_triples):
            triple = '<sdsfdsfsds>   <efgfsdfsxcwxcdgp>   <odfdsfdsccxcfsdfsdfo{0}>. \r\n'.format(i)
            ttl_insert= ttl_insert + triple
        r = vsc.execute_update_without_condition("graphpublic", "graphpublic", ttl_delete, ttl_insert)

        after_update = vsc.execute_select_query_auth("SELECT * FROM <graphpublic> WHERE {?S ?p ?o}")
        len_au = len(after_update)
        self.assertTrue(len_au==nbr_triples+2)
        pass

    def test_insert_big_ttl_with_transaction(self):
        graph_name = "transac_g1"
        temp_graph = "transactional_tmp_g"
        ttl_insert = ""
        nbr_triples = 2000

        for i in xrange(nbr_triples):
            triple = "<t>   <p>  'o_{0}'.\n".format(i)
            ttl_insert = ttl_insert + triple
        import time
        debut = time.time()
        r = vsh.insert_big_ttl_with_transaction(graph_name,ttl_insert)
        duration = time.time() - debut

        after_update = vsc.execute_select_query_auth("SELECT * FROM <{0}> WHERE {{?s ?p ?o}}".format(graph_name))
        len_au = len(after_update)
        self.assertTrue(len_au == nbr_triples + 1)
        print "Duration is {0}".format(duration)

        pass


    def test_delete_big_ttl_transaction(self):
        graph_name = "transac_g1"
        temp_graph = "transactional_tmp_g"
        ttl_insert = ""
        nbr_triples = 2000

        for i in xrange(nbr_triples):
            triple = "<t>   <p>  'o_{0}'.\n".format(i)
            ttl_insert = ttl_insert + triple

        import time
        r = vsh.insert_big_ttl_with_transaction(graph_name,ttl_insert,temp_graph)
        r = vsh.insert_big_ttl_with_transaction("graphToDrop",ttl_insert,temp_graph)
        # delete data
        r = vsh.execute_update_query("INSERT DATA {GRAPH <transac_g1> { <new> <triple> <toto> }}")

        after_update = vsc.execute_select_query_auth("SELECT * FROM <{0}> WHERE {{?s ?p ?o}}".format(graph_name))
        self.assertEquals(len(after_update),nbr_triples+2)

        start = time.time()
        r = vsh.delete_big_ttl_transaction(graph_name,ttl_insert,"graphToDrop",use_existing_rollback_graph=True)
        duration = time.time() - start
        print "Duration delete big ttl {0}".format(duration)


        after_update = vsc.execute_select_query_auth("SELECT * FROM <{0}> WHERE {{?s ?p ?o}}".format(graph_name))
        len_au = len(after_update)
        self.assertTrue(len_au == 2)

        pass

    def test_transactional_update_big_dataset(self):
        graph_name = "transac_g1"
        temp_graph = "transactional_tmp_g"
        ttl_insert = ""
        nbr_triples = 2500

        for i in xrange(nbr_triples):
            triple = "<t>   <p>  'o_{0}'.\n".format(i)
            ttl_insert = ttl_insert + triple

        import time
        r = vsh.insert_big_ttl_with_transaction(graph_name, ttl_insert, temp_graph)


        # create the update ttls

        new_insert = ""
        for i in xrange(nbr_triples):
            triple = "<tnew>   <pnew>  'o_{0}'.\n".format(i)
            new_insert = new_insert + triple

        exiting_ttl_to_delete =""
        for i in xrange(nbr_triples):
            triple = "<t>   <p>  'o_{0}'.\n".format(i)
            exiting_ttl_to_delete = exiting_ttl_to_delete + triple

        # delete data

        r = vsh.execute_update_query("INSERT DATA {GRAPH <transac_g1> { <new> <triple> <toto> }}")


        r = vsh.transactional_update_big_dataset(graph_name,graph_name,exiting_ttl_to_delete,new_insert)


        after_update = vsc.execute_select_query_auth("SELECT * FROM <{0}> WHERE {{?s ?p ?o}}".format(graph_name))
        self.assertEquals(len(after_update), nbr_triples + 2)

        after_update = vsc.execute_select_query_auth("SELECT * FROM <{0}> WHERE {{ <t> <p> ?o}}".format(graph_name))

        self.assertEquals(len(after_update), 0)

        after_update = vsc.execute_select_query_auth("SELECT * FROM <{0}> WHERE {{ <tnew> <pnew> ?o}}".format(graph_name))
        self.assertEquals(len(after_update), nbr_triples)




        pass