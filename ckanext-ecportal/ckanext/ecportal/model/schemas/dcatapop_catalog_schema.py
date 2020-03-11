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
from ckanext.ecportal.model.schemas.dcatapop_agent_schema import AgentSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_dataset_schema import DatasetSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LinguisticSystemSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import RightsStatementSchemaDcatApOp, \
    LocationSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_license_document_schema import LicenseDocumentDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric


class CatalogSchemaDcatApOp(SchemaGeneric):

    rdf_type = NAMESPACE_DCATAPOP.dcat + "Catalog"

    property_vocabulary_mapping = {
        'license_dcterms': 'http://publications.europa.eu/resource/authority/licence',
        'publisher_dcterms': 'http://publications.europa.eu/resource/authority/corporate-body',
        'language_dcterms': 'http://publications.europa.eu/resource/authority/language',
        'spatial_dcterms': ['http://publications.europa.eu/resource/authority/country', 'http://publications.europa.eu/resource/authority/continent'],
        'themeTaxonomy_dcat': 'http://publications.europa.eu/resource/authority/data-theme' # not correct, needs to be adapted if list is available
    }

    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(CatalogSchemaDcatApOp, self).__init__(uri, graph_name)

        self.type_rdf['0'] = SchemaGeneric(CatalogSchemaDcatApOp.rdf_type, graph_name)

        self.hasPart_dcterms = {}  # type: dict[str,CatalogSchemaDcatApOp]
        self.isPartOf_dcterms = {}  # type: dict[str,CatalogSchemaDcatApOp]
        self.modified_dcterms = {}  # type: dict[str,ResourceValue] #datetime
        self.description_dcterms = {}  # type: dict[str,ResourceValue] #Literal
        self.issued_dcterms = {}  # type: dict[str,ResourceValue] #Literal
        self.language_dcterms = {}  # type: dict[str, LinguisticSystemSchemaDcatApOp]
        self.license_dcterms = {}  # type: dict[str, LicenseDocumentDcatApOp]
        self.publisher_dcterms = {}  # type: dict[str, AgentSchemaDcatApOp]
        self.rights_dcterms = {}  # type: dict[str, RightsStatementSchemaDcatApOp]
        self.spatial_dcterms = {}  # type: dict[str, LocationSchemaDcatApOp]
        self.record_dcat = {}  # type: dict[str,CatalogRecord]
        self.dataset_dcat = {}  # type: dict[str,DatasetSchemaDcatApOp]
        self.themeTaxonomy_dcat = {}  # type: dict[str,ResourceValue] #ConceptScheme

        self.title_dcterms = {}  # type: dict[str,ResourceValue] #ConceptScheme #Literal
        self.homepage_foaf = {}  # type: dict[str,DocumentSchemaDcatApOp]

        self.identifier_adms = {}  # type: dict[str, IdentifierSchemaDcatApOp]
