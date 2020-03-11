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
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.model.schemas.dcatapop_checksum_schema import ChecksumSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import MediaTypeOrExtentSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_data_extension_schema import DataExtensionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LinguisticSystemSchemaDcatApOp, \
    RightsStatementSchemaDcatApOp, StandardSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_license_document_schema import LicenseDocumentDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
from ckanext.ecportal.lib import uri_util

from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP


class DistributionSchemaDcatApOp(SchemaGeneric):
    rdf_type = NAMESPACE_DCATAPOP.dcat + "Distribution"

    property_vocabulary_mapping = {
            'type_dcterms': 'http://publications.europa.eu/resource/authority/distribution-type',
            'license_dcterms': 'http://publications.europa.eu/resource/authority/licence',
            'status_adms': 'http://publications.europa.eu/resource/authority/dataset-status',
            'format_dcterms': 'http://publications.europa.eu/resource/authority/file-type',
            'language_dcterms': 'http://publications.europa.eu/resource/authority/language'
        }

    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        if not '{0}/{1}'.format(uri_util.PREFIX, 'distribution') in uri and uri != DistributionSchemaDcatApOp.rdf_type:
            uri = uri_util.new_distribution_uri()
        super(DistributionSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(DistributionSchemaDcatApOp.rdf_type, graph_name)

        self.mediaType_dcat = {}  # type: dict[str,MediaTypeOrExtentSchemaDcatApOp]
        self.numberOfDownloads_dcatapop = {}  # type: dict[str,ResourceValue]
        self.modified_dcterms = {}  # type: dict[str,ResourceValue] #dateTime
        self.checksum_spdx = {}  # type: dict[str,ChecksumSchemaDcatApOp]
        self.description_dcterms = {}  # type: dict[str,ResourceValue] #Literal
        self.format_dcterms = {}  # type: dict[str,MediaTypeOrExtentSchemaDcatApOp]
        self.issued_dcterms = {}  # type: dict[str,ResourceValue] #dateTime
        self.title_dcterms = {}  # type: dict[str,ResourceValue] #Literal
        self.type_dcterms = {}  # type: dict[str,SchemaGeneric] #DistributionType
        self.extensionLiteral_dcatapop = {}  # type: dict[str,DataExtensionSchemaDcatApOp]
        self.extensionValue_dcatapop = {}  # type: dict[str,DataExtensionSchemaDcatApOp]
        self.iframe_dcatapop = {}  # type: dict[str,ResourceValue]
        self.language_dcterms = {}  # type: dict[str,LinguisticSystemSchemaDcatApOp]
        self.license_dcterms = {}  # type: dict[str,LicenseDocumentDcatApOp]
        self.page_foaf = {}  # type: dict[str,DocumentSchemaDcatApOp]
        self.rights_dcterms = {}  # type: dict[str,RightsStatementSchemaDcatApOp]
        self.status_adms = {}  # type: dict[str,SchemaGeneric] #DatasetStatus
        self.accessURL_dcat = {}  # type: dict[str,SchemaGeneric]
        self.downloadURL_dcat = {}  # type: dict[str,SchemaGeneric]
        self.byteSize_dcat = {}  # type: dict[str,ResourceValue]
        self.conformsTo_dcterms = {}  # type: dict[str,StandardSchemaDcatApOp]
