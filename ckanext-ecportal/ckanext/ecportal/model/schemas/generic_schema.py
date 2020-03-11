# -*- coding: utf-8 -*-
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

from ckanext.ecportal.multilingual.languages_constants import LanguagesConstants
from rdflib import Graph

from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME
from ckanext.ecportal.model.schema_validation.schema_validation import ValidationSchema
from ckanext.ecportal.model.schemas.next_level_members import list_next_level_members
from ckanext.ecportal.model.utils_convertor import ConvertorFactory
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
import copy
import traceback

log = logging.getLogger(__file__)

_MDR_PROPERTY_BLACKLIST = [
    'publisher_dcterms', 'language_dcterms', 'license_dcterms', 'themeTaxonomy_dcterms', 'spatial_dcterms',
    'theme_dcterms', 'accessRights_dcterms', 'accrualPeriodicity_dcterms', 'identifier_dcterms', 'type_dcterms',
    'creator_dcterms', 'temporalGranularity_dcatapop'
]

inconvertable_parameters = ['uri', 'graph_rdflib', 'dict_prop_value', 'tripleStoreCRUDHelpers', 'graph_name',
                            'listPropertiesDeepExtraction', 'rdf_type', 'uriclass','property_vocabulary_mapping']
inconvertable_parameters_json_export = ['graph_rdflib', 'dict_prop_value', 'tripleStoreCRUDHelpers',
                                        'listPropertiesDeepExtraction', 'rdf_type','property_vocabulary_mapping']

SINGLE_VALUE_PROPERTIES = ['type_rdf', 'primaryTopic_foaf', 'modified_dcterms', 'conformsTo_dcterms', 'status_adms',
                          'issued_dcterms', 'source_dcterms', 'numberOfViews_dcatapop', 'publisher_dcterms',
                          'ckanName_dcatapop', 'accessRights_dcterms', 'accrualPeriodicity_dcterms',
                          'versionInfo_ow', 'creator_dcterms', 'isPartOf_dcterms', 'type_dcterms',
                          'format_dcterms', 'hasEmail_vcard', 'hasTelephone_vcard', 'hasAddress_vcard', 'numberOfDownloads_dcatapop',
                          'homePage_foaf', 'startDate_schema', 'endDate_schema', 'schemeAgency_adms',
                          'notation_skos', 'dataExtensionLiteral_dcatapop', 'dataExtensionValue_dcatapop',
                          'checksumValue_spdx', 'algorithm_spdx' ]

class SchemaGeneric(object):

    property_vocabulary_mapping = {}

    def __init__(self, resource_uri, graph_name=None, default_type=None):
        self.uri = resource_uri
        self.graph_name = graph_name or DCATAPOP_PUBLIC_GRAPH_NAME
        self.type_rdf = default_type or {}  # type: dict[str,SchemaGeneric]

    def get_description_from_ts(self):
        """
        get the description of the schema from the existing triples store
        :rtype: dict
        """
        try:
            description = self.__get_description_from_ts_current_level(graph_name=self.graph_name)
            if not description:
                return None
            self.__get_deep_level_schema()
            return description
        except BaseException as e:
            import traceback
            log.error(traceback.print_exc())
            log.error("Get description from TS failed for {0}".self.uri)
            log.error("Error. {0}".format(e.message))
            return None

    def get_resource_value_for_language(self, property_name, language):
        if not hasattr(self, property_name):
            log.warning('Object has no attribute {0}'.format(property_name))
            return ResourceValue('')

        for value in getattr(self, property_name).values():
            if value.lang == language or value.lang == None:
                return value
        return ResourceValue('')


    def __get_description_from_ts_current_level(self, graph_name=None):
        """
        Get the description of the schema from TS limited to the current level.

        :param graph_name:
        :return:
        """
        from ckanext.ecportal.model.schemas import MAPPER_RDF_TYPE_CLASS as MAPPER_RDF_TYPE_CLASS
        final_description_dict = dict()
        try:

            tripleStoreCRUDHelpers = TripleStoreCRUDHelpers()
            gn = graph_name
            if graph_name is None:
                gn = self.graph_name
            crud_uri = "<" + self.uri + ">"
            resource_description_from_TS = tripleStoreCRUDHelpers.get_all_properties_value(gn, crud_uri)
            dict_prop_values = dict()  # type: Dict[str,list]
            value_of_property = dict()  # type : dict[str,str]
            for desc in resource_description_from_TS:
                model_value = None
                prop = None
                value_type = None
                value_of_property = None
                value = None

                prop = desc['property']['value']
                value_of_property = desc['value']
                value_type = value_of_property['type']
                value = value_of_property['value']

                if value_type == 'uri':
                    schema = MAPPER_RDF_TYPE_CLASS.get(value, None)
                    if schema:
                        model_value = schema(uri=value, graph_name=self.graph_name)
                        model_value.type_rdf = {}

                    else:
                        model_value = SchemaGeneric(resource_uri=value, graph_name=self.graph_name)
                    key_special = "0"

                if value_type == 'literal':
                    datatype = 'string'
                    if value_of_property.has_key('xml:lang'):
                        lang = value_of_property['xml:lang']
                        key_special = "0"
                        model_value = ResourceValue(value, lang=lang)
                    else:
                        key_special = '0'
                        model_value = ResourceValue(value)
                if value_type == 'typed-literal':
                    datatype = value_of_property['datatype']
                    key_special = '0'
                    model_value = ResourceValue(value, type='typed-literal', datatype=datatype)

                dict_final_pv = dict()
                # add as member of the class
                member_name = NAMESPACE_DCATAPOP.get_member_name(prop)

                if final_description_dict.has_key(prop):
                    key = "{0}{1}".format("", final_description_dict[prop].__len__())
                    dict_final_pv[key] = model_value
                    final_description_dict[prop].update(dict_final_pv)
                    if member_name:
                        setattr(self, member_name, final_description_dict[prop])

                else:
                    dict_final_pv[key_special] = model_value
                    final_description_dict[prop] = dict_final_pv
                    if member_name:
                        setattr(self, member_name, dict_final_pv)
            return final_description_dict

        except BaseException as e:
            import traceback
            log.error(traceback.print_exc())
            log.error("Error. {0}".format(e.message))
            log.error("[Dataset]. get_description_from_ts_current_level failed {0}".format(self.uri))
            return None

    def __get_list_properties_for_next_level(self, schema):
        """
        Get the list of members of the schema to be used as next level for the data extraction.
        since e schema could has multiple rdf_type, on combine all properties
        :param SchemaGeneric schema:
        :rtype: list
        """
        try:
            properties_next_level = []
            for rdftype in schema.type_rdf.values():
                if list_next_level_members.has_key(rdftype.uri):
                    properties_next_level.extend(list_next_level_members[rdftype.uri])
            if properties_next_level.__len__() == 0:  # by default all members
                return []
            return properties_next_level
        except BaseException as e:
            log.error("[Get list properties next level] [Failed] [URI:<{0}>]".format(schema.uri))
            log.error(traceback.print_exc(e))
            return None

    def __get_deep_level_schema(self, list_properties=None, level=0, max_level=3, nbr=0):
        try:
            if level >= max_level:
                return None

            if not list_properties:
                list_properties = self.__get_list_properties_for_next_level(self)

            for prop in list_properties:
                try:
                    if prop not in inconvertable_parameters and self.__dict__.has_key(prop):
                        dict_prop_description = getattr(self, prop)

                        for key, schema in dict_prop_description.iteritems():
                            if isinstance(schema, SchemaGeneric):
                                schema.__get_description_from_ts_current_level()
                                level += 1
                                #  get the list of next level
                                list_members_next_level = self.__get_list_properties_for_next_level(schema)
                                schema.__get_deep_level_schema(list_members_next_level, level, nbr=nbr)
                                level -= 1

                                if schema.type_rdf:
                                    obj = copy.deepcopy(schema.type_rdf.get('0'))
                                    obj.__dict__.update(schema.__dict__)
                                    # obj.type_rdf = schema.type_rdf.get('0').type_rdf
                                    dict_prop_description[key] = obj
                            else:
                                pass
                    else:
                        pass
                except BaseException as noattr:
                    log.error("[Get Description from TS] [Failed] [URI:<{0}>]".format(self.uri))
                    log.error(traceback.print_exc())

            level = level + 1
            return True

        except BaseException as e:
            log.error("[GET Descrition from TS] [Failed]")
            log.error(traceback.print_exc(e))
            return None

    def save_to_ts(self, graph_name=None):
        """
            Insert or update the description of the current schema in the TS.
            all the existing description in TS will be removed.

        :param str graph_name:
        :rtype: bool|None
        """
        try:
            tripleStoreCRUDHelpers = TripleStoreCRUDHelpers()
            gn = graph_name
            if graph_name is None:
                gn = self.graph_name
            g = self.convert_to_graph_ml()
            ttl_schema = g.serialize(format='nt')
            tripleStoreCRUDHelpers.set_all_properties_values_as_ttl(gn, "<" + self.uri + ">", ttl_schema)
            return True
        except BaseException as e:
            log.error("Save schema to ts failed. [URI:<{0}>]".format(self.uri))
            log.error(traceback.print_exc(e))
            return None


    def convert_to_json_ld(self, graph_name=None):
        """
            Convert the graph to json-ld format

        :param str graph_name:
        :rtype: bool|None
        """
        try:
            tripleStoreCRUDHelpers = TripleStoreCRUDHelpers()
            gn = graph_name
            if graph_name is None:
                gn = self.graph_name
            g = self.convert_to_graph_ml()
            context = {"@vocab": "https://schema.org/Dataset"}
            ttl_schema = g.serialize(format='json-ld', context=context, indent=4)
            tripleStoreCRUDHelpers.set_all_properties_values_as_ttl(gn, "<" + self.uri + ">", ttl_schema)
            return True
        except BaseException as e:
            log.error("Save schema to ts failed. [uri {0}]".format(self.uri))
            return None

    def get_schema_type(self):
        """
        Identify the type of the schema in he case of Generic Schema
        :rtype str: the uri of the schema
        """
        try:

            uri = getattr(self.type_rdf.get('0', None), 'uri', None)
            return uri
        except BaseException as e:
            log.error("Get schema type failed. [uri: {0}]".format(self.uri))
            return None

    def convert_to_graph_ml(self, graph_rdflib=None, multi_level=True):
        """
        convert all the dataset object to rdflib graph with multi level option
        :param Graph graph_rdflib:
        :param bool multi_level:
        :rtype: Graph
        """
        try:
            g = graph_rdflib if graph_rdflib is not None else Graph()
            for member_name, list_generic_schema_or_rv in self.__dict__.iteritems():
                if list_generic_schema_or_rv and member_name not in inconvertable_parameters:
                    member_uri = NAMESPACE_DCATAPOP.generate_uri_from_member_name(member_name)
                    # desc = getattr(self, member_name)
                    for key, schema_or_rv in list_generic_schema_or_rv.iteritems():
                        if isinstance(schema_or_rv, ResourceValue):
                            rv = schema_or_rv  # just for the clarity of the code
                            st = ConvertorFactory.create_statement_with_literal(self.uri, member_uri, rv.value_or_uri,
                                                                                data_type=rv.datatype, lang=rv.lang)
                            if st:
                                g.add(st)
                            else:
                                log.error(
                                    "[convert_to_graph_ml]. Add literal to converted graph ({0}) ({1}) ({2})".
                                        format(self.uri, member_uri, rv.value_or_uri))
                        elif isinstance(schema_or_rv, SchemaGeneric):
                            schema = schema_or_rv
                            if self.uri not in "g":  # ['http://www.w3.org/ns/dcat#Dataset','http://www.w3.org/ns/dcat#CatalogRecord']:
                                try:
                                    st = ConvertorFactory.create_statement_with_uri(self.uri, member_uri, schema.uri)
                                except BaseException as e:
                                    st = None
                                if st:
                                    g.add(st)
                                else:
                                    log.error("[convert_to_graph_ml]. Add rersource to converted graph ({0}) ({1}) )".
                                              format(self.uri, member_uri))
                            if multi_level:
                                schema.convert_to_graph_ml(g)
            return g
        except BaseException as e:
            import traceback
            log.error(traceback.print_exc())
            log.error("Convert to graph failed for schema. [uri: {0}]".format(self.uri))
            return None

    def _validate_multi_level(self, final_report, multi_level=True, validation_rules=None):
        '''
        Validate the schema object and its sub schemas
        :param final_report:
        :param multi_level:
        :param validation_rules:
        :return:
        '''
        try:
            type_schema = self.get_schema_type()

            if type_schema:
                validator = ValidationSchema(self, type_schema, validation_rules=validation_rules)
                sv = validator.validate()
                if isinstance(sv, list):
                    final_report.extend(sv)
                if multi_level:
                    list_members_next_level = self.__get_list_properties_for_next_level(self)
                    for member_name, list_generic_schema_or_rv in self.__dict__.iteritems():
                        if list_generic_schema_or_rv and member_name not in inconvertable_parameters and member_name in list_members_next_level:
                            for key, schema_or_rv in list_generic_schema_or_rv.iteritems():
                                if isinstance(schema_or_rv, SchemaGeneric):
                                    schema = schema_or_rv  # type : SchemaGeneric
                                    schema._validate_multi_level(final_report, validation_rules=validation_rules)
                return final_report
        except BaseException as e:
            log.error("Validation of the schema failed. [uri: {0}]".format(self.uri))
            return None

    def validate_schema(self, validation_rules=None):
        try:
            return self._validate_multi_level([], validation_rules=validation_rules)
        except BaseException as e:
            log.error("Validation of the schema failed. [uri: {0}]  ".format(self.uri))
            return None

    def schema_dictaze(self):

        src_dict = self.__dict__
        result_dict = {}
        for key, value in src_dict.iteritems():
            if not value or key == 'graph_name':
                    continue
            if key in SINGLE_VALUE_PROPERTIES:
                result_dict[key] = self.__recursive_dictize(value, True)
            else:
                result_dict[key] = self.__recursive_dictize(value)

        return result_dict

    def __recursive_dictize(self, obj, single=False):
        '''
        :param ResourceValue|SchemaGeneric|list|unicode|dict obj:
        :return dict:
        '''
        if not obj:
            return {}

        if isinstance(obj, ResourceValue):
            return obj.__dict__

        if isinstance(obj, SchemaGeneric):
            # log.info('{0}, {1}'.format(obj.uri, obj.__class__.__name__))
            return self.__recursive_dictize(obj.__dict__, single)

        if isinstance(obj, list):
            return [self.__recursive_dictize(item) for item in obj]

        if isinstance(obj, unicode) or isinstance(obj, str):
            return obj

        result = {}
        list_result = []
        try:
            for key, value in obj.items():
                if not value or key == 'graph_name':
                    continue
                # log.info('{0}, {1}'.format(key,value.__class__.__name__))
                if key in SINGLE_VALUE_PROPERTIES:
                     result[key] = self.__recursive_dictize(value, True)

                elif self.__is_integer_key(key) and single:
                    debug = self.__recursive_dictize(value)
                    return debug
                elif self.__is_integer_key(key):
                    list_result.append(self.__recursive_dictize(value))
                else:
                    result[key] = self.__recursive_dictize(value)

            return list_result or result
        except BaseException as e:
            log.error("__recursive_dictize. Key: {0}. value: {1}".format(key, value))

    def __is_integer_key(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def array_get(array=[], index=0):
        try:
            return array[index]
        except:
            return None

    def export_to_json(self):
        """
        Export the schema to a json format to be used by the publisher.
        The aime is to provide a less complex structure with a minimum aspect of user friendly
        :param dict [str,list|str] json_dict:
        :return:
        """

        def adapt_structure(json_export, property_name, list_values):
            """
            Adapt the structure of the json export to be conform with the one of ui dict.

            :param json_export:
            :param property_name:
            :return:
            """

            def get_deep_value(obj=[], path_properties=[]):
                """
                Get the value of the last property in the path of properties.
                One considers that only the first objet of the array is used in each step.
                :param obj:
                :param path_properties:
                :return: str
                """
                try:
                    first_obj = obj[0]  # type: dict [str, list]
                    target_object = ""
                    for property in path_properties:
                        intermediate_obj = first_obj.get(property, [])  # type: list
                        first_obj = intermediate_obj[0]
                    value = first_obj
                    return value
                except BaseException as e:
                    return ""

            try:
                adapted_json_for_property = {}

                if property_name == "contactPoint_dcat":
                    cp = list_values[0]  # type: dict [str,list]
                    adapted_json_for_property["contactPoint_dcat__telephone"] = get_deep_value(list_values, ['hasTelephone_vcard', 'hasValue_vcard'])
                    adapted_json_for_property["contactPoint_dcat__name"] = get_deep_value(list_values, ['organisationDASHname_vcard'])
                    adapted_json_for_property["contactPoint_dcat__email"] = get_deep_value(list_values, ['hasEmail_vcard'])
                    adapted_json_for_property["contactPoint_dcat__address_street"] = get_deep_value(list_values, ['hasAddress_vcard', 'streetDASHaddress_vcard'])
                    adapted_json_for_property["contactPoint_dcat__address"] = adapted_json_for_property[
                        "contactPoint_dcat__address_street"]  # Todo check the best structure
                    adapted_json_for_property["contactPoint_dcat__address_postal"] = get_deep_value(list_values, ['hasAddress_vcard', 'postalDASHcode_vcard'])
                    adapted_json_for_property["contactPoint_dcat__address_locality"] = get_deep_value(list_values, ['hasAddress_vcard', 'locality_vcard'])
                    adapted_json_for_property["contactPoint_dcat__address_country"] = get_deep_value(list_values, ['hasAddress_vcard', 'countryDASHname_vcard'])
                    adapted_json_for_property["contactPoint_dcat__webpage"] = get_deep_value(list_values, ['homePage_foaf', 'url_schema'])

                elif property_name == "landingPage_dcat":
                    adapted_json_for_property["landingPage_dcat"] = get_deep_value(list_values, ["url_schema"])

                elif property_name == "homepage_foaf":
                    adapted_json_for_property["homepage_foaf"] = get_deep_value(list_values, ["url_schema"])


                elif property_name in "extensionValue_dcatapop":
                    adapted_json_for_property["extras"] = json_export.get('extras', [])
                    pass
                    for cp in list_values:
                        key_extra = get_deep_value([cp], ["title_dcterms"])
                        value_extra_extension_val = get_deep_value([cp], ["dataExtensionValue_dcatapop"])
                        adapted_json_for_property['extras'].append({'key': key_extra, 'value': value_extra_extension_val})
                        # adapted_json_for_property[]
                    pass
                elif property_name in "extensionLiteral_dcatapop":
                    adapted_json_for_property["extras"] = json_export.get('extras', [])
                    for cp in list_values:
                        key_extra = get_deep_value([cp], ["title_dcterms"])
                        value_extra_extension_literal = get_deep_value([cp], ["dataExtensionLiteral_dcatapop"])
                        adapted_json_for_property['extras'].append({'key': key_extra, 'value': value_extra_extension_literal})
                        # adapted_json_for_property[]
                elif property_name == "distribution_dcat":
                    # check if it is a visualization
                    adapted_json_for_property["resources_visualization"] = []
                    adapted_json_for_property["resources_distribution"] = []

                    for distribution in list_values:

                        type_visualization = "http://publications.europa.eu/resource/authority/distribution-type/VISUALIZATION"
                        key_type_distribution = "resources_distribution"
                        try:
                            if type_visualization == distribution['type_dcterms'][0]:
                                key_type_distribution = 'resources_visualization'
                        except BaseException as y:
                            key_type_distribution = "resources_distribution"
                        adapted_json_for_property[key_type_distribution].append(distribution)

                elif property_name == "provenance_dcterms":
                    provenance = get_deep_value(list_values, ['label_rdfs'])
                    adapted_json_for_property['provenance_dcterms'] = provenance

                elif property_name == "checksum_spdx":
                    checksumValue_spdx = get_deep_value(list_values, ['checksumValue_spdx'])
                    adapted_json_for_property['checksumValue_spdx'] = checksumValue_spdx


                elif property_name == "page_foaf":
                    adapted_json_for_property['resources_documentation'] = list_values

                elif property_name == "type_rdf":
                    json_export.pop("type_rdf", None)

                elif property_name == "temporal_dcterms":
                    temporal_from = get_deep_value(list_values, ['startDate_schema'])
                    temporal_to = get_deep_value(list_values, ['endDate_schema'])
                    adapted_json_for_property['temporal_coverage_from'] = temporal_from
                    adapted_json_for_property['temporal_coverage_to'] = temporal_to

                elif property_name == 'rights_dcterms':
                    rights = get_deep_value(list_values, ['label_rdfs'])
                    adapted_json_for_property["rights_dcterms"] = rights

                elif property_name == 'sample_adms':
                    # todo try to find better solution
                    samples = [val.get("uri", "") for val in list_values]
                    adapted_json_for_property["sample_adms"] = samples

                json_export.update(adapted_json_for_property)
                return json_export
            except BaseException as e:
                log.error("Export schema to json. Adaptation of the structure failed. property name {0}".
                          format(property_name))
                return json_export

        try:
            language_seperator = "-"
            special_members = ["contactPoint_dcat",
                               "landingPage_dcat",
                               "extensionValue_dcatapop",
                               "extensionLiteral_dcatapop",
                               "distribution_dcat",
                               "page_foaf",
                               "provenance_dcterms",
                               "checksum_spdx",
                               "type_rdf",
                               "temporal_dcterms",
                               "rights_dcterms",
                               "sample_adms",
                               'homepage_foaf'
                               ]
            # special_members = ["extensionValue_dcatapop"]

            json_export = {}
            for member_name, list_generic_schema_or_rv in self.__dict__.iteritems():
                member_name = unicode(member_name)
                # add the uri and the private status of the dataset and
                if self.get_schema_type() in ["http://www.w3.org/ns/dcat#Dataset", "http://www.w3.org/ns/dcat#Distribution","http://www.w3.org/ns/dcat#Catalog"]:
                    if member_name in ['uri', 'graph_name']:
                        json_export['uri'] = self.uri
                        json_export['graph_name'] = self.graph_name
                    elif member_name == "type_dcterms_SOS":
                        json_export["type_dcterms"] = [type_d.uri for type_d in self.type_dcterms.values()]

                if list_generic_schema_or_rv and (member_name not in inconvertable_parameters):
                    list_values = self.__export_property_to_json(member_name, list_generic_schema_or_rv)  # type: list[ResourceValue]
                    for property_value in list_values:
                        if isinstance(property_value, ResourceValue):
                            key_property_with_language = unicode(member_name)
                            if property_value.lang and property_value.lang != LanguagesConstants.LANGUAGE_CODE_EN:
                                key_property_with_language = member_name + language_seperator + property_value.lang
                            if key_property_with_language not in json_export:
                                json_export[key_property_with_language] = [property_value.value_or_uri]
                            else:
                                json_export[key_property_with_language].append(property_value.value_or_uri)
                        else:  # the property is a basically a schema or an uri
                            if member_name not in special_members:
                                if list_values == [{}]:  # todo a small workaround , try to fix it in the recursive function
                                    list_values = []
                                json_export[member_name] = list_values
                    if member_name in special_members:
                        json_export = adapt_structure(json_export, member_name, list_values)

            return json_export
        except BaseException as e:
            log.error("Export Schema to json failed. [uri: {0}]".format(self.uri))
            return None

    def __export_property_to_json(self, member_name, list_sg_rv):
        """
        :param sg_rv_or_list:
        :return:
        """
        try:
            property_values = []
            is_mdr = member_name in _MDR_PROPERTY_BLACKLIST;
            for key, schema_or_rv in list_sg_rv.iteritems():
                if isinstance(schema_or_rv, ResourceValue):
                    rv = schema_or_rv  # just for the clarity of the code
                    property_values.append(rv)
                elif isinstance(schema_or_rv, SchemaGeneric):
                    schema = schema_or_rv
                    if is_mdr:
                        property_values.append(schema.uri)
                    elif not schema.type_rdf:
                        property_values.append(schema.uri)
                    else:
                        property_values.append(schema.export_to_json())
            return property_values
        except BaseException as e:
            return None

    def build_DOI_dict_from_schema(self):
        '''
        Generate the dict that will be used by the DOI package
        :return dict:
        '''

        try:
            schema_dict = self.export_to_json()
            dataset_doi_dict = ConvertorFactory.schema_dict_to_DOI_dict(schema_dict)
            return dataset_doi_dict
        except BaseException as e:

            log.error("build the DOI dict failed for schema {0} ".format(self.uri))

    def build_DOI_dict_from_catalog_schema(self):
        '''
        Generate the dict that will be used by the DOI catalog
        :return dict:
        '''

        try:
            schema_dict = self.export_to_json()
            catalog_doi_dict = ConvertorFactory.schema_dict_to_DOI_dict(schema_dict, False)
            return catalog_doi_dict
        except BaseException as e:

            log.error("build the DOI dict failed for schema {0} ".format(self.uri))


class ResourceValue(object):
    """
        A generic class for literal and anyURI values.
        To be used if
            1) the value is literal
            2) the class is not yet implemented
            3) the class is simple (one need only the uri).

    """

    def __init__(self, value_or_uri, lang=None, type='literal', datatype=None):
        """
        :param str value_or_uri: the value of the literal
        :param str datatype: principaly, the xsd schema datatype
        :param str lang:
        :param str type: one of 'literal, typed-literal
        :return ResourceValue:
        """
        try:

            if value_or_uri is None:  # to avoid the case of None
                value_or_uri = ''
            self.value_or_uri = value_or_uri
            self.lang = lang
            self.type = type
            self.datatype = datatype

        except BaseException as e:
            log.error(
                "Creation of Resource value failed. [{0}] [{1}] [{2}] [{3}]".format(value_or_uri, lang, type, datatype))
            log.error(traceback.print_exc(e))
