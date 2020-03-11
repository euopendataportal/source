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

import logging

from ckanext.ecportal.model.schemas.dcatapop_catalog_record_schema import CatalogRecordSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_catalog_schema import CatalogSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_category_scheme_schema import CategorySchemeSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_checksum_schema import ChecksumSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_data_extension_schema import DataExtensionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_dataset_schema import DatasetSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_distribution_schema import DistributionSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_kind_schema import KindSchemaDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_license_document_schema import LicenseDocumentDcatApOp
from ckanext.ecportal.model.schemas.dcatapop_namespace import NAMESPACE_DCATAPOP
from ckanext.ecportal.model.schemas.dcatapop_period_of_time_schema import PeriodOfTimeSchemaDcatApOp
from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric

rdf_type_class_dict = {
    NAMESPACE_DCATAPOP.dcat + "CatalogRecord": CatalogRecordSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.dcat + "Catalog": CatalogSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.skos + "ConceptScheme": CategorySchemeSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.spdx + "Checksum": ChecksumSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.dcatapop + "DataExtension": DataExtensionSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.dcat + "Dataset": DatasetSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.dcat + "Distribution": DistributionSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.foaf + "Document": DocumentSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.vcard + "Kind": KindSchemaDcatApOp(''),
    NAMESPACE_DCATAPOP.dcterms + "LicenseDocument": LicenseDocumentDcatApOp(''),
    NAMESPACE_DCATAPOP.dcterms + "PeriodOfTime": PeriodOfTimeSchemaDcatApOp('')
}

log = logging.getLogger(__name__)


def instanciate_schema_generic(schema_generic):
    '''
    :param SchemaGeneric schema_generic:
    :return: The same object instanciated with the proper class
    '''
    try:
        if schema_generic and len(schema_generic.type_rdf.keys()) > 0:
            if rdf_type_class_dict.has_key(schema_generic.type_rdf['0'].uri):
                object_class = rdf_type_class_dict[schema_generic.type_rdf['0'].uri]
                object_class.__dict__ = schema_generic.__dict__
                return object_class
        return schema_generic
    except Exception as e:
        import traceback
        log.warning('{0}'.format(e))
        log.warning(traceback.print_exc())
        return schema_generic
