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

from tenacity import *
from SPARQLWrapper.SPARQLExceptions import EndPointNotFound
from SPARQLWrapper import SPARQLWrapper, JSON, DIGEST
from pylons import config
from ckanext.ecportal.configuration.configuration_constants import VIRTUOSO_HOST_NAME, VIRTUOSO_USER_NAME
from ckanext.ecportal.virtuoso.common_constants import VIRTUOSO_HOST_NAME_AUTHENTICATED, \
    DEFAULT_VIRTUOSO_PASSWORD, VIRTUOSO_PASSWORD, DEFAULT_VIRTUOSO_USERNAME, VIRTUOSO_DEFAULT_GRAPH, \
    DEFAULT_GRAPH_VALUE

log = logging.getLogger(__file__)
import traceback


class VirtuosoCRUDCore:
    _virtuoso_host_name = ""
    _virtuoso_host_name_auth = ""
    _virtuoso_user_name = ''
    _virtuoso_password = ''
    _sparql_client = None
    _default_graph = ""
    # TODO: both variables are not used
    _virtuoso_query_return = ""
    _sparql_query = ""

    def __init__(self):
        # create the object SPARQLWrapper


        # TODO: more explicit variables name
        vhn = config.get(VIRTUOSO_HOST_NAME)
        vhna = config.get(VIRTUOSO_HOST_NAME_AUTHENTICATED)
        # vhn = config.get('virtuoso.host.name', 'http://192.168.99.100:8890/sparql')
        # vhna = config.get('virtuoso.host.name.auth', 'http://192.168.99.100:8890/sparql-auth')

        if vhn is None or vhna is None:
            logging.error(
                "The configuration has not been set properly. Please check the parameters virtuoso.host.name and virtuos.host.name.auth")
            raise BaseException(
                "The configuration has not been set properly. Please check the parameters virtuoso.host.name and virtuos.host.name.auth")

        self._virtuoso_host_name = vhn
        self._virtuoso_host_name_auth = vhna

        # self._virtuoso_host_name = config.get('virtuoso.host.name', 'http://10.68.0.88:8890/sparql')
        # self._virtuoso_host_name_auth = config.get('virtuoso.host.name.auth', "http://192.168.35.11/sparql-auth")
        self._virtuoso_user_name = config.get(VIRTUOSO_USER_NAME, DEFAULT_VIRTUOSO_USERNAME)
        self._virtuoso_password = config.get(VIRTUOSO_PASSWORD, DEFAULT_VIRTUOSO_PASSWORD)
        self._default_graph = config.get(VIRTUOSO_DEFAULT_GRAPH, DEFAULT_GRAPH_VALUE)
        # create the wrapper object

        self._sparql_client = SPARQLWrapper(self._virtuoso_host_name_auth)
        self._sparql_client.setReturnFormat(JSON)

    def set_virtuoso_host_name(self, virtuoso_host_name):
        self._virtuoso_host_name = virtuoso_host_name

    def set_virtuoso_host_name_auth(self, virtuoso_host_name_auth):
        self._virtuoso_host_name_auth = virtuoso_host_name_auth

    def get_virtuoso_query_return(self):
        return self._virtuoso_query_return

    # authentication with DIGEST used by virtuoso
    def _authentication_to_triplestore(self):
        try:
            self._virtuoso_query_return = ""
            self._sparql_client.setHTTPAuth(DIGEST)
            self._sparql_client.setCredentials(self._virtuoso_user_name, self._virtuoso_password)
            return True
        except BaseException as e:
            log.error("_authentication_to_triplestore failed")
            return False

    def execute_select_query(self, sparql_query):
        try:
            self._virtuoso_query_return = ""
            self._sparql_client_without_auth = SPARQLWrapper(self._virtuoso_host_name)
            self._sparql_client_without_auth.setQuery(sparql_query)
            self._sparql_client_without_auth.setReturnFormat(JSON)

            results = self._sparql_client_without_auth.query().convert()
            final_result = results["results"]["bindings"]
            return final_result
        except BaseException as e:
            log.error("[TS_crud]. execute select query failed {0}".format(sparql_query))

            return None

    @retry(wait=wait_fixed(2),retry=retry_if_exception_type(EndPointNotFound), stop=stop_after_attempt(3))
    def execute_select_query_auth(self, sparql_query):
        try:
            start = time.time()
            self._virtuoso_query_return = ""
            self._authentication_to_triplestore()
            self._sparql_client.setQuery(sparql_query)
            self._sparql_query = sparql_query
            results = self._sparql_client.query().convert()
            final_result = results["results"]["bindings"]
            duration = time.time() - start
            log.debug("[TS_crud]. [execute select query, successful] [Duration: {0}], [Query: {1}] ".format(duration, sparql_query))
            return final_result
        except BaseException as e:
            msg = "Error executing query {0}; error {1}".format(sparql_query, e)
            log.error(msg)
            if isinstance(e,EndPointNotFound):
                raise e
            return None

    @retry(wait=wait_fixed(2),retry=retry_if_exception_type(EndPointNotFound), stop=stop_after_attempt(3))
    def execute_ask_query_auth(self, sparql_query):
        try:
            self._virtuoso_query_return = ""
            self._authentication_to_triplestore()
            self._sparql_client.setQuery(sparql_query)
            self._sparql_query = sparql_query
            results = self._sparql_client.query().convert()
            final_result = results["boolean"]
            log.debug("query {0} successful".format(sparql_query))
            return final_result
        except BaseException as e:
            msg = "Error executing query {0}; error {1}".format(sparql_query, e)
            log.error(msg)
            if isinstance(e,EndPointNotFound):
                raise e
            return None

    # The update query uses always the authentication
    def execute_update_query(self, sparql_query):
        try:
            start = time.time()
            self._virtuoso_query_return = ""
            self._authentication_to_triplestore()
            self._sparql_client.setMethod("POST")
            self._sparql_client.isSparqlUpdateRequest()
            self._sparql_client.setQuery(sparql_query)
            self._sparql_query = sparql_query
            results = self._sparql_client.query().convert()
            # put the returned message of virtuoso in this _virtuoso_query_return
            self._virtuoso_query_return = results["results"]['bindings'][0]['callret-0']['value']
            duration = time.time() - start
            log.debug("[TS_crud_helper]. [Execute update query successful], [Duration: {0}]. [Message: {1}]".format(duration,self.get_virtuoso_query_return()))
            log.debug("Sparql query is successful. {0}".format(sparql_query))
            return True
        except BaseException as e:
            log.error("[TS_Crud]. execute update query failed. {0}".format(sparql_query))
            log.error(traceback.print_exc(e))
            return False

    def check_server_status(self):
        try:
            self._authentication_to_triplestore()
            self._sparql_client.setMethod("POST")
            sparql_query = "ASK where {?s ?p ?o}"
            self._sparql_client.setQuery(sparql_query)
            results = self._sparql_client.query().convert()
            return results["boolean"]
        except BaseException as e:
            log.error("check_server_status")
            return False
