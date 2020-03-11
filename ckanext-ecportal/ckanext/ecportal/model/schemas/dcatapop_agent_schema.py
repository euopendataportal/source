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

from ckanext.ecportal.migration import migration_constants
from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric, ResourceValue
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP


class AgentSchemaDcatApOp(SchemaGeneric):  # TODO: Wait OP feedback to have the Ontology definition
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(AgentSchemaDcatApOp, self).__init__(uri, graph_name)

        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.foaf + migration_constants.CLASS_AGENT, graph_name)
        self.name_foaf = {}  # type: dict[str,ResourceValue]
        self.type_dcterms = {}  # type: dict[str, SchemaGeneric]
