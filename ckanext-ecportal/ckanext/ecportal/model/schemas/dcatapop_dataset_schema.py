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
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric


class DatasetSchemaDcatApOp(SchemaGeneric):

    rdf_type = NAMESPACE_DCATAPOP.dcat + "Dataset"

    property_vocabulary_mapping = {
            'temporalGranularity_dcatapop': 'http://publications.europa.eu/resource/authority/timeperiod',
            'language_dcterms': 'http://publications.europa.eu/resource/authority/language',
            'spatial_dcterms': ['http://publications.europa.eu/resource/authority/country', 'http://publications.europa.eu/resource/authority/continent'],
            'accrualPeriodicity_dcterms': 'http://publications.europa.eu/resource/authority/frequency',
            'type_dcterms': 'http://publications.europa.eu/resource/authority/dataset-type',
            'subject_dcterms': 'http://eurovoc.europa.eu',  # Sub parameter of theme_dcat
            'theme_dcat': 'http://publications.europa.eu/resource/authority/data-theme',  # Sub parameter of theme_dcat
            'publisher_dcterms': 'http://publications.europa.eu/resource/authority/corporate-body',
            'creator_dcterms': 'http://publications.europa.eu/resource/authority/corporate-body',
            'identifier_adms': 'http://publications.europa.eu/resource/authority/notation-type',
            'accessRights_dcterms': 'http://publications.europa.eu/resource/authority/access-right',
    }

    def __init__(self, uri, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        super(DatasetSchemaDcatApOp, self).__init__(uri, graph_name)

        self.type_rdf['0'] = SchemaGeneric(DatasetSchemaDcatApOp.rdf_type, graph_name)

        self.description_dcterms = {}  # type: dict[str,ResourceValue]
        self.title_dcterms = {}  # type: dict[str, ResourceValue]
        self.distribution_dcat = {}  # type: dict[str, DistributionSchemaDcatApOp]
        self.contactPoint_dcat = {}  # type: dict[str, KindSchemaDcatApOp]
        self.keyword_dcat = {}  # type: dict[str, ResourceValue]
        self.publisher_dcterms = {}  # type: dict[str, AgentSchemaDcatApOp]
        self.theme_dcat = {}  # type: dict[str, DataThemeSchemaDcatApOp]
        self.accessRights_dcterms = {}  # type: dict[str, RightsStatementSchemaDcatApOp] RightsStatement three possible values
        self.conformsTo_dcterms = {}  # type: dict[str, StandardSchemaDcatApOp]
        self.page_foaf = {}  # type: dict[str, DocumentSchemaDcatApOp]
        self.accrualPeriodicity_dcterms = {}  # type: dict[str, FrequencySchemaDcatApOp]
        self.hasVersion_dcterms = {}  # type: dict[str, SchemaGeneric] # TODO think about use Dataset
        self.identifier_dcterms = {}  # type: dict[str, ResourceValue] # be carefull with the identifier of adms
        self.isVersionOf_dcterms = {}  # type: dict[str, DatasetSchemaDcatApOp] # TODO think about use Dataset
        self.landingPage_dcat = {}  # type: dict[str, DocumentSchemaDcatApOp]
        self.language_dcterms = {}  # type: dict[str, LinguisticSystemSchemaDcatApOp]
        self.identifier_adms = {}  # type: dict[str, IdentifierSchemaDcatApOp]
        self.provenance_dcterms = {}  # type: dict[str, ProvenanceStatementSchemaDcatApOp]
        self.relation_dcterms = {}  # type: dict[str, SchemaGeneric]
        self.issued_dcterms = {}  # type: dict[str, ResourceValue] it is a date card: 0..1
        self.sample_adms = {}  # type: dict[str, SchemaGeneric]
        self.source_dcterms = {}  # type: dict[str, DatasetSchemaDcatApOp]
        self.spatial_dcterms = {}  # type: dict[str, LocationSchemaDcatApOp]
        self.temporal_dcterms = {}  # type: dict[str, PeriodOfTimeSchemaDcatApOp]
        self.type_dcterms = {}  # type: dict[str, DatasetTypeSchemaDcatApOp] # card(0..1) TODO check the other class skos:concept
        self.modified_dcterms = {}  # type: dict[str, ResourceValue]  # Date card (0..1)
        self.versionInfo_owl = {}  # type: dict[str, ResourceValue] # Literal card (0..1)
        self.versionNotes_adms = {}  # type: dict[str, ResourceValue] # literal
        self.subject_dcterms = {}  # type: dict[str, SchemaGeneric]
        self.hasPart_dcterms = {}  # type: dict[str, DatasetSchemaDcatApOp]
        self.isPartOf_dcterms = {}  # type: dict[str, DatasetSchemaDcatApOp]
        self.contributor_dcterms = {}  # type: dict[str, CorporateSchemaDcatApOp] #removed from excel but it remains as
        self.creator_dcterms = {}  # type:dict[str, AgentSchemaDcatApOp]
        self.extensionValue_dcatapop = {}  # type: dict[str, DataExtensionSchemaDcatApOp]
        self.extensionLiteral_dcatapop = {}  # type: dict[str, DataExtensionSchemaDcatApOp]
        self.alternative_dcterms = {}  # type:dict[str, ResourceValue]
        self.topic_foaf = {}  # type: dict[str, DocumentSchemaDcatApOp]
        self.isPartOfCatalog_dcatapop = {}  # type:dict[str, CatalogSchemaDcatApOp] # card(0..1)
        self.applicationUsingDataset_dcatapop = {}  # type: dict[str, SchemaGeneric]
        self.temporalGranularity_dcatapop = {}  # type: dict[str, TemporalGranularitySchemaDcatApOp] # range can be skod:Concept, card(0..1)
        self.ckanName_dcatapop = {}  # type: dict [str, ResourceValue]
        self.datasetGroup_dcatapop = {}  # type: dict [str, DatasetGroupSchemaDcatApOp]
        self.attribute_stat = {}  # type: dict[str, SchemaGeneric]
        self.dimension_stat = {}  # type: dict[str, SchemaGeneric]
        self.numSeries_stat = {}  # type: dict[str, ResourceValue]
        self.hasQualityAnnotation_dqv = {}  # type: dict[str, SchemaGeneric]
        self.statMeasure_stat = {}  # type: dict[str, SchemaGeneric]
