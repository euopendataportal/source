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

import ckanext.ecportal.model.schemas as schema



class DcatModelFactory(object):

    def factory(self, type, uri=''):
        from ckanext.ecportal.model.schemas.dcatapop_dataset_schema import DatasetSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_agent_schema import AgentSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_category_schema import CorporateSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_category_schema import DataThemeSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_category_schema import DatasetTypeSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_data_extension_schema import DataExtensionSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_distribution_schema import DistributionSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import FrequencySchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LinguisticSystemSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LocationSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import ProvenanceStatementSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import StandardSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_group_schema import DatasetGroupSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_identifier_schema import IdentifierSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_kind_schema import KindSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_period_of_time_schema import PeriodOfTimeSchemaDcatApOp
        from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
        from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric

        if schema.DATASET_DCATAPOP == type:
            return DatasetSchemaDcatApOp(uri)

        elif schema.DISTRIBUTION_DCAT == type:
            return DistributionSchemaDcatApOp(uri)
        elif schema.DOCUMENT_FOAF == type:
            return DocumentSchemaDcatApOp(uri)
        else:
            return SchemaGeneric(uri)