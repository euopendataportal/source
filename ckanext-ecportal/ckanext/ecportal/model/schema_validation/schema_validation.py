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

import json
import logging
import time
import traceback
import re
import ckan.model as model
from dateutil.parser import parse

from ckanext.ecportal.multilingual.languages_constants import LanguagesConstants
from ckanext.ecportal.model.schema_validation.validation_type_result import ValidationTypeResult
from ckanext.ecportal.lib.uri_util import is_uri_valid
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

import ckanext.ecportal.lib.cache.redis_cache as redis_cache
log = logging.getLogger(__file__)
list_language = LanguagesConstants.get_languages_as_list()


class ValidationSchema(object):
    validation_structre_rules = None


    def __init__(self, schema_to_validate, key_validation_rules, validation_rules=None):
        """
        :param SchemaGeneric schema_to_validate:
        :param str key_validation_rules: the key of the dict of validation rules
        :param str|None validation_rules: the json of the validation rules
        """
        try:
            self.schema_to_validate = None
            if schema_to_validate and key_validation_rules:
                self.schema_to_validate = schema_to_validate # type: SchemaGeneric
                self.key_validation_rules = key_validation_rules
                self.schema_validation_rules = self._prepare_list_validation_rules(validation_rules)
                self.validation_report = []
            else:
                log.error("Validation. Instantiation failed of the ValidationSchema. [Schema: {0}]. [rules:{1}]".format(
                    schema_to_validate, key_validation_rules))
        except BaseException as e:
            log.error("Validation. Instantiation failed of the ValidationSchema for instance [{0}]".format(
                schema_to_validate))

    @staticmethod
    def extract_validation_rules_from_file(path_validation_rules=None):
        """

        :param str path_validation_rules:
        :rtype: str
        """
        try:
            path_json_validation_rules = path_validation_rules
            if not path_validation_rules:
                # TODO use a config file
                path_json_validation_rules = CKAN_PATH + "/ckanext-ecportal/ckanext/ecportal/model/schema_validation/validation_rules.json"
            f_obj = open(path_json_validation_rules, "r")
            content_file = f_obj.read()
            return content_file
        except BaseException as e:
            log.error("Validation. Cannot extract validation rules from file {0}".format(path_json_validation_rules))
            return None

    def _prepare_list_validation_rules(self, validation_rules=None):

        """
        To get only the validation rules related to the the type of the schema.
        :param str validation_rules:
        :return:
        """

        def get_structural_validation_rules():
            try:
                # put in config file
                path_validation_structure_rules = CKAN_PATH + "/ckanext-ecportal/ckanext/ecportal/model/schema_validation/validation_structure.json"
                f = open(path_validation_structure_rules)
                validation_structre_rules = json.load(f)
                return validation_structre_rules
            except BaseException as e:
                log.error("load structural validation rules failed")
                log.error(traceback.print_exc())
                return None

        try:
            if not validation_rules:
                validation_rules = self.extract_validation_rules_from_file()
            all_validation_rules = json.loads(validation_rules)
            schema_validation_rules = all_validation_rules.get(self.key_validation_rules, {})
            # optimize loading the structural rules
            if not ValidationSchema.validation_structre_rules:
                ValidationSchema.validation_structre_rules = get_structural_validation_rules()

            return schema_validation_rules
        except BaseException as e:
            log.error("Validation. Cannot prepare list of validation rules {0}".format(self.key_validation_rules))
            return None

    def _get_number_of_instances_in_member(self, property_member):
        """
        :param str property_member:
        :rtype: int|None
        """
        try:
            count = 0
            if self.schema_to_validate:
                list_of_values = getattr(self.schema_to_validate, property_member,
                                         None)  # type: dict[str,ResourceValue|SchemaGeneric]
                if list_of_values:
                    # check if the resource value has a value not empty not None
                    for resource_value_or_schema in list_of_values.values():
                        if getattr(resource_value_or_schema, "value_or_uri", None) not in ['', None]:
                            count = count + 1
                        elif getattr(resource_value_or_schema, "uri", None) not in ['', None]:
                            count = count + 1
                else:
                    count = 0
                return count
            else:
                log.error("Validation. Get number of instances failed. Schema is None, property: [{0}]".format(
                    property_member))
                return -1
        except BaseException as e:
            log.error("Validation. Get number of instances failed {0}".format(property_member))
            log.log(traceback.print_exc(e))
            return None

    def validate_the_structure(self):
        """
        Validate the schema against the formal structre to avoid the problem of using ResourceValue insteed of GenericSchema.
        Or to use the incorrect python class if we want to force validation to check the concret class of the qschema generic.
        for each property check if all instances are valid using the file validation_structure.json.


        :return:
        """
        try:
            from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric, ResourceValue, \
                inconvertable_parameters
            import ckanext.ecportal.model.schemas as sc

            validation_member_report = {}
            log.info('[Validation] [Structural validation] [START] [URI:<{0}>]'.format(self.schema_to_validate.uri))
            list_type_members = ValidationSchema.validation_structre_rules
            for member_name, list_generic_schema_or_rv in self.schema_to_validate.__dict__.iteritems():
                if list_generic_schema_or_rv and member_name not in inconvertable_parameters:
                    for key, schema_or_rv in list_generic_schema_or_rv.iteritems():

                        struture_validation_member_rule = list_type_members.get(member_name, {'type': '', 'class': ''})
                        type_of_object = struture_validation_member_rule.get('type', 'not_managed')
                        uri_class_of_object = struture_validation_member_rule.get('class', None)
                        class_of_the_object = sc.MAPPER_RDF_TYPE_CLASS.get(uri_class_of_object, SchemaGeneric)
                        is_member_valid = True
                        if type_of_object == 'literal' and not isinstance(schema_or_rv, ResourceValue):
                            is_member_valid = False
                        elif type_of_object == "uri":
                            if not isinstance(schema_or_rv, class_of_the_object):
                                is_member_valid = False
                        if not is_member_valid:
                            validation_member_report = {}
                            validation_member_report['class'] = self.key_validation_rules
                            validation_member_report['uri_resource'] = self.schema_to_validate.uri
                            validation_member_report['result'] = ValidationTypeResult.fatal
                            validation_member_report['property'] = member_name
                            validation_member_report['level_of_error'] = ValidationTypeResult.fatal
                            validation_member_report['name'] = "structure.validation.error"
                            validation_member_report['message'] = 'structure.validation.error'
                            self.validation_report.append(validation_member_report)
        except BaseException as e:
            log.error("Structural validation failed {0}".format(self.schema_to_validate.uri))
            log.error(traceback.print_exc())

    def validate(self):
        """
        the main method to validte the current Schema
        :rtype: []: the report of validation
        """
        try:
            start = time.time()
            validation_member_result = ""
            if not self.schema_to_validate or not self.key_validation_rules:
                log.warning("Validation. Schema will not be validated. [{0}] ".format(self.schema_to_validate.uri))
                return []
            total_cv_duration = 0

            self.validate_the_structure()

            for validation_rule in self.schema_validation_rules:  # type: dict [str,str]
                validation_member_report = dict(validation_rule)
                validation_member_report['class'] = self.key_validation_rules
                validation_member_report['uri_resource'] = self.schema_to_validate.uri
                # put the default value of the level of error
                validation_member_report['level_of_error'] = validation_member_report.get("level_of_error",
                                                                                          ValidationTypeResult.error)

                property_member = validation_rule['property']
                constraint = validation_rule['constraint']

                if constraint == "card_1..n":
                    validation_member_result = self.at_least_one(property_member)

                elif constraint == "card_1..n_en":  # must have at least one in english and max one in other languages
                    validation_member_result = self.at_most_one_by_language(property_member, en_mandatory=True)

                elif constraint == "card_0..n_lang":  # can contain at most only one value by language
                    validation_member_result = self.at_most_one_by_language(property_member, en_mandatory=False)

                elif constraint == "card_0..1":
                    validation_member_result = self.at_most_one(property_member)

                elif constraint == "card_1..1":
                    validation_member_result = self.must_have_one(property_member)

                elif constraint == "date_later":
                    property_member2 = validation_rule['property2']
                    validation_member_result = self.date_later(property_member, property_member2)
                elif constraint == "controlled_vocabulary":
                    start_cv = time.time()
                    source = validation_rule.get("source", "triplestore")
                    # Special case of publisher
                    if source == "db_publisher":
                        validation_member_result = self.controlled_vocabulary_publisher_from_db(property_member)
                    elif source == "db_group":
                        validation_member_result = self.controlled_vocabulary_group_from_db(property_member)
                    elif source == "triplestore":
                        validation_member_result = self.controled_vocabularies_values(property_member)
                    duration_cv = time.time() - start_cv
                    total_cv_duration = total_cv_duration + duration_cv
                    if duration_cv > 0.1:
                        log.warning(
                            "Validation rule heavy. {0}. Duration {1}".format(validation_member_report['property'],
                                                                              duration_cv))
                elif constraint == "restricted_type":
                    datatype = validation_rule["type"]
                    validation_member_result = self.restricted_datatype(property_member, datatype)
                elif constraint == "contain_url":
                    validation_member_result = self.contain_url(property_member)

                if validation_member_result:
                    # put the level as described in the rule
                    validation_member_report['result'] = validation_member_result

                else:
                    validation_member_report['result'] = ValidationTypeResult.error

                # do not add succes result
                if validation_member_report.get('result', "") != ValidationTypeResult.success:
                    self.validation_report.append(validation_member_report)

            log.info("Validation. Schema {0} and the instance {1} successful".format(
                self.schema_to_validate.type_rdf['0'].uri, self.schema_to_validate.uri))
            duration = time.time() - start
            log.info("Validation of resource: [{0}]. Duration = {1}".format(self.schema_to_validate.uri, duration))
            return self.validation_report

        except BaseException as e:
            log.error("Validation Failed. Schema {0}".format(self.schema_to_validate.uri))
            return None

    def at_least_one(self, property_member):
        try:
            count = self._get_number_of_instances_in_member(property_member)
            if count is not None:
                if count > 0:
                    return ValidationTypeResult.success
                else:
                    return ValidationTypeResult.error
            else:
                return ValidationTypeResult.error

        except BaseException as e:
            log.error("Validation failed[{0}]".format(property_member))
            return ValidationTypeResult.error

    # Each element must have a title (at least in EN)
    def at_most_one_by_language(self, property_member, en_mandatory=False):
        """
        :param str property_member: a memeber of the schema
        :rtype: ValidationTypeResult|None
        """

        try:
            # Initialization of the number of occurrence for each langauge
            dict_occurrence_languge = {}
            for language in list_language:
                dict_occurrence_languge[language] = 0

            list_of_values = getattr(self.schema_to_validate, property_member)  # type: dict[str,ResourceValue]
            # count for each language
            for value in list_of_values.values():
                lang = value.lang
                if value.lang == '':
                    lang = 'no_language'
                if getattr(value, 'value_or_uri', '') not in ['', None]:
                    dict_occurrence_languge[lang] += 1
            more_than_one_occurence = False
            for occurrence_language in dict_occurrence_languge.values():
                if occurrence_language > 1:
                    more_than_one_occurence = True
                    # return ValidationTypeResult.error

            if en_mandatory:
                if dict_occurrence_languge[LanguagesConstants.LANGUAGE_CODE_EN] == 1 and not more_than_one_occurence:
                    return ValidationTypeResult.success
                else:
                    return ValidationTypeResult.error
            else:
                if not more_than_one_occurence:
                    return ValidationTypeResult.success
                else:
                    return ValidationTypeResult.error

        except BaseException as e:
            log.error("Validation failed[{0}]".format(property_member))
            return ValidationTypeResult.error

    def must_have_one(self, property_member):
        """

        :param property_member: str
        :rtype: str
        """
        try:
            count = self._get_number_of_instances_in_member(property_member)
            if count is not None:
                if count == 1:
                    return ValidationTypeResult.success
                else:
                    return ValidationTypeResult.error
            else:
                return ValidationTypeResult.error

        except BaseException as e:
            log.error("Validation failed[{0}]".format(property_member))
            return ValidationTypeResult.error

    def at_most_one(self, property_member):
        """

        :param property_member: str
        :rtype: ValidationTypeResult|None
        """

        try:
            count = self._get_number_of_instances_in_member(property_member)
            if count is not None:
                if count <= 1:
                    return ValidationTypeResult.success
                else:
                    return ValidationTypeResult.error
            else:
                return ValidationTypeResult.error

        except BaseException as e:
            log.error("Validation failed[{0}]".format(property_member))
            return ValidationTypeResult.error

    def controled_vocabularies_values(self, property_member):
        """

        :param property_member:
        :rtype: ValidationTypeResult|None

        """
        try:
            from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
            from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil
            object_dict= getattr(self.schema_to_validate, property_member, {})
            factory = ControlledVocabularyFactory()
            graphs = self.schema_to_validate.property_vocabulary_mapping.get(property_member, '')
            if not isinstance(graphs, list):
                graphs = [graphs]

            all_uris = []
            for graph in graphs:
                mdr_util = factory.get_controlled_vocabulary_util(graph)
                #for uri in mdr_util.get_all_uris():
                #    all_uris[uri] = True
                all_uris = all_uris + mdr_util.get_all_uris()


            exists = True
            for obj in object_dict.values(): #type: SchemaGeneric
                if obj.uri not in all_uris:
                    exists = False
                    break
            if exists:
                return ValidationTypeResult.success
            else:

                log.warning(
                    "Validation. controled_vocabularies_values failed. Ressource [{0}] property [{1}]".format
                    (self.schema_to_validate.uri, property_member))
                return ValidationTypeResult.error
        except BaseException as e:
            log.error("Validation. controled_vocabularies_values failed {0}".format(property_member))
            log.debug(traceback.print_exc(e))
            return None

    def unique_value_in_ts(self, property_member):
        """

        :param property_member:
        :return:
        """
        try:

            pass
        except BaseException as e:
            return None

    def restricted_datatype(self, property_member, datatype):
        """
        validate the values of a member based on the its datatype.

        :param str property_member:
        :param str datatype:
        :return: ValidationTypeResult|None
        """
        try:
            # if the property' value is empty the result is a success
            count = self._get_number_of_instances_in_member(property_member)
            if count <= 0:
                return ValidationTypeResult.success
            else:
                values_of_members = getattr(self.schema_to_validate, property_member,
                                            None)  # type: dict[str,ResourceValue]
                if datatype in "xsdDate":
                    isCorrectType = True
                    for value_date in values_of_members.values():
                        try:
                            parsed_date = parse(value_date.value_or_uri)
                        except BaseException as e:
                            isCorrectType = False

                elif datatype in "uri":
                    # TODO use rfc3987 validator
                    isCorrectType = True
                    for value in values_of_members.values():
                        try:
                            if is_uri_valid(value.value_or_uri):
                                pass
                        except BaseException as e:
                            isCorrectType = False

                elif datatype in "xsdDecimal":
                    isCorrectType = True
                    for value in values_of_members.values():
                        try:
                            if not value.value_or_uri.isdigit():
                                isCorrectType = False
                                break
                        except BaseException as e:
                            isCorrectType = False

                if isCorrectType:
                    return ValidationTypeResult.success
                else:
                    return ValidationTypeResult.error

        except BaseException as e:
            log.error("Validation. Restricted datatype failed[{0}], Resource [{0}]".format(property_member,
                                                                                           self.schema_to_validate.uri))
            return ValidationTypeResult.error

    def date_later(self, member_start_date, member_end_date):
        """
        Check if member_start_date <  member_end_date
        :param property_member:
        :param member_start_date:
        :param member_end_date:
        :rtype: str
        """
        try:
            if self.schema_to_validate:
                value_member_start_date = getattr(self.schema_to_validate, member_start_date,
                                                  None)  # type: dict[str,ResourceValue]
                value_member_end_date = getattr(self.schema_to_validate, member_end_date,
                                                None)  # type: dict[str,ResourceValue]

                if value_member_start_date and value_member_end_date:
                    try:
                        dt_member_start_date = parse(value_member_start_date['0'].value_or_uri)
                        dt_member_end_date = parse(value_member_end_date['0'].value_or_uri)
                    except BaseException as e:
                        log.error("Validation. date_later, cannot parse dates {0} {1}".format(
                            value_member_start_date['0'].value_or_uri, value_member_end_date['0'].value_or_uri))
                    if dt_member_start_date <= dt_member_end_date:
                        return ValidationTypeResult.success
                    else:
                        return ValidationTypeResult.error
                else:
                    log.warning('Validation. date_later has one of the members None')
                    return ValidationTypeResult.success
            else:
                log.error("Validation failed [{0}] [{1}]".format(member_start_date, member_end_date))
                return ValidationTypeResult.error
        except BaseException as e:
            log.error("Validation. Date Later validation is failed {0} {1}".format(member_start_date, member_end_date))
            return None

    def controlled_vocabulary_publisher_from_db(self, property_member):
        """
        validate the specif case in which the controlled vocabulary is ion the db.
        :param str property_member:
        :return: ValidationTypeResult|None
        """

        def get_name_from_uri(uri):
            """
            get the local name of the uri based on the template */localname
            :param str uri:
            :return str:
            """
            try:
                name_from_uri = uri.rsplit("/", 1)[1].lower()
                return name_from_uri
            except BaseException as e:
                log.error("Validation. get_name_from uri failed. [uri: {0}]".format(uri))
                return None

        try:
            list_uris = getattr(self.schema_to_validate, property_member, None)  # type: dict[str, SchemaGeneric]
            validation_result = ValidationTypeResult.success
            if list_uris:
                for publisher in list_uris.values():
                    # :type publisher: SchemaGeneric
                    key = "controlled_vocabulary_publisher_from_db_" + publisher.uri
                    cached_validation_result = redis_cache.get_from_cache(key, pool=redis_cache.MISC_POOL)
                    if cached_validation_result is None:
                        name_from_uri = get_name_from_uri(publisher.uri)
                        organizations = model.Group.get(name_from_uri)
                        if organizations:
                            cached_validation_result = 'True'
                        else:
                            cached_validation_result = 'False'
                        redis_cache.set_value_in_cache(key, cached_validation_result, pool=redis_cache.MISC_POOL)
                    if cached_validation_result == 'False':
                        break
                validation_result = ValidationTypeResult.success if cached_validation_result == 'True' else ValidationTypeResult.error
            return validation_result
        except BaseException as e:
            log.error("Validation. controlled_vocabulary_publisher_from_db failed. [Property {0}]. [uri: {0}] ".format(
                property_member, self.schema_to_validate.uri))
            log.error(traceback.print_exc(e))
            return None

    def controlled_vocabulary_group_from_db(self, property_member):
        """
        validate the specif case in which the controlled vocabulary is ion the db.
        :param str property_member:
        :return: ValidationTypeResult|None
        """

        def get_name_from_uri(uri):
            """
            get the local name of the uri based on the template */localname
            :param str uri:
            :return str:
            """
            try:
                # name_from_uri = uri.rsplit("/", 1)[1].lower()
                # In this version one uses the group name as uri
                name_from_uri = uri.lower()

                return name_from_uri
            except BaseException as e:
                log.error("Validation. get_name_from uri failed. [uri: {0}]".format(uri))
                return None

        try:
            list_uris = getattr(self.schema_to_validate, property_member, None)  # type: dict[str, SchemaGeneric]
            validation_result = ValidationTypeResult.success
            if list_uris:
                for group in list_uris.values():
                    # :type group: SchemaGeneric
                    key = "controlled_vocabulary_group_from_db_" + group.uri
                    cached_validation_result = redis_cache.get_from_cache(key, pool=redis_cache.MISC_POOL)
                    if cached_validation_result is None:
                        name_from_uri = get_name_from_uri(group.uri)
                        group_in_db = model.Group.get(name_from_uri)
                        if group_in_db:
                            cached_validation_result = 'True'
                        else:
                            cached_validation_result = 'False'
                        redis_cache.set_value_in_cache(key, cached_validation_result, pool=redis_cache.MISC_POOL)
                    if cached_validation_result == 'False':
                        break
                validation_result = ValidationTypeResult.success if cached_validation_result == 'True' else ValidationTypeResult.error
            return validation_result
        except BaseException as e:
            log.error("Validation. controlled_vocabulary_group_from_db failed. [Property {0}]. [uri: {0}] ".format(
                property_member, self.schema_to_validate.uri))
            log.error(traceback.print_exc(e))
            return None

    def contain_url(self, property_member):
        """
        Check if each entry.uri in property_member match url pattern: (ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?
        :param property_member: contain entries which are supposed correspond to a url
        :rtype: ValidationTypeResult
        """
        try:
            if self.schema_to_validate:
                pattern = re.compile("(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?")
                value_url = getattr(self.schema_to_validate, property_member, None)  # type:dict[str, ResourceValue]
                if value_url:
                    for url in value_url.values():
                        if not pattern.match(url.uri):
                            return ValidationTypeResult.error
                    return ValidationTypeResult.success
                else:
                    return ValidationTypeResult.success  # No value (and card 0..n)
            else:
                log.error("Validation failed [{0}]".format(property_member))
                return ValidationTypeResult.error
        except BaseException as e:
            log.error("Validation. Contain_url failed. [Property {0}]. [uri: {0}] ".format(
                property_member, self.schema_to_validate.uri))
            return ValidationTypeResult.error
