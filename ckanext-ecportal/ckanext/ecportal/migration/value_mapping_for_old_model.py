# -*- coding: utf-8 -*-
#    Copyright (C) <${YEAR}>  <Publications Office of the European Union>
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

from ckanext.ecportal.migration.datasets_migration_manager import ControlledVocabulary

controlled_vocabulary = ControlledVocabulary()

FILE_FORMAT_MAPPING = {
    "interactive": "http://publications.europa.eu/resource/authority/file-type/DCR",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "http://publications.europa.eu/resource/authority/file-type/XLSX",
    "image/jpeg": "http://publications.europa.eu/resource/authority/file-type/JPEG",
    "application/x-e00": "http://publications.europa.eu/resource/authority/file-type/E00",
    "text/comma-separated-values": "http://publications.europa.eu/resource/authority/file-type/CSV",
    "text/n3": "http://publications.europa.eu/resource/authority/file-type/RDF_N_TRIPLES",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "http://publications.europa.eu/resource/authority/file-type/PPTX",
    "application/ms-word": "http://publications.europa.eu/resource/authority/file-type/DOC",
    "application/vnd.ms-excel": "http://publications.europa.eu/resource/authority/file-type/XLS",
    "application/x-compress": "http://publications.europa.eu/resource/authority/file-type/TAR",
    "ZIP": "http://publications.europa.eu/resource/authority/file-type/ZIP",
    "application/x-mxd": "http://publications.europa.eu/resource/authority/file-type/MXD",
    "application/x-n3": "http://publications.europa.eu/resource/authority/file-type/RDF_TURTLE",
    "application/msaccess": "http://publications.europa.eu/resource/authority/file-type/MDB",
    "application/vnd.google-earth.kml+xml": "http://publications.europa.eu/resource/authority/file-type/KML",
    "text/plain": "http://publications.europa.eu/resource/authority/file-type/TXT",
    "application/x-gzip": "http://publications.europa.eu/resource/authority/file-type/ZIP",
    "webservice/sparql": "http://publications.europa.eu/resource/authority/file-type/SPARQLQ",
    "text/structured": "http://publications.europa.eu/resource/authority/file-type/TXT",
    "application/rss+xml": "http://publications.europa.eu/resource/authority/file-type/RSS",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "http://publications.europa.eu/resource/authority/file-type/DOCX",
    "application/x-dbase": "http://publications.europa.eu/resource/authority/file-type/DBF",
    "application/x-msaccess": "http://publications.europa.eu/resource/authority/file-type/MDB",
    "text/tab-separated-values": "http://publications.europa.eu/resource/authority/file-type/TSV",
    "application/sparql-query": "http://publications.europa.eu/resource/authority/file-type/SPARQLQ",
    "application/msword": "http://publications.europa.eu/resource/authority/file-type/DOC",
    "application/vnd.oasis.opendocument.spreadsheet": "http://publications.europa.eu/resource/authority/file-type/ODS",
    "application/javascript": "http://publications.europa.eu/resource/authority/file-type/JSON",
    "application/octet-stream": "http://publications.europa.eu/resource/authority/file-type/ODF",
    "application/rdf+xml": "http://publications.europa.eu/resource/authority/file-type/RDF_XML",
    "interactive": "http://publications.europa.eu/resource/authority/file-type/HTML"
}

EUROVOC_DOMAINS_MAPPING = {
    'http://eurovoc.europa.eu/100150': ['http://publications.europa.eu/resource/authority/data-theme/EDUC'],
    'http://eurovoc.europa.eu/100158': ['http://publications.europa.eu/resource/authority/data-theme/TECH'],
    'http://eurovoc.europa.eu/100149': ['http://publications.europa.eu/resource/authority/data-theme/EDUC',
                                        'http://publications.europa.eu/resource/authority/data-theme/SOCI',
                                        'http://publications.europa.eu/resource/authority/data-theme/HEAL'],
    'http://eurovoc.europa.eu/100151': ['http://publications.europa.eu/resource/authority/data-theme/TECH'],
    'http://eurovoc.europa.eu/100157': ['http://publications.europa.eu/resource/authority/data-theme/AGRI'],
    'http://eurovoc.europa.eu/100152': ['http://publications.europa.eu/resource/authority/data-theme/ECON'],
    'http://eurovoc.europa.eu/100161': ['http://publications.europa.eu/resource/authority/data-theme/REGI'],
    'http://eurovoc.europa.eu/100144': ['http://publications.europa.eu/resource/authority/data-theme/GOVE'],
    'http://eurovoc.europa.eu/100155': ['http://publications.europa.eu/resource/authority/data-theme/ENVI'],
    'http://eurovoc.europa.eu/100142': ['http://publications.europa.eu/resource/authority/data-theme/GOVE'],
    'http://eurovoc.europa.eu/100153': ['http://publications.europa.eu/resource/authority/data-theme/SOCI'],
    'http://eurovoc.europa.eu/100159': ['http://publications.europa.eu/resource/authority/data-theme/ENER'],
    'http://eurovoc.europa.eu/100154': ['http://publications.europa.eu/resource/authority/data-theme/TRAN'],
    'http://eurovoc.europa.eu/100162': ['http://publications.europa.eu/resource/authority/data-theme/INTR'],
    'http://eurovoc.europa.eu/100160': ['http://publications.europa.eu/resource/authority/data-theme/ECON'],
    'http://eurovoc.europa.eu/100145': ['http://publications.europa.eu/resource/authority/data-theme/JUST'],
    'http://eurovoc.europa.eu/100156': ['http://publications.europa.eu/resource/authority/data-theme/AGRI'],
    'http://eurovoc.europa.eu/100143': ['http://publications.europa.eu/resource/authority/data-theme/INTR'],
    'http://eurovoc.europa.eu/100148': ['http://publications.europa.eu/resource/authority/data-theme/ECON'],
    'http://eurovoc.europa.eu/100146': ['http://publications.europa.eu/resource/authority/data-theme/REGI',
                                        'http://publications.europa.eu/resource/authority/data-theme/ECON'],
    'http://eurovoc.europa.eu/100147': ['http://publications.europa.eu/resource/authority/data-theme/ECON'],
    'http://publications.europa.eu/resource/authority/data-theme/AGRI': [
        'http://publications.europa.eu/resource/authority/data-theme/AGRI'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/ECON': [
        'http://publications.europa.eu/resource/authority/data-theme/ECON'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/EDUC': [
        'http://publications.europa.eu/resource/authority/data-theme/EDUC'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/ENER': [
        'http://publications.europa.eu/resource/authority/data-theme/ENER'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/ENVI': [
        'http://publications.europa.eu/resource/authority/data-theme/ENVI'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/GOVE': [
        'http://publications.europa.eu/resource/authority/data-theme/GOVE'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/HEAL': [
        'http://publications.europa.eu/resource/authority/data-theme/HEAL'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/INTR': [
        'http://publications.europa.eu/resource/authority/data-theme/INTR'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/JUST': [
        'http://publications.europa.eu/resource/authority/data-theme/JUST'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/REGI': [
        'http://publications.europa.eu/resource/authority/data-theme/REGI'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/SOCI': [
        'http://publications.europa.eu/resource/authority/data-theme/SOCI'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/TECH': [
        'http://publications.europa.eu/resource/authority/data-theme/TECH'
    ],
    'http://publications.europa.eu/resource/authority/data-theme/TRAN': [
        'http://publications.europa.eu/resource/authority/data-theme/TRAN'
    ]

    }

DATASET_TYPE_MAPPING = {
    'http://data.europa.eu/euodp/kos/dataset-type/Ontology': 'http://publications.europa.eu/resource/authority/dataset-type/ONTOLOGY',
    'http://data.europa.eu/euodp/kos/dataset-type/Thesaurus': 'http://publications.europa.eu/resource/authority/dataset-type/THESAURUS',
    'http://data.europa.eu/euodp/kos/dataset-type/Mapping': 'http://publications.europa.eu/resource/authority/dataset-type/MAPPING',
    'http://data.europa.eu/euodp/kos/dataset-type/CoreComponent': 'http://publications.europa.eu/resource/authority/dataset-type/CORE_COMP',
    'http://data.europa.eu/euodp/kos/dataset-type/InformationExchangePackageDescription': 'http://publications.europa.eu/resource/authority/dataset-type/IEPD',
    'http://data.europa.eu/euodp/kos/dataset-type/CodeList': 'http://publications.europa.eu/resource/authority/dataset-type/CODE_LIST',
    'http://data.europa.eu/euodp/kos/dataset-type/NameAuthorityList': 'http://publications.europa.eu/resource/authority/dataset-type/NAL',
    'http://data.europa.eu/euodp/kos/dataset-type/ServiceDescription': 'http://publications.europa.eu/resource/authority/dataset-type/DSCRP_SERV',
    'http://data.europa.eu/euodp/kos/dataset-type/Schema': 'http://publications.europa.eu/resource/authority/dataset-type/SCHEMA',
    'http://data.europa.eu/euodp/kos/dataset-type/DomainModel': 'http://publications.europa.eu/resource/authority/dataset-type/DOMAIN_MODEL',
    'http://data.europa.eu/euodp/kos/dataset-type/Statistical': 'http://publications.europa.eu/resource/authority/dataset-type/STATISTICAL',
    'http://data.europa.eu/euodp/kos/dataset-type/SyntaxEncodingScheme': 'http://publications.europa.eu/resource/authority/dataset-type/SYNTAX_ECD_SCHEME',
    'http://data.europa.eu/euodp/kos/dataset-type/Taxonomy': 'http://publications.europa.eu/resource/authority/dataset-type/TAXONOMY'}

RESOURCE_TYPE = {
    'Feed': 'http://publications.europa.eu/resource/authority/distribution-type/FEED_INFO',
    'WebService': 'http://publications.europa.eu/resource/authority/distribution-type/WEB_SERVICE',
    'Download': 'http://publications.europa.eu/resource/authority/distribution-type/DOWNLOADABLE_FILE',
    'Visualization': 'http://publications.europa.eu/resource/authority/distribution-type/VISUALIZATION',
    'file.upload': 'http://publications.europa.eu/resource/authority/distribution-type/DOWNLOADABLE_FILE',
    'http://data.europa.eu/euodp/kos/documentation-type/MainDocumentation': 'http://publications.europa.eu/resource/authority/documentation-type/DOCUMENTATION_MAIN',
    'http://data.europa.eu/euodp/kos/documentation-type/RelatedDocumentation': 'http://publications.europa.eu/resource/authority/documentation-type/DOCUMENTATION_RELATED',
    'http://data.europa.eu/euodp/kos/documentation-type/RelatedWebPage': 'http://publications.europa.eu/resource/authority/documentation-type/WEBPAGE_RELATED'
}

STATUS_MAPPING = {
    "UNDERDEVELOPMENT": "http://publications.europa.eu/resource/authority/dataset-status/DEVELOP"

}

CONTROLLED_VOC = "controlled_vocabulary"
VALUES_MAPPING = "values_mapping"
DEFAULT_VALUE = "default_value"
DEFAULT_VALUE_DATATHEME = "http://publications.europa.eu/resource/authority/data-theme/GOVE"  # "http://eurovoc.europa.eu/100144"
DEFAULT_VALUE_FORMAT = "http://publications.europa.eu/resource/authority/file-type/OP_DATPRO"
DEFAULT_VALUE_DISTRIBUTION_TYPE = "http://publications.europa.eu/resource/authority/distribution-type/DOWNLOADABLE_FILE"  # "distributionDownload"
MAPPING = {
    "groups": {VALUES_MAPPING: EUROVOC_DOMAINS_MAPPING, DEFAULT_VALUE: DEFAULT_VALUE_DATATHEME},

    "format": {CONTROLLED_VOC: controlled_vocabulary.controlled_file_types_with_context,
               VALUES_MAPPING: FILE_FORMAT_MAPPING,
               DEFAULT_VALUE: DEFAULT_VALUE_FORMAT},

    "status": {CONTROLLED_VOC: controlled_vocabulary.controlled_status, VALUES_MAPPING: STATUS_MAPPING},
    "type_of_dataset": {VALUES_MAPPING: DATASET_TYPE_MAPPING},
    "accrual_periodicity": {CONTROLLED_VOC: controlled_vocabulary.controlled_frequencies},
    "resource_type": {VALUES_MAPPING: RESOURCE_TYPE, DEFAULT_VALUE: DEFAULT_VALUE_DISTRIBUTION_TYPE}

}
