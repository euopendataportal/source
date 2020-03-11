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
from ckanext.ecportal.model.schemas import *
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.lib import uri_util

class CatalogRecordSchemaDcatApOp(SchemaGeneric):
    rdf_type = NAMESPACE_DCATAPOP.dcat + "CatalogRecord"

    property_vocabulary_mapping = {
            'language_dcterms': 'http://publications.europa.eu/resource/authority/language',
            'status_adms': 'http://purl.org/adms'
    }

    def __init__(self, uri=None, graph_name=DCATAPOP_PUBLIC_GRAPH_NAME):
        if not '{0}/{1}'.format(uri_util.PREFIX,'record') in uri and uri != CatalogRecordSchemaDcatApOp.rdf_type:
            uri = uri_util.new_catalog_record_uri()
        super(CatalogRecordSchemaDcatApOp, self).__init__(uri, graph_name)
        self.type_rdf['0'] = SchemaGeneric(CatalogRecordSchemaDcatApOp.rdf_type, graph_name)

        self.conformsTo_dcterms = {}  # type: dict[str,ResourceValue]
        self.primaryTopic_foaf = {}  # type: dict[str,DatasetSchemaDcatApOp]
        self.modified_dcterms = {}  # type: dict[str,ResourceValue] #datetime
        self.description_dcterms = {}  # type: dict[str,ResourceValue] #Literal
        self.issued_dcterms = {}  # type: dict[str,ResourceValue] #datetime
        self.title_dcterms = {}  # type: dict[str,ResourceValue] #Literal
        self.language_dcterms = {}  # type: dict[str, LinguisticSystemSchemaDcatApOp]
        self.numberOfViews_dcatapop = {}  # type: dict[str,ResourceValue]
        self.source_dcterms = {}  # type: dict[str,CatalogRecord]
        self.status_adms = {}  # type: dict[str,ResourceValue] #DatasetStatus
