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

from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP


class IdentifierSchemaDcatApOp(SchemaGeneric):

    rdf_type = NAMESPACE_DCATAPOP.adms + 'Identifier'

    def __init__(self, uri, graph_name = "dcatapop-public"):
        super(IdentifierSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(IdentifierSchemaDcatApOp.rdf_type, graph_name)
        self.schemeAgency_adms = {} # type: dict[str,ResourceValue]
        self.issued_dcterms = {} # type: dict[str,ResourceValue]
        self.notation_skos = {} # type: dict[str,ResourceValue]
        self.creator_dcterms = {}  # type:dict[str, AgentSchemaDcatApOp]
