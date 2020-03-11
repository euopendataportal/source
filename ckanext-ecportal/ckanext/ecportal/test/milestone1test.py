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

# from unittest import TestCase
from ckanext.ecportal.virtuoso.utils_triplestore_ingestion_helpers import TripleStoreIngestionHelpers as tsih

from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers as tsch

logging.basicConfig(level=logging.DEBUG)

vsc = tsih()

crud_helper = tsch()
a = 0


def setup():
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
    crud_helper.execute_update_query(sparql_query)
    logging.info("Setup of data done")


def restoretest():
    setup()
    ingestion_files()


def ingestion_files():
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



    except BaseException as e:

        return None


def get_description_from_ts():
    ds1 = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
    ds2 = DatasetDcatApOp("http://data.europa.eu/999/dataset/dgt-translation-memory-V3")
    ds_private = DatasetDcatApOp("http://data.europa.eu/999/dataset/dgt-translation-memory-V4", privacy_state="private",
                                 graph_name=DCATAPOP_PRIVATE_GRAPH_NAME)

    # extract the dontent from graphs

    desc1 = ds1.get_description_from_ts()
    desc2 = ds2.get_description_from_ts()
    desc_private = ds_private.get_description_from_ts()

    ckan_name1 = ds1.schema.ckanName_dcatapop['0'].value_or_uri
    ckan_name2 = ds2.schema.ckanName_dcatapop['0'].value_or_uri
    ckan_name_private = ds_private.schema.ckanName_dcatapop['0'].value_or_uri
    keywords1 = ds1.schema.keyword_dcat
    # rv = ResourceValue()

    print "Dataset: http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2"
    print "CkanName is : {0} ".format(ckan_name1)
    print "keywords are :".format()
    for k, rv in keywords1.iteritems():
        print "lnaguage '{0}' has the value '{1}'".format(rv.lang, rv.value_or_uri)

        # print "Dataset: http://data.europa.eu/999/dataset/dgt-translation-memory-V3"
        # print "CkanName is : {0} ".format(ckan_name2)
        # print "keywords are :".format()
        # for k, rv in ds2.schema.keyword_dcat.iteritems():
        #     print "lnaguage '{0}' has the value '{1}'".format(rv.lang, str(rv.value_or_uri))


        # print "CkanName of {0} is {1} ".format("http://data.europa.eu/999/dataset/dgt-translation-memory-V3",ckan_name2)
        # print "CkanName of {0} is {1} ".format("http://data.europa.eu/999/dataset/dgt-translation-memory-V4",ckan_name_private)


def edit_save_to_ts():
    ds1 = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
    if ds1.get_description_from_ts():
        ds1.privacy_state = "public"
        ds1.schema.ckanName_dcatapop['0'].value_or_uri = "NEW CKAN NAME"
        ds1.schema.keyword_dcat['fr'] = ResourceValue(u'la réussite', lang="fr")
        ds1.schema.keyword_dcat['grg'] = ResourceValue(u'επιτυχία', lang="gr")
        ds1.schema.contactPoint_dcat['0'].hasTelephone_vcard['0'].hasValue_vcard['0'].uri = "TEL:213232323"
        if ds1.save_to_ts():
            print " Save done"
        ds1after = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        ds1after.get_description_from_ts()
        pass


def save_as_public():
    ds_private = DatasetDcatApOp("http://data.europa.eu/999/dataset/dgt-translation-memory-V4", privacy_state="private",
                                 graph_name=DCATAPOP_PRIVATE_GRAPH_NAME)
    ds_private.privacy_state = 'public'
    ds_private.get_description_from_ts()
    ds_private.save_to_ts()


# setup()
ingestion_files()
# get_description_from_ts()
# edit_save_to_ts()
# save_as_public()
