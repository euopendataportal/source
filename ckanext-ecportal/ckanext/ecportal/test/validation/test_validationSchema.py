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

from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.model.schema_validation.schema_validation import ValidationSchema, ValidationTypeResult
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue, SchemaGeneric
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
from ckanext.ecportal.action.ecportal_validation import validate_doi

class TestValidationSchema(TestWithVirtuosoConfiguration):
    def test_get_validation_rules_from_file(self):

        pass

    def test_at_most_one_by_language(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            ds.schema.title_dcterms['1'] = ResourceValue("new title", "fr")
            ds.schema.title_dcterms['2'] = ResourceValue("new title2", "it")
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            # validation_result = True
            for result in report:
                if result.get("property") == "title_dcterms" and result.get("constraint") == "card_1..n_en":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
                    break
            self.assertTrue(validation_result, " Test validation of test_at_least_one_en failed")

            # test the case of empty value

            ds.schema.title_dcterms['0'].value_or_uri = ''
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "title_dcterms" and result.get("constraint") == "card_1..n_en":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
            self.assertTrue(not validation_result, " Test validation of test_at_least_one_en failed")

            ds.schema.title_dcterms['0'].value_or_uri = None
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "title_dcterms" and result.get("constraint") == "card_1..n_en":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
            self.assertTrue(not validation_result, " Test validation of test_at_least_one_en failed")

            # No english title
            ds.schema.title_dcterms['0'] = ResourceValue("new title", "de")
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "title_dcterms" and result.get("constraint") == "card_1..n_en":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
            self.assertTrue(not validation_result, " Test validation of test_at_least_one_en failed")

            # validator = ValidationSchema(ds.schema)
            # report = validator.validate()

            # self.fail()

    def test_must_have_one(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            # must have one ckan name,
            validation_error = False
            ds.schema.ckanName_dcatapop['1'] = ResourceValue("New CKAN")
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "ckanName_dcatapop" and result.get("constraint") == "card_1..1":
                    validation_resul = False if result.get("result") == ValidationTypeResult.error else True
            self.assertTrue(not validation_resul, " Test validation of must_have_one failed")

    def test_at_most_one(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            validation_error = False
            # ds.schema.theme_dcat['1'] = ResourceValue("New CKAN")
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "accessRights_dcterms" and result.get("constraint") == "card_0..1":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
                    break
            self.assertTrue(validation_result, " Test validation of must_have_one failed")

            # add another member
            ds.schema.accessRights_dcterms['1'] = SchemaGeneric("newthem")
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "accessRights_dcterms" and result.get("constraint") == "card_0..1":
                    validation_result = True if result.get("result") == ValidationTypeResult.error else False
                    break
            self.assertTrue (validation_result, " Test validation of must_have_one (more than 1) failed")
            pass

            ds.schema.accessRights_dcterms = None
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "accessRights_dcterms" and result.get("constraint") == "card_0..1":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
                    break
            self.assertTrue(validation_result, " Test validation of must_have_one (cardinality 0) failed")
            pass

            # self.fail()

    def test_unique_value_in_ts(self):
        pass
        # self.fail()

    def test_restricted_datatype(self):
        pass
        # self.fail()

    def test_date_later(self):
        pass
        # self.fail()

    def test_controlled_vocabularies_values(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            validation_result = True
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "theme_dcat" and result.get("constraint") == "controlled_vocabulary":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
                if not validation_result:
                    break
            self.assertTrue(validation_result, " Test validation of validation failed")

            ds.schema.accrualPeriodicity_dcterms['1'] = SchemaGeneric("http://doNoBelongToControledVocabulary")
            validation_result = True
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "accrualPeriodicity_dcterms" and result.get(
                        "constraint") == "controlled_vocabulary":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
                if not validation_result:
                    break
            self.assertTrue(not validation_result, " Test validation of validation failed")

            pass
    def test_controlled_vocabulary_publisher_from_db(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        validation_result = True
        if ds.get_description_from_ts():

            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if result.get("property") == "publisher_dcterms" and result.get("constraint") == "controlled_vocabulary":
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
                    break
        self.assertTrue(validation_result, " Test validation of validation failed")


    def test_validation(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2")
        if ds.get_description_from_ts():
            # must have one ckan name,
            validation_result = True
            # ds.schema.theme_dcat['1'] = ResourceValue("New CKAN")
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                validation_result = False if result.get("result") == ValidationTypeResult.error else True
                if not validation_result:
                    break
            self.assertTrue(validation_result, " Test validation of validation failed")
            pass

    def test_contain_url(self):
        ds = DatasetDcatApOp("http://data.europa.eu/88u/dataset/ba22f500-839a-4313-bfa2-2414bfb2b429")
        properties = ["source_dcterms", "provenance_dcterms", "conformsTo_dcterms", "sample_adms",
                      "isVersionOf_dcterms", "hasVersionOf_dcterms", "isPartOf_dcterms", "hasPart_dcterms",
                      "relation_dcterms", "applicationUsingDataset_dcatapop"]
        validation_result = True
        if ds.get_description_from_ts():
            validator = ValidationSchema(ds.schema, ds.schema.get_schema_type())
            report = validator.validate()
            for result in report:
                if ((result.get("property") in properties) and result.get("constraint") == "contain_url"):
                    validation_result = False if result.get("result") == ValidationTypeResult.error else True
                if not validation_result:
                    break
        self.assertTrue(validation_result, "Test validation of contain_url failed")
pass
