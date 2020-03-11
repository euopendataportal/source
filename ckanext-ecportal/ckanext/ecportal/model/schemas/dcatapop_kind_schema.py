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

from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric





class KindSchemaDcatApOp(SchemaGeneric):

    rdf_type = NAMESPACE_DCATAPOP.vcard + "Kind"

    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(KindSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(KindSchemaDcatApOp.rdf_type, graph_name)

        self.organisationDASHname_vcard = {}  # type:dict[str,ResourceValue] Literal
        self.hasEmail_vcard = {}  # type: dict[str,SchemaGeneric]
        self.hasTelephone_vcard = {}  # type:dict[str,TelephoneSchemaDcatApOp]
        self.hasAddress_vcard = {}  # type: dict[str,AddressSchemaDcatApOp]
        self.homePage_foaf = {}  # type:  dict[str, DocumentSchemaDcatApOp]


class TelephoneSchemaDcatApOp(SchemaGeneric):
    rdf_type = NAMESPACE_DCATAPOP.vcard + "Voice"

    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(TelephoneSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(TelephoneSchemaDcatApOp.rdf_type, graph_name)

        self.hasValue_vcard = {}  # type: dict[str, SchemaGeneric]


class AddressSchemaDcatApOp(SchemaGeneric):
    rdf_type = NAMESPACE_DCATAPOP.vcard + "Address"

    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(AddressSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(AddressSchemaDcatApOp.rdf_type, graph_name)

        self.streetDASHaddress_vcard = {}  # type: dict[str,ResourceValue] Literal
        self.postalDASHcode_vcard = {}  # type: dict[str,ResourceValue] Literal
        self.locality_vcard = {}  # type: dict[str,ResourceValue] Literal
        self.countryDASHname_vcard = {}  # type: dict[str,ResourceValue] Literal
