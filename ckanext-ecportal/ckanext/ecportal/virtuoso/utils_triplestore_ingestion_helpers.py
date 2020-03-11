# -*- coding: utf-8 -*-
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
import urllib
import hashlib

from ckanext.ecportal.model.common_constants import *
from rdflib import Graph, URIRef, util, BNode

from ckanext.ecportal.lib.uri_util import create_blanknode_uri
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_core import TripleStoreIngestionCore
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp

from ckanext.ecportal.migration.dataset_transition_util import generate_doi_for_dataset

EMBARGO_NAMESPACE = "INGESTION_IN_PROGRESS_"
log = logging.getLogger(__file__)
def fix(s):
    i = s.rindex('/')
    return s[:i] + urllib.quote(s[i:])


class TripleStoreIngestionHelpers:
    def __init__(self):
        self.ingestion_core = TripleStoreIngestionCore()

    def ingest_graph_from_rdf_file(self, graph_name, rdf_file, format_file="xml"):
        try:
            guessed_format = util.guess_format(rdf_file)
            if guessed_format is not None:
                selected_format = guessed_format
            else:
                selected_format = format_file
            with open(rdf_file) as f:
                file_content = f.read()
            return self.ingest_graph_from_string(graph_name, file_content, selected_format)
        except BaseException as e:
            return False

    def ingest_graph_from_string(self, graph_name, input_string, format_input="xml"):
        try:
            g = Graph()
            g.parse(data=input_string, format=format_input)
            # Validate URIs
            # self.__check_URI(g)
            kg = self.__clean_not_valid_URI(g)
            gwbn = self.__convert_to_graph_without_blankNode(g)
            self.ingestion_core.ingest_graph_to_virtuoso(graph_name, gwbn)
            return True
        except BaseException as e:
            log.error("Ingestionr of RDF from string failed. {0}".format(str(e)))
            return False




    def __check_URI(self, graph):
        kg = Graph()
        tup = None
        errors = []
        for stm in graph:
            tup = stm
            for key in (0, 1, 2):
                if (isinstance(stm[key], URIRef)):
                    uri_stringified = str(stm[key])
                    if " " in uri_stringified:
                        errors.append((uri_stringified, "White space in URI"))

        if len(errors) > 0:
            for error in errors:
                logging.error("Invalid URI : \n {0}".format(error))

            raise ValueError("Some URIs are invalid, please check the logs")

    def __clean_not_valid_URI(self, graph):
        try:
            kg = Graph()
            tup = None
            for stm in graph:
                object_new = []
                tup = stm
                for key in (0, 1, 2):
                    if (isinstance(stm[key], URIRef)):
                        object_encode = str(stm[key]).replace(" ", "%20")
                        object_new.append(URIRef(object_encode))
                    else:
                        object_new.append(tup[key])

                tup = (object_new[0], object_new[1], object_new[2])
                kg.add(tup)
            return kg
        except BaseException as e:
            return None

    def __convert_to_graph_without_blankNode(self, graph):
        """
        :param Graph graph
        :rtype:Graph | None
        """
        try:
            ns_blanknode = "{0}{1}".format("http://blanknode",
                                           "#")  # TODO use the uri_util to create a valide name space
            gwbn = Graph()
            for s, p, o in graph.triples((None, None, None)):
                uri_s = s
                uri_o = o
                if isinstance(s, BNode):
                    # convert to uri
                    uri = create_blanknode_uri(str(s))
                    uri_s = URIRef(uri)
                if isinstance(o, BNode):
                    # convert to uri
                    uri = create_blanknode_uri(str(o))
                    uri_o = URIRef(uri)
                gwbn.add((uri_s, p, uri_o))
            return gwbn
        except BaseException as e:
            logging.error("Error in creating the uri of the blancknode")
            return None


    def build_embargo_datasets_from_string_content(self, rdf_string_content, dataset_description_map, format_input="xml", doi_flag=True):
        """
        To build a dict of datasets in embargo mode. The key of the dict is the uri, the value is the dataset object

        :param unicode rdf_string_content:
        :param map dataset_description_map:
        :rtype: dict[str, DatasetDcatApOp]
        """

        def create_name_of_graph(rdf_string_content):
            """
            :param rdf_string_content: string that represents a rdf.
            :return: None if failure, a graph name otherwise.
            """
            try:
                if isinstance(rdf_string_content, unicode):
                    content_md5 = hashlib.md5(rdf_string_content.encode('utf8')).hexdigest()
                else:
                    content_md5 = hashlib.md5(rdf_string_content.decode('utf8').encode('utf8')).hexdigest()
                graph_name = DCATAPOP_EMBARGO_NAMESPACE + content_md5
                return graph_name
            except BaseException as e:
                import traceback
                log.error(traceback.print_exc())
                log.error("Create name of graph failed")
                return None
        try:
            name_ingestion_graph = create_name_of_graph(rdf_string_content)
            list_embargo_datasets = {}
            if name_ingestion_graph:
                #  Create the embargo graph for the current job of ingestion
                tripleStoreCRUDHelpers = TripleStoreCRUDHelpers()
                tripleStoreCRUDHelpers.graph_remove(name_ingestion_graph)
                tripleStoreCRUDHelpers.graph_create(name_ingestion_graph)
                # load one time the content of rdf to virtuoso.
                if self.ingest_graph_from_string(name_ingestion_graph, rdf_string_content, format_input):
                    for dataset_uri, dataset_description in dataset_description_map.items():
                        embargo_dataset = DatasetDcatApOp(dataset_uri, DCATAPOP_INGESTION_DATASET, name_ingestion_graph)
                        embargo_dataset.privacy_state = DCATAPOP_INGESTION_DATASET
                        if embargo_dataset.get_description_from_ts():
                            # Generate DOI if requested
                            list_embargo_datasets[dataset_uri] = embargo_dataset

                            if dataset_description.generate_doi and doi_flag:
                                doi = generate_doi_for_dataset(embargo_dataset, dataset_description.generate_doi)
                                if doi:
                                    embargo_dataset.set_doi(doi)
                        else:
                            log.error("Ingest dataset from string error. Can not extract embargo dataset from graph. graph name"
                                      " [{0}]. dataset uri [{1}]".format(name_ingestion_graph,dataset_uri))
                            return None
                    return list_embargo_datasets
                else:
                    log.error("Ingest dataset from string failed. The ingestion to the embargo graph failed. graph "
                              "name [{0}]. content: [{1}]".format(name_ingestion_graph, rdf_string_content))
                    return None
            else:
                log.error("Ingest dataset from string failed. Can not create a the name of the embargo graph. Content "
                          "[{0}]".format(rdf_string_content.encode('utf-8')))

        except BaseException as e:
            import traceback
            log.error(traceback.print_exc())
            log.error(u"Ingest dataset from string failed. Exception {0}".format(str(e)))
            log.error(u"Ingest dataset from string failed. file content: [{0}]".format(rdf_string_content))
            return None
