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

from ckanext.ecportal.model.schemas.dcatapop_namespace import NAMESPACE_DCATAPOP
from ckanext.ecportal.model.schemas.dcatapop_catalog_record_schema import CatalogRecordSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_agent_schema import AgentSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_identifier_schema import IdentifierSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_catalog_schema import CatalogSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_category_schema import CategorySchemaDcatApOp, \
    DatasetTypeSchemaDcatApOp, DataThemeSchemaDcatApOp, CorporateSchemaDcatApOp, \
    TemporalGranularitySchemaDcatApOp, PublisherTypeSchemaDcatApOp, StatusSchemaDcatApOp, \
    LicenseTypeSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_category_scheme_schema import CategorySchemeSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_checksum_schema import ChecksumSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_data_extension_schema import DataExtensionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_dataset_schema import DatasetSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_distribution_schema import DistributionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_license_document_schema import LicenseDocumentDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LinguisticSystemSchemaDcatApOp, \
    RightsStatementSchemaDcatApOp, LiteralSchemaDcatApOp, LocationSchemaDcatApOp, \
    MediaTypeOrExtentSchemaDcatApOp, StandardSchemaDcatApOp, FrequencySchemaDcatApOp, \
    ProvenanceStatementSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_group_schema import DatasetGroupSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_kind_schema import KindSchemaDcatApOp, TelephoneSchemaDcatApOp, \
    AddressSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_period_of_time_schema import PeriodOfTimeSchemaDcatApOp

DATASET_DCATAPOP = NAMESPACE_DCATAPOP.dcat + "Dataset"


AGENT_FOAF = NAMESPACE_DCATAPOP.foaf + "Agent"
CATALOGRECORD_DCAT = NAMESPACE_DCATAPOP.dcat + "CatalogRecord"
CATALOG_DCAT = NAMESPACE_DCATAPOP.dcat + 'Catalog'
IDENTIFIER_ADMS = NAMESPACE_DCATAPOP.adms + 'Identifier'
DATASETGROUP_DCATAPOP = NAMESPACE_DCATAPOP.dcatapop + 'DatasetGroup'
LANGUAGE_DCTERMS = NAMESPACE_DCATAPOP.dcterms +'LinguisticSystem'
DISTRIBUTIONTYPE_DCATAPOP = NAMESPACE_DCATAPOP.dcatapop + 'DistributionType'
DOCUMENTATIONTYPE_DCATAPOP = NAMESPACE_DCATAPOP.dcatapop + 'DocumentationType'
DISTRIBUTION_DCAT = NAMESPACE_DCATAPOP.dcat + "Distribution"
DOCUMENT_FOAF = NAMESPACE_DCATAPOP.foaf + "Document"

DOCUMENT_DCATAPOP = NAMESPACE_DCATAPOP.foaf + "Document"
CATEGORY_SKOS = NAMESPACE_DCATAPOP.skos + "Concept"
CATEGORYSCHEME_SKOS = NAMESPACE_DCATAPOP.skos + "ConceptScheme"
CHECKSUM_SPDX = NAMESPACE_DCATAPOP.spdx + "Checksum"
DATAEXTENSION_DCATAPOP = NAMESPACE_DCATAPOP.dcatapop + "DataExtension"
DATASET_DCATAPOP = NAMESPACE_DCATAPOP.dcat + "Dataset"
DISTRIBUTION_DCATAPOP = NAMESPACE_DCATAPOP.dcat + "Distribution"
DOCUMENT_FOAF = NAMESPACE_DCATAPOP.foaf + "Document"
LINGUISTIC_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "LinguisticSystem"
RIGHTSTATEMENT_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "RightsStatement"
LITERAL_RDFS = NAMESPACE_DCATAPOP.rdfs + "Literal"
LOCATION_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "Location"
MEDIATYPEOREXTENT_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "MediaTypeOrExtent"
STANDARD_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "Standard"
FREQUENCY_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "Frequency"
PROVENANCE_SPDX = NAMESPACE_DCATAPOP.spdx + "ProvenanceStatement"
KIND_VCARD = NAMESPACE_DCATAPOP.vcard + "Kind"
TELEPHONE_VCARD = NAMESPACE_DCATAPOP.vcard + "Voice"
ADDRESS_VCARD = NAMESPACE_DCATAPOP.vcard + "Address"
LICENSE_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "LicenseDocument"
PERIODOFTIME_DCTERMS = NAMESPACE_DCATAPOP.dcterms + "PeriodOfTime"



MAPPER_RDF_TYPE_CLASS = {
    AGENT_FOAF: AgentSchemaDcatApOp,
    CATALOGRECORD_DCAT: CatalogRecordSchemaDcatApOp,
    CATALOG_DCAT: CatalogSchemaDcatApOp,
    CATEGORY_SKOS: CategorySchemaDcatApOp,
    CATEGORYSCHEME_SKOS: CategorySchemeSchemaDcatApOp,
    CHECKSUM_SPDX: ChecksumSchemaDcatApOp,
    DATAEXTENSION_DCATAPOP: DataExtensionSchemaDcatApOp,
    DATASET_DCATAPOP: DatasetSchemaDcatApOp,
    DISTRIBUTION_DCATAPOP: DistributionSchemaDcatApOp,
    DOCUMENT_FOAF: DocumentSchemaDcatApOp,
    LINGUISTIC_DCTERMS: LinguisticSystemSchemaDcatApOp,
    RIGHTSTATEMENT_DCTERMS: RightsStatementSchemaDcatApOp,
    LITERAL_RDFS: LiteralSchemaDcatApOp,
    LOCATION_DCTERMS: LocationSchemaDcatApOp,
    MEDIATYPEOREXTENT_DCTERMS: MediaTypeOrExtentSchemaDcatApOp,
    STANDARD_DCTERMS: StandardSchemaDcatApOp,
    FREQUENCY_DCTERMS: FrequencySchemaDcatApOp,
    PROVENANCE_SPDX: ProvenanceStatementSchemaDcatApOp,
    DATASETGROUP_DCATAPOP: DatasetGroupSchemaDcatApOp,
    IDENTIFIER_ADMS: IdentifierSchemaDcatApOp,
    KIND_VCARD: KindSchemaDcatApOp,
    TELEPHONE_VCARD: TelephoneSchemaDcatApOp,
    ADDRESS_VCARD: AddressSchemaDcatApOp,
    LICENSE_DCTERMS: LicenseDocumentDcatApOp,
    PERIODOFTIME_DCTERMS: PeriodOfTimeSchemaDcatApOp


}
