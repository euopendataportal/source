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

from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric

class LinguisticSystemSchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri, graph_name = "dcatapop-public"):
        # super(LinguisticSystemSchemaDcatApOp, self).__init__(uri, graph_name, default_type={'0':SchemaGeneric(schema.LANGUAGE_DCTERMS)})
        super(LinguisticSystemSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.dcterms + "LinguisticSystem", graph_name)


class RightsStatementSchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(RightsStatementSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.dcterms + "RightsStatement", graph_name)
        self.label_rdfs = {}


class LiteralSchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(LiteralSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.rdfs + "Literal", graph_name)


class LocationSchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(LocationSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.dcterms + "Location", graph_name)


class MediaTypeOrExtentSchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(MediaTypeOrExtentSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.dcterms + "MediaTypeOrExtent", graph_name)


class StandardSchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(StandardSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.dcterms + "Standard", graph_name)


class FrequencySchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(FrequencySchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.dcterms + "Frequency", graph_name)


class ProvenanceStatementSchemaDcatApOp(SchemaGeneric):
    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(ProvenanceStatementSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(NAMESPACE_DCATAPOP.spdx + "ProvenanceStatement", graph_name)


