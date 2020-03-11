# -*- coding: utf-8 -*-
# Copyright (C) 2019  Publications Office of the European Union

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>
import cPickle as pickle
import hashlib

from pylons import config
from ckanext.ecportal.model.controlled_vocabulary_wrapper import ConceptSchemaSkosWrapper, ConceptSchemeSchemaSkosWrapper, CorporateBodyWrapper, CORPORATE_BODY
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
from ckanext.ecportal.virtuoso.utils_triplestore_query_helpers import TripleStoreQueryHelpers

import ckanext.ecportal.lib.cache.redis_cache as redis_cache

FILTERED_VOCABULARIES = ['http://publications.europa.eu/resource/authority/corporate-body',
                         'http://publications.europa.eu/resource/authority/dataset-status',
                         'http://publications.europa.eu/resource/authority/dataset-type',
                         'http://publications.europa.eu/resource/authority/frequency',
                         'http://publications.europa.eu/resource/authority/continent',
                         'http://publications.europa.eu/resource/authority/distribution-type',
                         'http://publications.europa.eu/resource/authority/file-type',
                         'http://publications.europa.eu/resource/authority/language',
                         'http://publications.europa.eu/resource/authority/notation-type',
                         'http://publications.europa.eu/resource/authority/documentation-type']

DEFAULT_LANGUAGE = config.get('ckan.locale_default','en')
MD5 = hashlib.md5

class ControlledVocabularyUtil(object):
    """
    This could be the mdr_list object to perform operations on one controlled cocabulary
    It holds a map of instances of the mdr items, where the key is the URI:
    { "http://publications.europa.eu/resource/authority/distribution-type/DOWNLOADABLE_FILE": ConceptSchemaSkosWrapper}
    """
    SKOS_TYPE = ConceptSchemaSkosWrapper

    def __init__(self, mdr_graph_name, mdr_class=None):
        self._mdr_graph_name = mdr_graph_name
        self.schema_concept_scheme = ConceptSchemeSchemaSkosWrapper(mdr_graph_name, mdr_graph_name)
        self.concept_map = {} #type dict[str,ConceptSchemaSkosWrapper]
        self.schema_concept_scheme.get_description_from_ts()
        self.translations = {}
        self.form_values = None
        self.CONCEPT_LIST_QUERY = 'select ?uri from <{0}> where {{  ?uri a <http://www.w3.org/2004/02/skos/core#Concept> . OPTIONAL {{ ?uri <http://publications.europa.eu/ontology/authority/deprecated> "false"}} .}}'
        if 'true' == config.get('ckan.context.odp', 'false') and mdr_graph_name in FILTERED_VOCABULARIES:
            self.CONCEPT_LIST_QUERY = 'select ?uri from <{0}> where {{  ?uri a <http://www.w3.org/2004/02/skos/core#Concept> . ?uri <http://lemon-model.net/lemon#context> <http://publications.europa.eu/resource/authority/use-context/ODP> . OPTIONAL {{ ?uri <http://publications.europa.eu/ontology/authority/deprecated> "false"}}.}}'

        if mdr_graph_name:
            query_helper = TripleStoreQueryHelpers()
            query_str = self.CONCEPT_LIST_QUERY.format(mdr_graph_name)
            result = query_helper.execute_select_query(query_str) or []
            for res in result:
                value = res.get('uri',{}).get('value')
                if not CORPORATE_BODY == mdr_graph_name:
                    self.concept_map[value] = ConceptSchemaSkosWrapper(value, mdr_graph_name)
                else:
                    self.concept_map[value] = CorporateBodyWrapper(value, mdr_graph_name)



    def get_concept_description(self, mdr_uri):
        '''

        :param str mdr_uri:
        :return: ConceptSchemaSkosWrapper|CorporateBodyWrapper
        '''
        if mdr_uri not in self.concept_map.keys():
            return self.SKOS_TYPE('', self._mdr_graph_name)
        concept = self.concept_map.get(mdr_uri, self.SKOS_TYPE(mdr_uri, self._mdr_graph_name))

        if not concept.ttl_as_in_ts:
            concept = self.__get_from_cache(mdr_uri, concept)
            if not concept.ttl_as_in_ts:
                concept.get_description_from_ts()
            self.concept_map[mdr_uri] = concept
            redis_cache.set_value_no_ttl_in_cache(MD5(mdr_uri).hexdigest(), pickle.dumps(concept), pool=redis_cache.VOCABULARY_POOL)

        return concept

    def get_all_translations(self, mdr_uri):
        '''

        :param str mdr_uri:
        :return: dict[str, str]
        '''

        if not self.translations.get(mdr_uri, None):
            concept = self.get_concept_description(mdr_uri)
            result = {}
            for label in concept.schema.prefLabel_skos.values(): #type: ResourceValue
                result[label.lang] = label.value_or_uri
            self.translations[mdr_uri] = result

        return self.translations[mdr_uri]

    def get_all_alternative_labals(self, mdr_uri):
        """

        :param mdr_uri:
        :return:
        """
        concept = self.get_concept_description(mdr_uri)
        result = {}
        for label in concept.schema.altLabel_skos.values(): #type: ResourceValue
            # what if no language indication given?
            result[label.lang] = label.value_or_uri

        return result

    def get_translation_for_language(self, mdr_uri, lang, fallback_language=DEFAULT_LANGUAGE):
        '''

        :param str mdr_uri:
        :param str lang:
        :param str fallback_language:
        :return: str
        '''
        result = self.get_all_translations(mdr_uri)
        return result.get(lang, result.get(fallback_language)) or mdr_uri

    def get_alternative_lable_for_language(self, mdr_uri, lang, fallback_language=DEFAULT_LANGUAGE):
        """

        :param mdr_uri:
        :param lang:
        :param fallback_language:
        :return:
        """
        result = self.get_all_alternative_labals(mdr_uri)
        return result.get(lang, result.get(fallback_language)) or mdr_uri

    def get_all_uris(self):
        '''

        :return: list[str]
        '''
        return self.concept_map.keys()

    def get_all_descriptions(self):
        '''

        :return: list[ConceptSchemaSkosWrapper]
        '''
        result = []
        for uri in self.concept_map.keys():
            result.append(self.get_concept_description(uri))

        return result


    def get_all_values_for_form(self, lang):
        if self.form_values:
            return self.form_values
        result = []
        for uri in self.concept_map.keys():
            label = self.get_translation_for_language(uri, lang)
            result.append({'uri': uri, 'label': label})

        self.form_values = sorted(result, key=lambda k: k['label'])
        return self.form_values

    def prefill_cache_(self):
        """
        Function to prefill the redis cache after it has been flushed
        """
        for mdr_uri, concept in self.concept_map.items():
            concept.get_description_from_ts()
            redis_cache.set_value_no_ttl_in_cache(MD5(mdr_uri).hexdigest(), pickle.dumps(concept), pool=redis_cache.VOCABULARY_POOL)


    def get_mdr_description_for_term_in_prefLabel(self, term):
        # search in every mdr item in every language
        pass


    def __get_from_cache(self, mdr_uri, concept):
        if config.get('ckan.cache.active', 'false') != 'true':
            return concept

        key = MD5(mdr_uri).hexdigest()
        mdr_pickled = redis_cache.get_from_cache(key, pool=redis_cache.VOCABULARY_POOL)
        if mdr_pickled:
            concept = pickle.loads(mdr_pickled)
            return concept

        return concept


class CorporateBodiesUtil(ControlledVocabularyUtil):

    SKOS_TYPE = CorporateBodyWrapper

    def __init__(self, mdr_graph_name, mdr_class=None):
        super(CorporateBodiesUtil, self).__init__(mdr_graph_name, mdr_class)
        self.publisher_hierarchy = None


    def get_publisher_hierarchy(self):
        """
        Use the currently loaded corporate_bodies-skos file in Virtuoso to retrive the publisher hierarchy
        :return: dict result
        """
        from ordereddict import OrderedDict
        if self.publisher_hierarchy:
            return self.publisher_hierarchy

        children_allowed = config.get('ckan.skos.children.authorized', '').split()
        first_level = self.get_first_level_publishers()
        result = OrderedDict()
        for institution in first_level:
            if institution.split('/')[-1].lower() in children_allowed:
                result[institution] = self.get_children_publisher_of(institution)
            else:
                result[institution] = []

        self.publisher_hierarchy = result
        return result



    def get_first_level_publishers(self):
        """
        Returns the 1st level publisher as child of 'European Union' in protocolar order according to the configuration
        :return:
        """
        protocolar_order = config.get('ckan.protocolar_institution_order', '').split()
        #load eurun definitely  from TS
        eurun = CorporateBodyWrapper("http://publications.europa.eu/resource/authority/corporate-body/EURUN", self._mdr_graph_name)
        eurun.get_description_from_ts()
        # compare children with configuration (stacked list comprehension [2 for loops] )
        children = [next((child.uri for child in eurun.schema.narrower_skos.values() if child.uri in self.concept_map.keys() and child.uri.split('/')[-1].lower() == inst.lower()), None) for inst in protocolar_order]
        children = filter(None,children)
        return children


    def get_children_publisher_of(self, publisher_uri):
        """
        Returns all children of the given publisher, by checking each publisher in the valid publishers list if it has the given one as parent.
        :param publisher_uri:
        :return:
        """
        result_list = []

        for uri in self.concept_map.keys():
            current_concept = self.get_concept_description(uri)
            add_child = next((pub.uri for pub in current_concept.schema.broader_skos.values() if pub.uri == publisher_uri),None)
            if add_child:
                result_list.append(current_concept.uri)
        return result_list
