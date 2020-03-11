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

from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers as tsch
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_helpers import TripleStoreIngestionHelpers as tsih

logging.basicConfig(level=logging.DEBUG)

vsc = tsih()

crud_helper = tsch()
a = 0

uri_prefix = "http://data.europa.eu/88u/dataset/"

def setUp():
    # todo use a specific method from the unit package
    """
    to be used for all the methods T
    :return:
    """
    sparql_query = """
        drop silent graph <testGraph>

        create silent graph <testGraph>

        drop silent graph <testGraph2>
        create silent graph <testGraph2>

        drop silent graph <DcatApOPPublic>
        create silent graph <DcatApOPPublic>

        drop silent graph <dcatapop-public>
        create silent graph <dcatapop-public>

        drop silent graph <dcatapop-private>
        create silent graph <dcatapop-private>

        drop silent graph <dcatapop-ingestion-test>
        create silent graph <dcatapop-ingestion-test>


        """
    # crud_helper.execute_update_query(sparql_query)


setUp()


class TestIngestionHelpers(TestWithVirtuosoConfiguration):
    def tearDown(self):
        pass

    def test_ingest_graph_from_rdf_file(self):
        vsc.ingest_graph_from_rdf_file("testGraph",
                                       "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/testVirtuoso.owl")
        properties = crud_helper.get_all_properties_value("testGraph", "<http://www.arhs-cube.com#name>")
        self.assertEqual(len(properties), 3, "ingest_rdf_file_to_virtuoso : The number of properties ingested is wrong")

    def test_ingest_graph_from_input_file(self):
        file_content = ""
        with open(
                "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/testVirtuoso.owl") as f:
            file_content = f.read()
        f.close()
        vsc.ingest_graph_from_string("testGraph2", file_content)
        properties = crud_helper.get_all_properties_value("testGraph2", "<http://www.arhs-cube.com#name>")
        self.assertEqual(len(properties), 3, "ingest_rdf_file_to_virtuoso : The number of properties ingested is wrong")

    def test_ingest_dataset(self):
        vsc.ingest_graph_from_rdf_file("DcatApOPPublic",
                                       "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/Dataset-example_withoutError.rdf",
                                       "application/rdf+xml")
        properties = crud_helper.execute_select_query_auth("SELECT * FROM <DcatApOPPublic> {?s ?p ?o}")

        self.assertEqual(len(properties), 259,
                         "ingest_rdf_file_to_virtuoso : The number of properties ingested is wrong, find {0}".format(
                             len(properties)))

    def test_ingest_from_string__transform_blanknod(self):
        import time
        size_set_of_datasets = 3
        with open(
                "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/Dataset-example_withoutError.rdf") as f:
            file_content = f.read()
        vsc.ingest_graph_from_string("dcatapop-ingestion-test", file_content)

        size_set_of_datasets -= 1
        for i in xrange(size_set_of_datasets):
            t = i + 1
            new_file_content = file_content.replace("dgt-translation-memory-V1-2",
                                                    "dgt-translation-memory-V1-2_{0}".format(t))
            new_file_content = new_file_content.replace("A freely Available Translation Memory in 22 Languages",
                                                        "title of the dataset {0}".format(t))
            new_file_content = new_file_content.replace("tel:086631722", "tel:691717713_{0}".format(t))
            new_file_content = new_file_content.replace("Jean-Monnet Building A2/137",
                                                        "Jean-Monnet Building A2/137_{0}".format(t))
            new_file_content = new_file_content.replace("23434", "{0}".format(int(t * 100)))
            new_file_content = new_file_content.replace("publisher V23 application",
                                                        "publisher V23 application_{0}".format(time.time()))
            new_file_content = new_file_content.replace("d588a398-3776-43ba-8b0c-b84c424d3d23",
                                                        "d588a398-3776-43ba-8b0c-b84c424d3d23_{0}".format(
                                                            time.time()))
            new_file_content = new_file_content.replace("Documentation of the xml file",
                                                        "Documentation of the xml file_{0}".format(time.time()))
            new_file_content = new_file_content.replace("3453", "3453{0}".format(int(t)))

            vsc.ingest_graph_from_string("dcatapop-ingestion-test", new_file_content)

        lstm = crud_helper.execute_select_query_auth("select * from <dcatapop-ingestion-test> where {?s ?p ?o}")
        sparql_query = "select " \
                       "(count(?o) as ?count_contactpoint) (count (?ou) as ?count_blanknode_contactpoint) " \
                       "from <dcatapop-ingestion-test>" \
                       "where {" \
                       "{?s <http://www.w3.org/ns/dcat#contactPoint> ?o.}" \
                       "union {" \
                       "?s <http://www.w3.org/ns/dcat#contactPoint> ?ou. filter isBlank(?ou) }}"

        list_blanknodes = crud_helper.execute_select_query_auth(sparql_query)
        count_contactpoint = int(list_blanknodes[0]['count_contactpoint']['value'])
        count_blanknode_contactpoint = int(list_blanknodes[0]['count_blanknode_contactpoint']['value'])
        count = len(lstm)
        self.assertEqual(count, 259 + (130 * size_set_of_datasets), "Select SPARQL is not working")
        self.assertTrue((count_contactpoint == size_set_of_datasets + 1) and (count_blanknode_contactpoint == 0),
                        "Error in convertion of blanknodes to URI")

    def test_ingestion_files(self):
        try:
            base_path = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/datasets/"
            with open(base_path + "dataset1.rdf") as f:
                file_content = f.read()
                vsc.ingest_graph_from_string(DCATAPOP_PUBLIC_GRAPH_NAME, file_content)
            with open(base_path + "dataset2.rdf") as f:
                file_content = f.read()
                vsc.ingest_graph_from_string(DCATAPOP_PUBLIC_GRAPH_NAME, file_content)
            with open(base_path + "dataset_private.rdf") as f:
                file_content = f.read()
                vsc.ingest_graph_from_string(DCATAPOP_PRIVATE_GRAPH_NAME, file_content)

            lstm_private = crud_helper.execute_select_query_auth("select * from <dcatapop-private> where {?s ?p ?o}")
            lstm_public = crud_helper.execute_select_query_auth("select * from <dcatapop-public> where {?s ?p ?o}")
            pass
        except BaseException as e:
            return None

    def test_build_embargo_datasets_from_string_content(self):
        base_path = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/datasets/"
        with open(base_path + "dataset1.rdf") as f:
            file_content = f.read()
        uri = "http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2"
        list_uris ={uri:None}
        list_embargo_datasets = vsc.build_embargo_datasets_from_string_content(file_content,list_uris)

        self.assertEqual(list_embargo_datasets[uri].schema.ckanName_dcatapop['0'].value_or_uri, "dgt-translation-memory-V1-2")
        pass

