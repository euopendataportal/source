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

from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME
from ckanext.ecportal.virtuoso.triplet import Triplet
from ckanext.ecportal.virtuoso.utils_triplestore_crud_core import VirtuosoCRUDCore
import traceback

ORDER_BY = " ORDER BY "

MAX_RESULT_PER_REQUEST = 100000

TRIPLETS_DELIMITER = ' .\n'

MAX_TRIPLETS = 100000

WILDCARD_WITH_SPACES = " * "

OBJECT_WITH_SPACES = " ?o "

PREDICATE_WITH_SPACES = " ?p "

SUBJECT_WITH_SPACES = " ?s "

WILDCARD = "*"

OBJECT = "?o"

PREDICATE = "?p"

SUBJECT = "?s"

VIRTUOSO_SUBJECT_RETURN = "s"

VIRTUOSO_OBJECT_RETURN = "o"

VIRTUOSO_VALUE_KEY = "value"

MAX_TRIPLETS_IN_ONE_QUERY = 800

log = logging.getLogger(__file__)



class TripleStoreCRUDHelpers(VirtuosoCRUDCore):
    def __call__(self):
        pass

    def graph_create(self, graph_name):
        try:
            create_graph_query = "CREATE silent GRAPH <{0}> ".format(graph_name)
            result = self.execute_update_query(create_graph_query)
            if not result:
                log.error("ERROR Virtuoso CRUD: Create Graph {0}")
            return True
        except BaseException as e:
            return False

    def graph_remove(self, graph_name):
        try:
            sparql_query = "DROP SILENT GRAPH <{0}>".format(graph_name)
            result = self.execute_update_query(sparql_query)
            if result:
                log.info("[Graph remove]. Remove graph successful. {0}".format(graph_name))
            else:
                log.error("[Graph remove]. Remove graph failed. {0}".format(graph_name))
            return result

        except BaseException as e:
            log.error("[Graph remove]. Remove graph failed. {0}".format(graph_name))
            log.error(traceback.print_exc(e))
            return False

    def graph_copy(self, graph_source, graph_target):
        try:
            sparql_query = "COPY GRAPH <{0}> TO <{1}>".format(graph_source, graph_target)
            result = self.execute_update_query(sparql_query)
            return result

        except BaseException as e:
            return False

    def get_list_graphs(self):
        try:
            sparql_query = "SELECT DISTINCT (?grf as ?graph_name) WHERE {GRAPH ?grf {?s ?p ?o}}"
            result = self.execute_select_query_auth(sparql_query)
            # extract only the name of graphs
            final_list = [g['graph_name']['value'] for g in result]
            return final_list
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return None

    def execute_insert_ttl(self, graph_name, str_list_triples):
        try:

            sparql_query = "WITH <{0}> INSERT {{ {1} }}".format(graph_name, str_list_triples)
            result = self.execute_update_query(sparql_query)
            return result
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def execute_delete_ttl(self, graph_name, str_list_triples, str_condition=None):
        try:
            sparql_query = "WITH <{0}> DELETE {{ {1} }} ".format(graph_name, str_list_triples)
            if str_condition:
                sparql_query = sparql_query + " WHERE {%s} " % str_condition

            result = self.execute_update_query(sparql_query)
            return result
        except BaseException as e:
            log.error("[execute_delete_ttl] failed {0}".format(str_list_triples))
            log.error(traceback.print_exc(e))
            return False

    def execute_update_ttl(self, graph_name, str_old, str_new, str_condition):
        try:
            sparql_query = "WITH <{0}> DELETE {{ {1} }} WHERE {{ {3} }} INSERT {{ {2} }} " \
                .format(graph_name, str_old, str_new, str_condition)
            result = self.execute_update_query(sparql_query)
            return result
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def execute_update_without_condition(self, graph_name_delete, graph_name_insert, ttl_delete, ttl_insert):
        """
        a combo method to remove and to update the dataset content in ts in one transaction.
        usefull for the update of dataset and to dataset's description from graph to onther
        :param graph_name_delete:
        :param graph_name_insert:
        :param ttl_delete:
        :param ttl_insert:
        :return:
        """
        try:
            # ttl_insert_chunks = \
            #     map(TRIPLETS_DELIMITER.join,
            #         list(create_chunks_from_list(ttl_insert.split(TRIPLETS_DELIMITER),
            #                                      MAX_TRIPLETS)))  # type: list[str]
            # for ttl_insert_chunk in ttl_insert_chunks:
            if len(ttl_delete) > 0:
                sparql_query = "WITH GRAPH <{0}> DELETE {{ {2} }}  INSERT {{ {3} }} " \
                    .format(graph_name_delete, graph_name_insert, ttl_delete, ttl_insert)
                if graph_name_insert != graph_name_delete:
                    sparql_query = "DELETE DATA {{ GRAPH <{0}> {{ {2} }}  }} INSERT DATA {{ GRAPH <{1}> {{ {3} }}  }}" \
                        .format(graph_name_delete, graph_name_insert, ttl_delete, ttl_insert)
            else:
                sparql_query = "INSERT DATA {{ GRAPH <{0}> {{ {1} }}  }}" \
                    .format(graph_name_insert, ttl_insert)
            result = self.execute_update_query(sparql_query)
            if result:
                log.info("[execute_update_without_condition]. Query : {0}".format(sparql_query))
            else:
                log.error("[execute_update_without_condition]. Query : {0}".format(sparql_query))
            return result
        except BaseException as e:
            log.error("[execute_update_without_condition].{0}".format(sparql_query))
            log.error(traceback.print_exc(e))
            return False

    def transactional_update_big_dataset (self, graph_name_delete, graph_name_insert, ttl_delete, ttl_insert):
        """
        Virtuoso 7 seems to have an issus with queries that contains more than 1426 triples.
        This function proposes a transactional solution to deal with big datasets.

        :param graph_name_delete:
        :param graph_name_insert:
        :param ttl_delete:
        :param ttl_insert:
        :return:
        """
        try:
            # create the delete_ttl graph for recovery
            log.info("[Transactional Update Big Dataset]: Start")
            final_result_update = False
            temp_insert_ttl_graph_name = self.create_name_of_graph(ttl_insert)
            rollback_graph_name = ""
            if len(ttl_delete) <= 1:
                # The update is just an insert
                final_result_update = self.insert_big_ttl_with_transaction(graph_name_insert,ttl_insert)
            else:
                rollback_graph_name = self.create_name_of_graph(ttl_delete)
                log.info("[Transactional Update Big Dataset]: Start save rollback graph")
                result_save_rollback_ttl = self.insert_big_ttl_with_transaction(rollback_graph_name,ttl_delete)

                if result_save_rollback_ttl:
                    log.info("[Transactional Update Big Dataset] Save rollback graph: successfull")
                    log.info("[Transactional Update Big Dataset] Start save new ttl in graph")
                    result_save_temp_insert_ttl = self.insert_big_ttl_with_transaction(temp_insert_ttl_graph_name,ttl_insert)
                    if not result_save_temp_insert_ttl:
                        log.error("[Transactional Update Big Dataset]. Save new ttl in graph: Failed")
                        log.error("[Transactional Update Big Dataset]. Failed")
                        return False
                    else:
                        log.info("[Transactional Update Big Dataset]. Save new ttl in graph: successfull")
                else:
                    log.error("[Transactional Update Big Dataset]. Save rollback graph: Failed")
                    return False

                result_delete_from_main_graph = self.delete_big_ttl_transaction(graph_name_delete,
                                                                                ttl_delete,rollback_graph_name,
                                                                                use_existing_rollback_graph=True)
                if result_delete_from_main_graph:
                    log.info(
                        "[Transactional Update Big Dataset]. Delete ttl from main graph: successful")
                    copy_graph = "INSERT {{GRAPH <{0}> {{ ?s ?p ?o }} }} WHERE " \
                                 "{{ GRAPH <{1}> {{ ?s ?p ?o }} }}".format(graph_name_insert, temp_insert_ttl_graph_name)
                    final_result_update = self.execute_update_query(copy_graph)
                    if final_result_update:
                        log.info("[Transactional Update Big Dataset]. Copy ttl from temp insert graph to main graph: successful")
                    else:
                        log.error("[Transactional Update Big Dataset]. Copy ttl from temp insert graph to main graph: failed")
                        log.error("[Transactional Update Big Dataset]. Save transactional_update_big_dataset failed")
                else:
                    log.error("[Transactional Update Big Dataset]. Delete ttl from main graph: Failed")
                    log.error("[Transactional Update Big Dataset]. Failed")

            if final_result_update:
                log.info("[transactional_update_big_dataset]. Successfull.")
            else:
                log.error("[transactional_update_big_dataset]. Failed")
            return final_result_update
        except BaseException as e:
            log.error("[transactional_update_big_dataset]. Failed")
            log.error(traceback.print_exc(e))
            if rollback_graph_name:
                self.rollback_from_graph(graph_name_delete,rollback_graph_name)
            return False
        finally:
            self.graph_remove(temp_insert_ttl_graph_name)
            if rollback_graph_name:
                self.graph_remove(rollback_graph_name)

    def insert_big_ttl_with_transaction(self, graph_name, ttl_insert, temp_graph=None):
        """

        :param graph_name:
        :param ttl_insert:
        :return:
        """
        try:
            temp_transactional_graph = ""
            if not temp_graph:
                temp_transactional_graph = self.create_name_of_graph(ttl_insert)
            else:
                temp_transactional_graph = temp_graph
            transactional_pool_queries = []
            drop_temporary_graph = "DROP SILENT GRAPH <{0}> \n CREATE SILENT GRAPH <{0}>".format(temp_transactional_graph)
            chunked_temp_complete_insert_ttl = self.build_chunked_query_from_ttl("INSERT", temp_transactional_graph, ttl_insert)
            query_insert_ttl_temp_graph = "{0}\n{1}".format(drop_temporary_graph,chunked_temp_complete_insert_ttl)
            result_query_insert_temp_graph = self.execute_update_query(query_insert_ttl_temp_graph)

            result_copy = False
            if result_query_insert_temp_graph:
                log.info("[Insert_big_ttl_with_transaction]. Insert new ttl in temp graph successful. Graph:{0}".format(temp_transactional_graph))
                copy_graph = "INSERT {{GRAPH <{0}> {{ ?s ?p ?o }} }} WHERE " \
                             "{{ GRAPH <{1}> {{ ?s ?p ?o }} }}".format(graph_name, temp_transactional_graph)
                result_copy = self.execute_update_query(copy_graph)
                if result_copy:
                    log.info("[Insert_big_ttl_with_transaction]. Copy new ttl to main graph: successful")
                else:
                    log.info("[Insert_big_ttl_with_transaction]. Insert new ttl in temp graph: Failed")
            else:
                log.info("[Insert_big_ttl_with_transaction]. Insert new ttl in temp graph: failed]")
            # self.graph_remove(temp_transactional_graph)
            return result_copy
        except BaseException as e:
            log.error("[Insert_big_ttl_with_transaction]. Failed]")
            log.error(traceback.print_exc(e))
            return False
        finally:
            self.graph_remove(temp_transactional_graph)



    def delete_big_ttl_transaction(self,graph_name, ttl_delete, rollback_graph_name, use_existing_rollback_graph = False):
        """
        Delete ttl from the graph_name in transactional way
        :param graph_name:
        :param ttl_delete:
        :param rollback_graph_name:
        :param use_existing_rollback_graph:
        :return:
        """

        try:
            log.info("[Delete_big_ttl_transaction]: Start")
            result_save_rolback_ttl = False
            if not use_existing_rollback_graph:
                result_save_rollback_ttl = self.insert_big_ttl_with_transaction(rollback_graph_name, ttl_delete, rollback_graph_name+"_temp")
                if result_save_rollback_ttl:
                    log.info("[Delete_big_ttl_transaction]. Save rollback graph successful")
                else:
                    log.error("Delete_big_ttl_transaction]. Save rollback graph failed")
                    return False
            import time
            start = time.time()
            result_complet_delete_ttl = self.execute_update_query("DELETE {{ GRAPH <{0}> {{ ?s ?p ?o }} }} WHERE "
                                                                  "{{ GRAPH <{1}> {{ ?s ?p ?o }} }}".
                                                                  format(graph_name,rollback_graph_name))

            if not result_complet_delete_ttl:
                log.error("[Delete_big_ttl_transaction]. Delete from the graph {0}: Failed".format(graph_name))
                log.info("[Delete_big_ttl_transaction]. Start rollback from graph: {0}".format(rollback_graph_name))
                result_rollback_query = self.rollback_from_graph(graph_name,rollback_graph_name)
            return result_complet_delete_ttl
        except BaseException as e:
            log.error("[Delete_big_ttl_transaction]. Failed. Start rollback")
            log.error(traceback.print_exc(e))
            result_rollback_query = self.rollback_from_graph(graph_name, rollback_graph_name)
        finally:
            if not use_existing_rollback_graph:
                self.graph_remove(rollback_graph_name)

    def rollback_from_graph(self, main_graph, rollback_graph):
        copy_graph = "INSERT {{GRAPH <{0}> {{ ?s ?p ?o }} }} WHERE " \
                     "{{ GRAPH <{1}> {{ ?s ?p ?o }} }}".format(main_graph, rollback_graph)
        result_rollback_query = self.execute_update_query(copy_graph)
        if result_rollback_query:
            log.info("[Delete_big_ttl_transaction]. Rollback: successful")
        else:
            log.info("[Delete_big_ttl_transaction]. Rollback from graph: Failed")
        return result_rollback_query



    def get_list_resources_by_class(self, graph_name, class_uri):
        try:
            sparql_query = "SELECT  * FROM <{0}> WHERE {{?instance a <{1}> }}" \
                .format(graph_name, class_uri)
            list_instances = self.execute_select_query_auth(sparql_query)
            list_uris = [instance.get("instance").get('value') for instance in list_instances]
            return list_uris
        except BaseException as e:
            return False


    # get the list of all properties with thier values
    def get_all_properties_value(self, graph_name, resources_uri):
        try:
            sparql_query = "SELECT  ?property ?value FROM <{0}> WHERE {{ {1} ?property ?value }}" \
                .format(graph_name, resources_uri)
            property_values = self.execute_select_query_auth(sparql_query)
            return property_values

        except BaseException as e:
            return False

    # get the values of the property
    def get_property_values(self, graph_name, resource_uri, property_uri):
        try:
            sparql_query = "SELECT  ?property ?value FROM <{0}> WHERE {{ {1} {2} ?value}}" \
                .format(graph_name, resource_uri, property_uri)
            property_values = self.execute_select_query_auth(sparql_query)
            return property_values

        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def add_property_values(self, graph_name, resource_uri, property_uri, new_values):
        try:
            list_values = ", ".join(new_values)
            str_list_property_values = "{0} {1} {2}".format(resource_uri, property_uri, list_values)
            result = self.execute_insert_ttl(graph_name, str_list_property_values)
            return result
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def update_property_values(self, graph_name, resource_uri, property_uri, new_arr_values):
        try:
            list_values = ", ".join(new_arr_values)
            to_remove = " {0} {1} ?old_values ".format(resource_uri, property_uri)
            new_ttls = "{0} {1} {2} .".format(resource_uri, property_uri, list_values)
            condition = to_remove
            result = self.execute_update_ttl(graph_name, to_remove, new_ttls, condition)
            return result
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    # to set the value of the property with a unique value
    def update_property_value(self, graph_name, resource_uri, property_uri, value_property):
        try:
            self.update_property_values(graph_name, resource_uri, property_uri, [value_property])
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    # set all properties values of a resource, remove old ones.
    def set_all_properties_values(self, graph_name, resource_uri, new_dict_prop_values):
        try:

            # create the core of the insert query
            ttl_all_values = ""
            for prop, val_prop in new_dict_prop_values.iteritems():
                ttl_val_prop = " {0} {1} {2} .".format(resource_uri, prop, " , ".join(val_prop))
                ttl_all_values = "{0} {1} ".format(ttl_all_values, ttl_val_prop)
            delete = "{0} ?p ?o".format(resource_uri)
            insert = "{0} ".format(ttl_all_values)
            condition = delete
            result = self.execute_update_ttl(graph_name, delete, insert, condition)
            return result

        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def set_all_properties_values_as_ttl(self, graph_name, resource_uri, new_ttl_prop_values):
        """
        :param graph_name:
        :param resource_uri:
        :param new_ttl_prop_values:
        :return:
        """
        try:

            # create the core of the insert query
            ttl_all_values = new_ttl_prop_values
            delete = "{0} ?p ?o".format(resource_uri)
            insert = "{0} ".format(ttl_all_values)
            condition = delete
            result = self.execute_update_ttl(graph_name, delete, insert, condition)
            return result

        except BaseException as e:
            return False


    def get_property_value_by_language(self, graph_name, resource_uri, property_uri, lang):
        try:
            sparql_query = "SELECT  ?value FROM <{0}> WHERE {{ {1} {2} ?value. FILTER (lang (?value)='{3}')}}" \
                .format(graph_name, resource_uri, property_uri, lang)
            property_values = self.execute_select_query_auth(sparql_query)
            return property_values

        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def get_all_different_text_value_by_language_or_without(self, graph_names, resource_uri, property, lang):
        '''

        :param list graph_names: The list of graph to query
        :param resource_uri:
        :param property:
        :param lang:
        :return:
        '''
        try:
            graph_from = ''
            if not isinstance(graph_names,list):
                graph_names = [graph_names]
            for graph_name in graph_names:
                if graph_name:
                    graph_from += 'FROM <{0}> '.format(graph_name)

            sparql_query = "SELECT DISTINCT ?value {0}{{ {1} {2} ?o . bind(str(?o) as ?value) . FILTER (lang(?o) IN ('{3}', ''))}} " \
                .format(graph_from, resource_uri, property, lang)
            result = self.execute_select_query_auth(sparql_query)
            return result
        except BaseException as e:
            log.error("get_all_different_text_value_by_language_or_without failed")
            log.error(traceback.print_exc(e))
            return False

    def get_related_triples(self, graph_name, ressource_uri):
        try:
            sparql_query = "DESCRIBE {0} from <isolation>".format(ressource_uri);
            result = self.execute_select_query_auth(sparql_query)
            return result
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def check_if_spo_exists(self, graph_name, resource_uri, property_uri, value):
        try:
            sparql_query = "ASK FROM <{0}> WHERE {{<{1}> <{2}> {3}}}" \
                .format(graph_name, resource_uri, property_uri, value)
            asked = self.execute_ask_query_auth(sparql_query)
            return asked
        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def get_subjects_by_property_value(self, graph_name, resource_uri, value):
        try:
            sparql_query = "SELECT  ?value FROM <{0}> WHERE {{ ?value {1} {2}}}" \
                .format(graph_name, resource_uri, value)
            property_values = self.execute_select_query_auth(sparql_query)
            return property_values

        except BaseException as e:
            log.error(traceback.print_exc(e))
            return False

    def find_subject_for_where_clauses(self, graph_name=str, triplet_list=None, order_by_clause=""):
        return self.find_any_for_where_clauses(graph_name=graph_name, triplet_list=triplet_list,
                                               result_clause=SUBJECT_WITH_SPACES, order_by_clause=order_by_clause)

    def find_predicate_for_where_clauses(self, graph_name=str, triplet_list=None, order_by_clause=""):
        return self.find_any_for_where_clauses(graph_name=graph_name, triplet_list=triplet_list,
                                               result_clause=PREDICATE_WITH_SPACES, order_by_clause=order_by_clause)

    def find_object_for_where_clauses(self, graph_name=str, triplet_list=None, order_by_clause=""):
        return self.find_any_for_where_clauses(graph_name=graph_name, triplet_list=triplet_list,
                                               result_clause=OBJECT_WITH_SPACES, order_by_clause=order_by_clause)

    def find_subject_and_predicate_for_where_clauses(self, graph_name=str, triplet_list=None, order_by_clause=""):
        return self.find_any_for_where_clauses(graph_name=graph_name, triplet_list=triplet_list,
                                               result_clause=SUBJECT_WITH_SPACES + PREDICATE_WITH_SPACES,
                                               order_by_clause=order_by_clause)

    def find_subject_and_object_for_where_clauses(self, graph_name=str, triplet_list=None, order_by_clause=""):
        return self.find_any_for_where_clauses(graph_name=graph_name, triplet_list=triplet_list,
                                               result_clause=SUBJECT_WITH_SPACES + OBJECT_WITH_SPACES,
                                               order_by_clause=order_by_clause)

    def find_subject_and_object_in_graphs_for_where_clauses(self, graph_names=list, triplet_list=None,
                                                            order_by_clause=""):
        return self.find_any_in_graphs_for_where_clauses(graph_names=graph_names, triplet_list=triplet_list,
                                                         result_clause=SUBJECT_WITH_SPACES + OBJECT_WITH_SPACES,
                                                         order_by_clause=order_by_clause)

    def find_predicate_and_object_for_where_clauses(self, graph_name=str, triplet_list=None, order_by_clause=""):
        return self.find_any_for_where_clauses(graph_name=graph_name, triplet_list=triplet_list,
                                               result_clause=PREDICATE_WITH_SPACES + OBJECT_WITH_SPACES,
                                               order_by_clause=order_by_clause)

    def find_all_for_where_clauses(self, graph_name=str, triplet_list=None, order_by_clause=""):
        return self.find_any_for_where_clauses(graph_name=graph_name, triplet_list=triplet_list,
                                               result_clause=SUBJECT_WITH_SPACES + PREDICATE_WITH_SPACES + OBJECT_WITH_SPACES,
                                               order_by_clause=order_by_clause)

    def find_any_for_where_clauses(self, graph_name=str, triplet_list=None, result_clause=WILDCARD_WITH_SPACES,
                                   order_by_clause=""):
        return self.find_any_in_graphs_for_where_clauses([graph_name], triplet_list, result_clause,
                                                         order_by_clause=order_by_clause)

    def find_any_in_graphs_for_where_clauses(self,
                                             graph_names=list,
                                             triplet_list=dict,
                                             result_clause=WILDCARD_WITH_SPACES,
                                             limit=0,
                                             offset=0,
                                             order_by_clause=""):
        if graph_names is None:
            graph_names = [DCATAPOP_PUBLIC_GRAPH_NAME]

        if triplet_list is None:
            triplet_list = [Triplet(SUBJECT_WITH_SPACES, PREDICATE_WITH_SPACES, "")]
        try:
            sparql_query = "SELECT * {{"
            sparql_query += "SELECT" + result_clause
            for graph_name in graph_names:
                sparql_query += " FROM <{0}> ".format(graph_name)
            sparql_query += "WHERE {"
            for triplet in triplet_list:
                if triplet.subject:
                    if triplet.subject[0] == '?':
                        sparql_query += triplet.subject + " "
                    else:
                        sparql_query += " <" + triplet.subject + "> "
                else:
                    sparql_query += SUBJECT_WITH_SPACES
                if triplet.predicate:
                    if triplet.predicate[0] == '?':
                        sparql_query += triplet.predicate + " "
                    else:
                        sparql_query += " <" + triplet.predicate + "> "
                else:
                    sparql_query += PREDICATE_WITH_SPACES
                if triplet.object:
                    if triplet.object[0] == '?':
                        sparql_query += triplet.object + " "
                    else:
                        sparql_query += " <" + triplet.object + "> "
                else:
                    sparql_query += OBJECT_WITH_SPACES
                if triplet.filter:
                    sparql_query += triplet.filter
                sparql_query += "."
                sparql_query = sparql_query
            sparql_query += "}"
            sparql_query += ORDER_BY
            if order_by_clause:
                order_by_statement = order_by_clause
            else:
                if result_clause == WILDCARD_WITH_SPACES:
                    log.warn('Error Sparql query with offset and no variable to perform order by')
                    order_by_statement = SUBJECT_WITH_SPACES
                else:
                    order_by_statement = result_clause
            sparql_query += order_by_statement

            offset_statement = ""
            limit_statement = ""
            if offset > 0:
                offset_statement = " OFFSET " + str(offset)
            sparql_query += " }} "
            if limit > 0:
                limit_statement = " LIMIT " + str(limit)

            sparql_query += offset_statement + limit_statement
            log.debug(sparql_query)
            property_values = self.execute_select_query_auth(sparql_query)
            if len(property_values) == MAX_RESULT_PER_REQUEST:
                return property_values + self.find_any_in_graphs_for_where_clauses(graph_names, triplet_list,
                                                                                   result_clause,
                                                                                   limit=MAX_RESULT_PER_REQUEST,
                                                                                   offset=offset + MAX_RESULT_PER_REQUEST)
            return property_values

        except BaseException as e:
            log.error(sparql_query)
            log.error(traceback.print_exc(e))
            return False

    def find_graph_of_dataset(self,dataset_uri):
        """

        :param str dataset_uri:
        :return str:
        """
        try:
            query = "select * from named <dcatapop-public> from named <dcatapop-private> " \
                "where {{graph ?graph {{<{0}> a <http://www.w3.org/ns/dcat#Dataset>}}}}".format(dataset_uri)
            result = self.execute_select_query_auth(query)
            return result
        except BaseException as e:
            log.error("[TS_Helper] [find the graph of dataset ][Failed] [Dataset:{0}]".format(dataset_uri))




    def _chunk_ttl(self,ttl_string):
        '''

        :param ttl_string:
        :return:
        '''

        max_size_chunk = MAX_TRIPLETS_IN_ONE_QUERY
        list_ttl = ttl_string.splitlines()
        list_chunks = [list_ttl[i:i + max_size_chunk] for i in xrange(0, len(list_ttl), max_size_chunk)]
        list_chunk_ttl_string = map(lambda x:"\r".join(x),list_chunks)
        return list_chunk_ttl_string

    def build_chunked_query_from_ttl(self, query_type, graph_name, ttl_string):
        '''

        :param query_type:
        :param graph_name:
        :param ttl_string:
        :return:
        '''

        list_chunk_ttl_string = self._chunk_ttl(ttl_string)
        complete_chunked_query = ""
        for ttl_string in list_chunk_ttl_string:
            if len(ttl_string)>1:
                sparql_query = "{0} DATA {{GRAPH <{1}> {{ {2} }} }}".format(query_type, graph_name, ttl_string)
                complete_chunked_query = "{0}\n\r{1}".format(complete_chunked_query, sparql_query)
        return complete_chunked_query


    def build_transactional_insert(self, graph_name, ttl_string, temp_graph):
        """
        Build the insert sparql query
        :param graph_name:
        :param ttl_string:
        :param temp_graph:
        :return:
        """
        temp_transactional_graph = temp_graph
        transactional_pool_queries = []
        drop_temporary_graph = "DROP SILENT GRAPH <{0}>".format(temp_transactional_graph)
        temp_complete_insert_ttl = self.build_chunked_query_from_ttl("INSERT", temp_transactional_graph, ttl_insert)
        copy_graph = "INSERT {{GRAPH <{0}> {{ ?s ?p ?o }} }} WHERE {{ GRAPH <{1}> {{ ?s ?p ?o }} }}".format(graph_name, temp_transactional_graph)

        transactional_pool_queries =[drop_temporary_graph,
                                     temp_complete_insert_ttl,
                                     copy_graph,
                                     drop_temporary_graph]
        transactional_query = "\n".join(transactional_pool_queries)
        return transactional_query

    def build_transactional_delete_ttl(self, graph_name, ttl_string, rollback_graph_name, use_exiting_rollback_graph = False):
        """
        Build a delete query
        :param graph_name:
        :param ttl_string:
        :param temp_graph:
        :return: str
        """


        transactional_pool_queries = []
        drop_temporary_graph = ""
        temp_complete_insert_rolleback_ttl = ""
        if not use_exiting_rollback_graph:
            drop_temporary_graph = "DROP SILENT GRAPH <{0}>".format(rollback_graph_name)
            temp_complete_insert_rolleback_ttl = self.build_chunked_query_from_ttl("INSERT", rollback_graph_name, ttl_insert)
        complete_delete_ttl = self.build_chunked_query_from_ttl("DELETE", graph_name, ttl_string)
        transactional_pool_queries = [drop_temporary_graph,
                                      temp_complete_insert_rolleback_ttl,
                                      complete_delete_ttl]
        transactional_query = "\n".join(transactional_pool_queries)
        return transactional_query

    def create_name_of_graph(self, rdf_string_content):
        """
        :param rdf_string_content: string that represents a rdf.
        :return: None if failure, a graph name otherwise.
        """
        try:
            GRAPH_NAMESPACE = "TEMP_TRANSACTIONAL_"

            import hashlib
            import uuid
            if isinstance(rdf_string_content, basestring):
                content_md5 = hashlib.md5(rdf_string_content.encode('utf8')).hexdigest()
            else:
                content_md5 = hashlib.md5(rdf_string_content.decode('utf8').encode('utf8')).hexdigest()
            # graph_name = GRAPH_NAMESPACE + content_md5
            graph_name = GRAPH_NAMESPACE + str(uuid.uuid4())
            return graph_name
        except BaseException as e:
            import traceback
            log.error(traceback.print_exc())
            log.error("Create name of graph failed")
            return None

def create_chunks_from_list(list_to_transform, chunk_size=1):
    """Yield successive n-sized create_chunks_from_list from list_to_transform."""
    for i in xrange(0, len(list_to_transform), chunk_size):
        yield list_to_transform[i:i + chunk_size]

