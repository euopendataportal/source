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
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import MediaTypeOrExtentSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.lib import uri_util

class DocumentSchemaDcatApOp(SchemaGeneric):
    rdf_type = NAMESPACE_DCATAPOP.foaf + "Document"

    property_vocabulary_mapping = {
        'type_dcterms': 'http://publications.europa.eu/resource/authority/documentation-type',

        'format_dcterms': 'http://publications.europa.eu/resource/authority/file-type',
        'language_dcterms': 'http://publications.europa.eu/resource/authority/language'
    }

    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        if not '{0}/{1}'.format(uri_util.PREFIX,'document') in uri and uri != DocumentSchemaDcatApOp.rdf_type:
            uri = uri_util.new_documentation_uri()
        super(DocumentSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(DocumentSchemaDcatApOp.rdf_type, graph_name)

        self.format_dcterms = {}  # type: dict[str,MediaTypeOrExtentSchemaDcatApOp]
        self.title_dcterms = {}  # type: dict[str,ResourceValue] #Literal
        self.type_dcterms = {}  # type: dict[str,ResourceValue] #Literal #DocumentationType
        self.topic_foaf = {}  # type: dict[str,SchemaGeneric] TODO: To be verified
        self.url_schema = {}  # type: dict[str,ResourceValue] #anyURI
        self.description_dcterms = {}  # type: dict[str,ResourceValue]
        self.language_dcterms = {}  # type: dict[str,LinguisticSystemSchemaDcatApOp]

