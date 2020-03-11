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

import datetime
import logging
import urllib
import pylons
import ckan.plugins as plugins
import ckan.model as model
import traceback
from rfc3987 import parse as uri_parse
from rdflib import URIRef, Literal, Graph, XSD
from rdflib.namespace import Namespace, NamespaceManager
from ckanext.ecportal.lib import uri_util
from ckanext.ecportal.multilingual.languages_constants import LanguagesConstants
log = logging.getLogger(__file__)

DEFAULT_LANGUAGE = pylons.config.get('ckan.locale_default', 'en')
SHA1 = 'SHA-1'

EUROVOC_DOMAINS_MAPPING = {'http://eurovoc.europa.eu/100150': ['http://publications.europa.eu/resource/authority/data-theme/EDUC'],
                           'http://eurovoc.europa.eu/100158': ['http://publications.europa.eu/resource/authority/data-theme/TECH'],
                           'http://eurovoc.europa.eu/100149': ['http://publications.europa.eu/resource/authority/data-theme/EDUC', 'http://publications.europa.eu/resource/authority/data-theme/SOCI',
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
                           'http://eurovoc.europa.eu/100146': ['http://publications.europa.eu/resource/authority/data-theme/REGI', 'http://publications.europa.eu/resource/authority/data-theme/ECON'],
                           'http://eurovoc.europa.eu/100147': ['http://publications.europa.eu/resource/authority/data-theme/ECON']}

DATASET_TYPE_MAPPING = {'http://data.europa.eu/euodp/kos/dataset-type/Ontology': 'http://publications.europa.eu/resource/authority/dataset-type/ONTOLOGY',
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


class ConvertorFactory:
    def __init__(self):
        pass

    @classmethod
    def create_statement_with_literal(self, uri_resource, uri_property, value, data_type=None, lang=None):
        try:
            # Do not accept to generate triple with None as value
            if value is not None:
                # priority to lang
                dt = None if lang else data_type
                literal_value = Literal(value, lang, dt, normalize=False)
                stm = (URIRef(uri_resource), URIRef(uri_property), literal_value)
                return stm
            else:
                return None
        except BaseException as e:
            log.error("create_statement_with_literal failed. [uri_resource:{0}], [property: {1}], value: [{2}]"
                      .format(uri_resource, uri_property, value))
            return None

    @classmethod
    def get_rdflib_datatype(self, wrapper_datatype):
        try:
            if not wrapper_datatype is None:
                if wrapper_datatype.__len__ > 0 and not "http://" in wrapper_datatype:
                    dt = XSD + wrapper_datatype
                    return dt
                elif wrapper_datatype.__len__ > 0:
                    return wrapper_datatype
            else:
                return XSD.string

        except BaseException as e:
            return None

    @classmethod
    def create_statement_with_uri(self, uri_resource, uri_property, uri_value):

        try:
            # clean the uri

            # uri_value = uri_value.encode('ascii','ignore').decode('utf8')
            # import urllib
            # uri_value = urllib.quote_plus(uri_value)
            if " " in uri_property:
                log.warn("uri_property {0} contains unauthorized characters".format(uri_property))
                uri_property = uri_property.replace(" ", "")
            if " " in uri_resource:
                log.warn("uri_resource {0} contains unauthorized characters".format(uri_resource))
                uri_resource = uri_resource.replace(" ", "")

            # check if the uri is correct, it should be if he validation is correctly done.
            # if the uri_value is not a validate uri create a new value ( work done for the migration)
            is_uri = False
            try:
                parsed_uri = uri_parse(uri_value)
                is_uri = True
            except BaseException as e:
                is_uri = False
            if not is_uri:
                safe_chars = "%/:?@+#,;()"
                uri_value = urllib.quote_plus(uri_value, safe_chars)

            if uri_resource and uri_property and uri_value:
                stm = (URIRef(uri_resource), URIRef(uri_property), URIRef(uri_value))
                return stm
            else:
                log.error("[create statement with uri] [failed] "
                          "[uri_resource:<{0}>] [uri_property:<{1}>] [uri_value:<{2}>]".
                          format(uri_resource,uri_property,uri_value))
                return None

        except BaseException as e:
            log.error("[create_statement_with_uri] [failed] [uri_resource:<{0}>] [uri_property:<{1}>] [uri_value:<{2}>]".
                      format(uri_resource, uri_property, uri_value))
            log.error(traceback.print_exc(e))
            return None

    def create_graph_from_dict(self, resource_uri, dict_property_value):
        try:
            g = Graph()
            for dpv in dict_property_value:
                stm = self.create_statement_with_literal(resource_uri, dict)

            pass
        except BaseException as e:
            pass

    @staticmethod
    def add_namespaces(ns_definition):
        g = Graph()
        for ns_def in ns_definition:
            new_NS = Namespace(ns_def[1])
            ns_manager = NamespaceManager(Graph())
            ns_manager.bind(ns_def[0], new_NS)
        return ns_manager
        pass

    @classmethod
    def create_multi_lang_full_text_field(self, graph):
        """
        A generic method to create the full text value of a graph based on literal nodes only. The result is a dict with for each key "lang" an aggregated string value
        of all literal with the language
        the case of literal without language is treated by using the NO_Languages key
        :param Graph graph:
        :rtype: dict[unicode,unicode]
        """
        try:
            if not graph:
                log.error("[Utils_convertor]. create_multi_lang_full_text_field failed. Graph None")
                return None
            NO_LANGUAGE = u'no_language'
            # put the list of URIs of properties that will not be treated
            black_list_properties = []  # empty means all properties
            list_allowed_types = [unicode, str, datetime.datetime, long,
                                  int]  # TODO check if unicode and  str are enough
            DELIMITER = " ---- "

            list_language = LanguagesConstants.get_languages_as_list()
            list_language.append(NO_LANGUAGE)

            # initialisation of content of the mega_field
            mega_text = dict()
            for language in list_language:
                mega_text[language] = u""

            for s, p, o in graph.triples((None, None, None)):
                if isinstance(o, Literal):
                    if not (p in black_list_properties):
                        val = o.toPython()
                        type_literal = type(val)
                        literal_value = unicode(val)
                        if type_literal in list_allowed_types:
                            literal_language = unicode(o.language) if o.language else NO_LANGUAGE
                            # a special case if a language is not already managed by the list of languages (should not happen)
                            if not mega_text.has_key(literal_language):
                                mega_text[literal_language] = ""
                            mega_text[literal_language] += literal_value + DELIMITER
                        else:
                            pass
                    else:
                        pass
                else:
                    pass

            log.info("[Utils_convertor]. create_multi_lang_full_text_field successful")
            return mega_text
        except BaseException as e:
            log.error(("[Utils_convertor]. create_multi_lang_full_text_field failed, Graph {0}".format(graph)))
            return None

    @classmethod
    def schema_dict_to_DOI_dict(self, schema_dict, is_dataset=True):
        '''
        Generate the dict that will be used by the DOI package
        :param dict schema_dict:
        :return dict:
        '''

        def _get_first_element(variable_name, dict_json=None, default=u''):
            '''
            get the first element of the  array or the string if it is not a list
            :param str variable_name:
            :param dict dict_json:
            :param str default:
            :return:
            '''

            try:
                if not dict_json:
                    dict_json = schema_dict
                list_val = dict_json.get(variable_name, [])
                if isinstance(list_val, list):
                    if len(list_val) > 0:
                        return unicode(list_val[0])
                    else:
                        return default
                else:
                    return unicode(list_val)
            except BaseException as e:
                return default

        def _get_label_from_mdr(uri, property_uri="<http://www.w3.org/2004/02/skos/core#prefLabel>"):
            '''
            Get the label of the URI
            :param str uri:
            :return:
            '''
            resource_uri = "<{0}>".format(uri)
            # property_uri = "http://www.w3.org/2004/02/skos/core#prefLabel"
            graph_names = [
                "http://eurovoc.europa.eu",
                "http://publications.europa.eu/resource/authority/data-theme",
                "http://publications.europa.eu/resource/authority/corporate-body"
            ]

            from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
            label = uri
            tsch = TripleStoreCRUDHelpers()
            try:
                label_structure = tsch.get_all_different_text_value_by_language_or_without(graph_names, resource_uri, property_uri, 'en')
                label = label_structure[0].get("value").get("value")
            except BaseException as e:
                log.error("get_label_from_mdr failed for {0}".format(uri))
                log.error(traceback.print_exc(e))
            return label

        def generate_list_values_with_language(property_name):

            '''
            :param str property_name:
            :return:
            '''
            list_properties_with_langage = []
            for property in schema_dict:  # type: str
                if property_name in property:
                    lang = property.split("-")[-1] if "-" in property else "en"  # the case of property without explicit language
                    list_properties_with_langage.append({"lang": lang, "text": _get_first_element(property)})
            return list_properties_with_langage

        def _get_right_label(right):
            """

            :param str right: the uri of the the right instance
            :return: the label
            """
            label = right
            # TODO get the label of the right
            return label

        try:
            #
            from dateutil.parser import parse
            from iso639_1_3converison import convertion_list_uri_languages_to_iso639_1
            # convert to DOI dict
            doi_dataset_dict = {}
            # doi_dataset_dict["identifier"] = _get_first_element("identifier_adms").get('notation_skos','')
            doi_dataset_dict["creator"] = _get_label_from_mdr(_get_first_element("publisher_dcterms"))
            doi_dataset_dict["title"] = generate_list_values_with_language("title_dcterms")
            doi_dataset_dict["publisher"] = _get_label_from_mdr("http://publications.europa.eu/resource/authority/corporate-body/PUBL")
            doi_dataset_dict["url"] = _get_first_element('uri')

            doi_dataset_dict["current_date"] = str(datetime.datetime.now().strftime("%Y%m%d"))

            date_issued = _get_first_element("issued_dcterms")
            if date_issued:
                doi_dataset_dict["publicationYear"] = str(parse(date_issued).year)
            else:
                # TODO check with client what publicationYear contains when date_issued is undefined
                doi_dataset_dict["publicationYear"] = str(parse(doi_dataset_dict["current_date"]).year)

            doi_dataset_dict["resourceType"] = "Dataset"
            if not is_dataset:
                doi_dataset_dict["resourceType"] = "Data catalog"

            # Recommended fields

            list_dcterm_subject = schema_dict.get("subject_dcterms", [])
            doi_dataset_dict["subject_subject"] = []
            for subject_dcterms in list_dcterm_subject:
                doi_dataset_dict["subject_subject"].append({"uri": subject_dcterms, "text": _get_label_from_mdr(subject_dcterms)})

            doi_dataset_dict["subject_theme"] = []
            for dcat_theme in schema_dict.get("theme_dcat", []):
                doi_dataset_dict["subject_theme"].append({"uri": dcat_theme, "text": _get_label_from_mdr(dcat_theme)})

            doi_dataset_dict["subject_keyword"] = schema_dict.get("keyword_dcat", [])

            doi_dataset_dict["date_issued"] = str(parse(date_issued).strftime("%Y/%m/%d"))
            modified_dcterms = _get_first_element("modified_dcterms", "")
            doi_dataset_dict["date_modified"] = str(parse(modified_dcterms).strftime("%Y/%m/%d"))

            relatedIdentifier_document = ""
            if is_dataset:
                relatedIdentifier_document = schema_dict.get("landingPage_dcat", "")  # TODO clarify the comment in the excel file
            else:
                relatedIdentifier_document = schema_dict.get("homepage_foaf", "")  # TODO clarify the comment in the excel file

            doi_dataset_dict["relatedIdentifier_document"] = relatedIdentifier_document
            if not isinstance(relatedIdentifier_document, list):
                doi_dataset_dict["relatedIdentifier_document"] = [relatedIdentifier_document]

            doi_dataset_dict["isPartOf"] = schema_dict.get("isPartOf_dcterms", [])
            doi_dataset_dict["hasPart"] = schema_dict.get("hasPart_dcterms", [])

            doi_dataset_dict["relatedIdentifier_source"] = schema_dict.get("source_dcterms", [])
            doi_dataset_dict["relatedIdentifier_hasVersion"] = schema_dict.get("hasVersion", [])
            doi_dataset_dict["relatedIdentifier_isVersionOf"] = schema_dict.get("isVersionOf", [])
            doi_dataset_dict["description"] = generate_list_values_with_language("description_dcterms")

            # Optional fields
            doi_dataset_dict["language"] = convertion_list_uri_languages_to_iso639_1(schema_dict.get("language_dcterms", []))  # TODO check the primary language
            doi_dataset_dict["alternateIdentifier"] = [{"alternateIdentifierType":"PURL", "value":schema_dict.get('uri',"")}]
            # convert to is639-1

            doi_dataset_dict["rights"] = []
            for right in schema_dict.get("rights_dcterms", []):
                doi_dataset_dict["rights"].append({"uri": right, "text": _get_right_label(right)})
            # TODO add version
            doi_dataset_dict["version"] = schema_dict.get("versionInfo_owl", [])

            return doi_dataset_dict
        except BaseException as e:
            traceback.print_exc(e)
            raise e


class Dataset_Convertor():
    def __init__(self):
        pass

    @classmethod
    def convert_eurovoc_domains_list(cls, eurovoc_domains_list):
        '''

        :param list eurovoc_domains_list:
        :return: set of themes
        '''

        result = set()
        for domain in eurovoc_domains_list:
            theme_list = EUROVOC_DOMAINS_MAPPING.get(domain)
            result = result.union(set(theme_list))

        return result

    @classmethod
    def convert_translations_of_parameters(self, dict, parameter, type='literal', datatype=None):
        from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
        result_dict = {}
        if dict and parameter:
            value_to_set = dict.get(parameter)
            if value_to_set:
                rv = ResourceValue(value_to_set, DEFAULT_LANGUAGE, type=type, datatype=datatype)
                result_dict['0'] = rv
            self.set_variables_for_languages(dict, parameter, result_dict, type)
        return result_dict

    @classmethod
    def set_variables_for_languages(cls, dict, parameter, result_dict, type):
        from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
        for idx, lang in enumerate(LanguagesConstants.get_languages_as_list()):
            param = parameter + '-' + lang
            if dict.get(param):
                rvl = ResourceValue(dict.get(param), lang, type=type)
                result_dict[str(len(result_dict))] = rvl

    @classmethod
    def convert_translations_of_splitted_parameters(self, dict, parameter, type='literal'):
        from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
        result_dict = {}
        if dict and parameter:
            variable = dict.get(parameter)
            if variable:
                variables = variable.split(" ")
                for variable in variables:
                    rv = ResourceValue(variable, DEFAULT_LANGUAGE, type=type)
                    length = str(len(result_dict))
                    result_dict[length] = rv
                self.set_splitted_variables_for_languages(dict, parameter, result_dict, type)
        return result_dict

    @classmethod
    def set_splitted_variables_for_languages(cls, dict, parameter, result_dict, type):
        from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
        for idx, lang in enumerate(LanguagesConstants.get_languages_as_list()):
            param = parameter + '-' + lang
            variable = dict.get(param)
            if variable:
                variables = variable.split(" ")
                for variable in variables:
                    rvl = ResourceValue(variable, lang, type=type)
                    length = str(len(result_dict))
                    result_dict[length] = rvl

    @classmethod
    def set_splitted_uris(cls, dict, parameter):
        from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric
        import ckanext.ecportal.lib.uri_util as uri_util
        result_dict = {}
        uris = dict.get(parameter)
        if uris:
            for uri in uris.split(" "):
                if uri:
                    if uri_util.is_uri_valid(uri):
                        url_length = str(len(result_dict))
                        result_dict[url_length] = SchemaGeneric(uri)
                    else:
                        url_length = str(len(result_dict))
                        result_dict[url_length] = SchemaGeneric(uri)
                        log.warn("Url [{0}] is not valid".format(uri))
        return result_dict

    @classmethod
    def set_splitted_labels(cls, dict, parameter):
        from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
        result_dict = {}
        labels = dict.get(parameter)
        if labels:
            for label in labels.split(" "):
                if label:
                    label_length = str(len(result_dict))
                    result_dict[label_length] = ResourceValue(label)
        return result_dict

    def convert_theme_dcat(self, data_dict, param, theme_dcat_dict):
        from ckanext.ecportal.lib.dataset_util import SchemaGeneric
        if param == 'theme':
            groups = data_dict.get(param, [])
            if groups:
                theme_dcat_dict = {}
            if not isinstance(groups, list):
                groups = [groups]
            for group in groups:
                if group:
                    length = str(len(theme_dcat_dict))
                    theme_dcat_dict[length] = SchemaGeneric(group)
        elif param == 'concepts_eurovoc':
            themes = data_dict.get(param, [])
            if not isinstance(themes, list):
                themes = [themes]
                for theme in themes:
                    if theme:
                        length = str(len(theme_dcat_dict))
                        theme_dcat_dict[length] = SchemaGeneric(theme)
        else:  # theme not yet in screens
            log.warning('Unknown theme for {0}'.format(param))

        return theme_dcat_dict

    def convert_contact_point(self, address, email, name, phone, webpage):
        from ckanext.ecportal.lib.dataset_util import ResourceValue
        from ckanext.ecportal.model.schemas.dcatapop_kind_schema import KindSchemaDcatApOp, \
            TelephoneSchemaDcatApOp, AddressSchemaDcatApOp, DocumentSchemaDcatApOp, SchemaGeneric

        return_dict = {}

        kind_schema = KindSchemaDcatApOp(uri_util.create_uri_for_schema(KindSchemaDcatApOp))
        # Address
        if address:
            address_schema = AddressSchemaDcatApOp(uri_util.create_uri_for_schema(AddressSchemaDcatApOp))
            address_schema.streetDASHaddress_vcard = {'0': ResourceValue(address)}
            kind_schema.hasAddress_vcard = {'0': address_schema}

        # Email
        if email:
            kind_schema.hasEmail_vcard = {'0': SchemaGeneric(email)}
            pass

        # name
        if name:
            length = str(len(kind_schema.organisationDASHname_vcard))
            kind_schema.organisationDASHname_vcard = {length: ResourceValue(name)}
            # names = name.split(" ")
            # for name in names:
            #     length = str(len(kind_schema.organisationDASHname_vcard))
            #     kind_schema.organisationDASHname_vcard = {length: ResourceValue(name)}

        # phone
        if phone:
            phone_schema = TelephoneSchemaDcatApOp(uri_util.create_uri_for_schema(TelephoneSchemaDcatApOp))
            phone_schema.hasValue_vcard = {'0': SchemaGeneric(phone)}
            kind_schema.hasTelephone_vcard = {'0': phone_schema}

        # Webpage
        if webpage:
            webpage_schema = DocumentSchemaDcatApOp(uri_util.create_uri_for_schema(DocumentSchemaDcatApOp))
            # TODO, must add default values otherwise the validation will be failed
            webpage_schema.topic_foaf['0'] = SchemaGeneric("default_topic_foaf")
            webpage_schema.title_dcterms['0'] = ResourceValue("title_default_values", lang='en')
            webpage_schema.type_dcterms['0'] = SchemaGeneric("default_type_dcterms")

            webpage_schema.url_schema = {'0': ResourceValue(webpage)}

            kind_schema.homePage_foaf = {'0': webpage_schema}

        if kind_schema:
            return {'0': kind_schema}
        else:
            return return_dict

    def convert_spatial(self, list_of_countries):
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LocationSchemaDcatApOp
        return_dict = {}
        if list_of_countries:
            if not isinstance(list_of_countries, list):
                list_of_countries = [list_of_countries]
            for idx, country in enumerate(list_of_countries):
                if country:
                    return_dict[str(idx)] = LocationSchemaDcatApOp(country)
        return return_dict

    def convert_groups(self, groups):
        from ckanext.ecportal.model.schemas.dcatapop_group_schema import DatasetGroupSchemaDcatApOp
        return_dict = {}
        group_list = self._get_groups_from_databse_by_id(groups)

        if group_list:
            for group in group_list:
                return_dict[str(len(return_dict))] = DatasetGroupSchemaDcatApOp(group['name'])

        return return_dict

    def build_dict_for_inputs(self, inputs, dict, object_to_set):
        import copy
        dict = {}
        if inputs:
            if not isinstance(inputs, list):
                inputs = [inputs]
            for input in inputs:
                if input:
                    current_object = object_to_set(input)
                    # setattr(current_object, "uri", input)
                    dict[str(len(dict))] = current_object
        return dict

    def convert_keywords(self, keyword_string):
        from ckanext.ecportal.lib.dataset_util import ResourceValue
        tags = keyword_string if isinstance(keyword_string, list) else [tag.strip() for tag in keyword_string.split(',') if tag.strip()]
        return_dict = {}
        if tags:
            i = 0
            for keyword in tags:
                return_dict[str(i)] = ResourceValue(keyword, DEFAULT_LANGUAGE)
                i += 1
        return return_dict

    def convert_language(self, languages):
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import LinguisticSystemSchemaDcatApOp
        return_dict = {}
        if languages:
            if not isinstance(languages, list):
                languages = [languages]
            for idx, country in enumerate(languages):
                if country:
                    return_dict[str(idx)] = LinguisticSystemSchemaDcatApOp(country)
        return return_dict

    def convert_temporal_coverage(self, date_from, date_to):
        from ckanext.ecportal.model.schemas.dcatapop_period_of_time_schema import PeriodOfTimeSchemaDcatApOp
        from ckanext.ecportal.lib.dataset_util import ResourceValue
        return_dict = {}
        period = PeriodOfTimeSchemaDcatApOp(uri=uri_util.create_uri_for_schema(PeriodOfTimeSchemaDcatApOp))
        if date_from:
            period.startDate_schema['0'] = ResourceValue(date_from, datatype=XSD.date)
        if date_to:
            period.endDate_schema['0'] = ResourceValue(date_to, datatype=XSD.date)

        if period.startDate_schema or period.endDate_schema:
            return_dict['0'] = period


        return return_dict

    def convert_dataset_type(self, datasets_type):
        from ckanext.ecportal.model.schemas.dcatapop_category_schema import DatasetTypeSchemaDcatApOp
        return_dict = {}
        if datasets_type and isinstance(datasets_type, list):
            for ds_type in datasets_type:
                return_dict[str(len(return_dict))] = DatasetTypeSchemaDcatApOp(ds_type)

        elif datasets_type:
            return_dict['0'] = DatasetTypeSchemaDcatApOp(datasets_type)
        return return_dict

    def convert_resources_distribution(self, resources, dcat_dataset):
        '''

        :param resources:
        :param DatasetSchemaDcatApOp dcat_dataset:
        :return:
        '''
        from ckanext.ecportal.lib.dataset_util import SchemaGeneric, ResourceValue
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import MediaTypeOrExtentSchemaDcatApOp, \
            RightsStatementSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_distribution_schema import DistributionSchemaDcatApOp
        from ckanext.ecportal.lib.controlled_vocabulary_util import Distribution_controlled_vocabulary as distributions
        from ckanext.ecportal.model.schemas.dcatapop_checksum_schema import ChecksumSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_license_document_schema import LicenseDocumentDcatApOp
        from ckanext.ecportal.helpers import is_dict_empty
        from ckanext.ecportal.model.schemas.dcatapop_data_extension_schema import DataExtensionSchemaDcatApOp
        import ckanext.ecportal.lib.uri_util as uri_util

        return_dict = {}
        i = 0
        for resource in resources:
            # if resource.get('resource_type') not in distributions().get_full_dict().values():
            #     continue
            res_id = resource.pop('id', None)
            titles = self.convert_translations_of_parameters(resource, 'title')
            resource.pop('title', None)  # todo remove all the multi lingual title and description
            descriptions = self.convert_translations_of_parameters(resource, 'description')
            resource.pop('description', None)
            access_url = self.set_splitted_uris(resource, "access_url")
            resource.pop('access_url', None)
            download_url = self.set_splitted_uris(resource, 'download_url')
            release_date = self.convert_translations_of_parameters(resource, 'release_date', datatype=XSD.date)
            resource.pop('release_date', None)
            last_modifieds = self.convert_translations_of_parameters(resource, 'modification_date', datatype=XSD.date)
            resource.pop('modification_date', None)
            iframes = self.convert_translations_of_parameters(resource, 'iframe_code')
            resource.pop('iframe_code', None)
            sizes = self.convert_translations_of_parameters(resource, 'byte_size', datatype=XSD.decimal)
            resource.pop('byte_size', None)
            format = resource.pop('format', None)
            languages = resource.pop('language', None)
            linked_schema = self.set_splitted_uris(resource, 'linked_schema')
            resource.pop('linked_schema', None)
            status = self.set_splitted_uris(resource, "status")
            resource.pop('status', None)
            checksum = resource.pop('checksum', None)
            rights = resource.pop('rights', None)
            nb_download = resource.pop('downloads', None)
            resource_type = resource.pop('resource_type', None)
            licence = resource.pop('licence', None)
            old_res = None
            if dcat_dataset and res_id:
                old_res = next((old_distribution for old_distribution in dcat_dataset.distribution_dcat.values() if res_id in old_distribution.uri), None)

                if old_res:
                    uri = old_res.uri
                    nb_download = old_res.numberOfDownloads_dcatapop.get('0', ResourceValue('')).value_or_uri
                else:
                    uri = uri_util.new_distribution_uri()

            else:
                uri = uri_util.new_distribution_uri()
            distrib = DistributionSchemaDcatApOp(uri)

            # After deleting all parameters, only Extension remains
            for key, value in resource.get('extras', {}).iteritems():
                data_extension_uri = uri_util.new_dataextension_uri()
                try:
                    val = int(value)
                    extension = DataExtensionSchemaDcatApOp(data_extension_uri)
                    extension.dataExtensionLiteral_dcatapop['0'] = ResourceValue(key)
                    extension.dataExtensionValue_dcatapop['0'] = ResourceValue(value, datatype=XSD.decimal)
                    extension.title_dcterms = titles
                    distrib.extensionValue_dcatapop[str(len(distrib.extensionValue_dcatapop))] = extension


                except TypeError:
                    extensionLiteral = DataExtensionSchemaDcatApOp(data_extension_uri)
                    extensionLiteral.dataExtensionLiteral_dcatapop['0'] = ResourceValue(key)
                    extensionLiteral.dataExtensionValue_dcatapop['0'] = ResourceValue(value)
                    extensionLiteral.title_dcterms = titles
                    distrib.extensionLiteral_dcatapop[str(len(distrib.extensionLiteral_dcatapop))] = extensionLiteral

            if not is_dict_empty(access_url):
                distrib.accessURL_dcat = access_url
            if not is_dict_empty(descriptions):
                distrib.description_dcterms = descriptions
            if not is_dict_empty(format):
                distrib.format_dcterms['0'] = MediaTypeOrExtentSchemaDcatApOp(format)
            if licence:
                distrib.license_dcterms['0'] = LicenseDocumentDcatApOp(licence)
            if not is_dict_empty(download_url):
                distrib.downloadURL_dcat = download_url
            if not is_dict_empty(linked_schema):
                distrib.conformsTo_dcterms = linked_schema
            if not is_dict_empty(sizes):
                distrib.byteSize_dcat = sizes
            if not is_dict_empty(last_modifieds):
                distrib.modified_dcterms = last_modifieds
            if not is_dict_empty(release_date):
                distrib.issued_dcterms = release_date
            if not is_dict_empty(status):
                distrib.status_adms = status
            if not is_dict_empty(titles):
                distrib.title_dcterms = titles
            if not is_dict_empty(iframes):
                distrib.iframe_dcatapop = iframes
            if rights:
                rs = RightsStatementSchemaDcatApOp(uri_util.new_rightstatement_uri())
                rs.label_rdfs['0'] = ResourceValue(rights)
                distrib.rights_dcterms['0'] = rs
            if nb_download:
                distrib.numberOfDownloads_dcatapop['0'] = ResourceValue(nb_download, datatype=XSD.decimal)
            else:
                distrib.numberOfDownloads_dcatapop['0'] = ResourceValue('0', datatype=XSD.decimal)

            if checksum:
                checksum_schema = ChecksumSchemaDcatApOp(uri_util.new_checksum_uri())
                checksum_schema.algorithm_spdx['0'] = SchemaGeneric(SHA1)
                checksum_schema.checksumValue_spdx['0'] = ResourceValue(checksum, datatype=XSD.hexBinary)
                distrib.checksum_spdx = {'0': checksum_schema}

            distrib.type_dcterms['0'] = SchemaGeneric(resource_type)
            # distrib.mediaType_dcat['0'] = mediaType

            # hex = hashlib.sha1()
            # hex.update(pickle.dumps(distrib))
            # checksum_schema = ChecksumSchemaDcatApOp(uri_util.new_checksum_uri())
            # checksum_schema.algorithm_spdx['0'] = SchemaGeneric(SHA1)
            # checksum_schema.checksumValue_spdx['0'] = ResourceValue(hex.hexdigest(), datatype=XSD.hexBinary)
            # distrib.checksum_spdx = {'0' : checksum_schema}

            distrib.language_dcterms = self.convert_language(languages)

            return_dict[str(i)] = distrib
            i += 1
            if old_res and download_url:
                if download_url != old_res.downloadURL_dcat.get('0', SchemaGeneric('')).uri:
                    for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
                        if item.name != 'qa':
                            item.notify(distrib)

            elif old_res and access_url:
                if access_url != old_res.accessURL_dcat['0'].uri:
                    for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
                        if item.name != 'qa':
                            item.notify(distrib)
            elif not old_res:
                for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
                    if item.name != 'qa':
                        item.notify(distrib)

        return return_dict

    def convert_resources_page(self, resources, dcat_dataset, dataset_uri=None):
        '''

        :param resources:
        :param DatasetSchemaDcatApOp dcat_dataset:
        :return:
        '''
        from ckanext.ecportal.model.schemas.dcatapop_empty_classes_schema import MediaTypeOrExtentSchemaDcatApOp
        from ckanext.ecportal.model.schemas.dcatapop_document_schema import DocumentSchemaDcatApOp
        from ckanext.ecportal.lib.dataset_util import SchemaGeneric
        import ckanext.ecportal.lib.uri_util as uri_util
        from ckanext.ecportal.lib.controlled_vocabulary_util import \
            Documentation_controlled_vocabulary as documentations
        return_dict = {}
        for resource in resources:
            old_res = None
            i = len(return_dict)
            if resource.get('resource_type') not in documentations().get_full_dict().values():
                continue

            res_id = resource.get('id', '')
            titles = self.convert_translations_of_parameters(resource, 'title')
            descriptions = self.convert_translations_of_parameters(resource, 'description')
            urls = self.convert_translations_of_parameters(resource, 'url')
            format = resource.get('format', None)

            if dcat_dataset:
                old_res = next((schema for schema in dcat_dataset.page_foaf.values() if res_id == schema.uri.split('/')[-1]), None)
                for schema in dcat_dataset.page_foaf.values(): #type: DocumentSchemaDcatApOp
                    url_match = next((old_url for old_url in schema.url_schema.values() if old_url.value_or_uri in [new_urls.value_or_uri for new_urls in urls.values()]), None)
                    if url_match:
                        old_res = schema
                        break
                if old_res:
                    uri = old_res.uri
                else:
                    uri = uri_util.new_documentation_uri()

            else:
                uri = uri_util.new_documentation_uri()

            topic = self.set_splitted_uris(resource, 'topic')
            languages = resource.get('language', None)

            document = DocumentSchemaDcatApOp(uri)
            document.description_dcterms = descriptions
            document.title_dcterms = titles
            if format:
                document.format_dcterms['0'] = MediaTypeOrExtentSchemaDcatApOp(format)
            document.url_schema = urls
            uri_dataset = dataset_uri
            if dcat_dataset:
                uri_dataset = dcat_dataset.uri
            document.topic_foaf[str(len(document.topic_foaf))] = SchemaGeneric(uri_dataset)
            document.type_dcterms['0'] = SchemaGeneric(resource.get('resource_type'))
            document.language_dcterms = self.convert_language(languages)

            return_dict[str(i)] = document

            if old_res and urls:
                if urls != old_res.url_schema['0'].value_or_uri:
                    for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
                        if item.name != 'qa':
                            item.notify(document)
            elif not old_res:
                for item in plugins.PluginImplementations(plugins.IResourceUrlChange):
                    if item.name != 'qa':
                        item.notify(document)

        return return_dict

    def convert_text_to_list(self, text):
        text.split(" ")

    def _get_groups_from_databse_by_id(self, id):

        if not isinstance(id, list):
            id = [id]
        q_group = model.Session.query(model.Group).filter(model.Group.id.in_(id))
        groups = q_group.all()

        list_group = []
        for object in groups:
            list_group.append({'name': object.name,
                               'id': object.id,
                               'title': object.title})

        return list_group
