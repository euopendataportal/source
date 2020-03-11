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

import time
import datetime
import pickle
from ckanext.ecportal.model.common_constants import *
from ckanext.ecportal.lib import uri_util
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric, NAMESPACE_DCATAPOP, ResourceValue
from rdflib import XSD
import base64
import logging
log = logging.getLogger(__file__)
import traceback
# from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp


class RevisionSchemaDcatApOp(SchemaGeneric):


    def __init__(self, dataset_to_put_in_revision=None, author='api', uri_direct=None, revision_id=''):
        '''

        :param is_revision_of:
        :param schema_to_put_in_revision:
        :param author:
        :param uri_direct:
        '''

        self.author_revision = {}
        self.timestamp_revision = {}
        self.isRevisionOf_revision = {}
        self.logMessage_revision = {}
        self.ckanRevisionId_revision = {} # type: dict[str, ResourceValue]
        self.graph_name = DCATAPOP_REVISION_GRAPH_NAME

        try:

            if uri_direct:
                super(RevisionSchemaDcatApOp, self).__init__(uri_direct)
                self.graph_name = DCATAPOP_REVISION_GRAPH_NAME
                # SchemaGeneric.__init__(self,uri_direct)

            # for key, value in dict1.iteritems():
            #     if value and key not in self.inconvertable_parameters:
            #         setattr(self,key,value)
            else:

                if dataset_to_put_in_revision:

                    content_dataset = pickle.dumps(dataset_to_put_in_revision)
                    content_dataset_base64 = base64.encodestring(content_dataset)
                    is_revision_of = dataset_to_put_in_revision.dataset_uri
                    self.uri = uri_util.create_revision_uri()
                    self.type_rdf = {"0": SchemaGeneric(NAMESPACE_DCATAPOP.revision)}
                    self.isRevisionOf_revision = {'0': SchemaGeneric(is_revision_of)}

                    self.contentDataset_revision = {'0': ResourceValue(content_dataset_base64)}

                    self.author_revision = {'0': ResourceValue(author)}
                    self.logMessage_revision = {}
                    current_datetime = datetime.datetime.fromtimestamp(time.time())
                    self.timestamp_revision = {'0': ResourceValue(current_datetime, type="typed-literal",datatype=XSD.date)}
                    if revision_id:
                        self.ckanRevisionId_revision['0'] = ResourceValue(revision_id)
                    self.save_revision_to_ts()

        except BaseException as e:
            log.error("Revision can not be created. uri: {0}".format(dataset_to_put_in_revision.dataset_uri))
            log.error(traceback.print_exc(e))
            return None

    def save_revision_to_ts(self):
        '''
        optimized saving of th revision by creating the ttl manually. the serializer of rdflib takes long time in the case of a huge literal
        :return:
        '''
        try:
            from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
            content = self.contentDataset_revision.get('0', ResourceValue).value_or_uri
            content = content.encode('string_escape')
            self.contentDataset_revision = {}
            tripleStoreCRUDHelpers = TripleStoreCRUDHelpers()
            g = self.convert_to_graph_ml()
            ttl_before_content = self.convert_to_graph_ml().serialize(format='nt')
            #build the triple manually to
            content_triple = ' <{0}> <{1}> "{2}" .'.format(self.uri,"http://data.europa.eu/88u/revision#contentDataset",content)
            ttl_revision = ttl_before_content + content_triple
            r = tripleStoreCRUDHelpers.set_all_properties_values_as_ttl(self.graph_name, "<" + self.uri + ">", ttl_revision)
        except BaseException as e:
            log.error("Revision can not be saved. uri: {0}".format(self.isRevisionOf_revision.get('0').uri))
            log.error(traceback.print_exc(e))
            raise e

