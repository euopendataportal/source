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

from ckanext.ecportal.virtuoso.utils_triplestore_crud_core import VirtuosoCRUDCore
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers

class TripleStoreIngestionCore(VirtuosoCRUDCore):
    def __init__(self):
        self.crud_helper = TripleStoreCRUDHelpers()

    def ingest_graph_to_virtuoso(self, graph_name, graph_object):
        try:
            # TODO: Optimize with Turtle if possible
            ttl_formated = graph_object.serialize(format='nt')
            self.crud_helper.execute_insert_ttl(graph_name, ttl_formated)
        except BaseException as e:
            return False
