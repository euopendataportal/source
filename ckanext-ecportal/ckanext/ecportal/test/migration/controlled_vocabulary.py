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

from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary, BLANKNODE_VARIABLE
from ckanext.ecportal.migration.migration_constants import IDENTIFIER
from ckanext.ecportal.virtuoso.predicates_constants import AUTHORITY_CODE_PREDICATE, IDENTIFIER_URI, IN_SCHEME_PREDICATE, LEGACY_CODE, \
    OP_MAPPED_CODE
from ckanext.ecportal.virtuoso.triplet import Triplet
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import VIRTUOSO_VALUE_KEY, TripleStoreCRUDHelpers, \
    OBJECT_WITH_SPACES, SUBJECT_WITH_SPACES, VIRTUOSO_SUBJECT_RETURN, VIRTUOSO_OBJECT_RETURN
import time
import traceback
import logging
log = logging.getLogger(__file__)

from pylons import config
import ckanext.ecportal.lib.cache.redis_cache as redis_cache
import pickle


def retrieve_all_publishers():
    triplet_list = [Triplet(predicate=IN_SCHEME_PREDICATE, object=Controlled_Vocabulary.publishers),
                    Triplet(predicate=AUTHORITY_CODE_PREDICATE), ]
    searched_fields = SUBJECT_WITH_SPACES + OBJECT_WITH_SPACES
    properties_values = TripleStoreCRUDHelpers().find_any_for_where_clauses(Controlled_Vocabulary.publishers,
                                                                            triplet_list, searched_fields)

    # Transform object retrieved from the helper to a dict mapping authority-code to the value of the corporate-body
    publisher_controller = build_dict_mapping_object_to_subject(properties_values)

    return publisher_controller


def retrieve_all_file_types():
    triplet_list = [Triplet(subject=BLANKNODE_VARIABLE, predicate=LEGACY_CODE),
                    Triplet(predicate=OP_MAPPED_CODE, object=BLANKNODE_VARIABLE), ]
    searched_fields = SUBJECT_WITH_SPACES + OBJECT_WITH_SPACES
    properties_values = TripleStoreCRUDHelpers().find_any_for_where_clauses(Controlled_Vocabulary.file_types,
                                                                            triplet_list, searched_fields)
    # Transform object retrieved from the helper to a dict mapping legacy code to the uri of the parent node
    file_types = build_dict_mapping_object_to_subject(properties_values)

    return file_types

def retrieve_all_file_types_with_context():
    from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
    from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil
    factory = ControlledVocabularyFactory()
    formats = factory.get_controlled_vocabulary_util(
        ControlledVocabularyFactory.FILE_TYPE)  # type: ControlledVocabularyUtil
    list_format = formats.get_all_uris()
    final_list_formats = dict.fromkeys(list_format,"format")


    return final_list_formats




def retrieve_all_frequencies():
    triplet_list = [Triplet(predicate=IDENTIFIER_URI)]
    properties_values = TripleStoreCRUDHelpers().find_any_for_where_clauses(Controlled_Vocabulary.frequency,
                                                                            triplet_list)
    # Transform object retrieved from the helper to a dict mapping frequency identifier to their uri
    frequencies = build_dict_mapping_object_to_subject(properties_values)

    return frequencies


def retrieve_all_datasets_status():
    triplet_list = [Triplet(predicate=AUTHORITY_CODE_PREDICATE)]
    properties_values = TripleStoreCRUDHelpers().find_any_for_where_clauses(Controlled_Vocabulary.dataset_status,
                                                                            triplet_list)
    # Transform object retrieved from the helper to a dict mapping frequency identifier to their uri
    status_dict = build_dict_mapping_object_to_subject(properties_values)

    return status_dict


def retrieve_all_languages():
    return retrieve_authority_codes(Controlled_Vocabulary.language)


def retrieve_all_distribution_types():
    return retrieve_authority_codes(Controlled_Vocabulary.distribution_type)


def retrieve_all_documentation_types():
    return retrieve_authority_codes(Controlled_Vocabulary.documentation_type)


def retrieve_all_country_types():
    return retrieve_authority_codes(Controlled_Vocabulary.country)

def retrieve_all_time_periods():
    return retrieve_authority_codes(Controlled_Vocabulary.time_periodicity)

def retrieve_all_notation_types():
    return retrieve_authority_codes(Controlled_Vocabulary.notation_type)

def retrieve_all_license():
    return retrieve_authority_codes(Controlled_Vocabulary.licence)

def retrieve_all_aurovoc_concept():
    return retrieve_authority_codes(Controlled_Vocabulary.eurovoc)

def retrieve_all_data_themes():
    return retrieve_authority_codes(Controlled_Vocabulary.data_theme)

def retrieve_all_access_rights():
    return retrieve_authority_codes(Controlled_Vocabulary.access_rights)

def retrieve_all_adms():
    return retrieve_authority_codes(Controlled_Vocabulary.adms)

def retrieve_all_dataset_types():
    return retrieve_authority_codes(Controlled_Vocabulary.dataset_type)

def retrieve_authority_codes(controlled_vocabulary):
    triplet_list = [Triplet(predicate=AUTHORITY_CODE_PREDICATE)]
    properties_values = TripleStoreCRUDHelpers().find_any_for_where_clauses(controlled_vocabulary,
                                                                            triplet_list)
    # Transform object retrieved from the helper to a dict mapping frequency identifier to their uri
    dict = build_dict_mapping_object_to_subject(properties_values)
    return dict


def build_dict_mapping_subject_to_object(properties_values):
    dict = {}
    for properties_value in properties_values:
        dict[properties_value.get(VIRTUOSO_SUBJECT_RETURN).get(VIRTUOSO_VALUE_KEY)] = properties_value \
            .get(VIRTUOSO_OBJECT_RETURN) \
            .get(VIRTUOSO_VALUE_KEY)
    return dict


def build_dict_mapping_object_to_subject(properties_values):
    dict = {}
    for properties_value in properties_values:
        dict[properties_value.get(VIRTUOSO_SUBJECT_RETURN).get(VIRTUOSO_VALUE_KEY)] = properties_value \
            .get(VIRTUOSO_OBJECT_RETURN) \
            .get(VIRTUOSO_VALUE_KEY)
    return dict


class ControlledVocabulary:
    def __init__(self):

        start = time.time()

        try:
            active_cache = config.get('ckan.cache.active', 'true')
            cv = None
            if active_cache == 'true':
                # get the ConrolledVocabulary from cache
                controlled_voc_string = redis_cache.get_from_cache("ControlledVocabulary_Mapping", pool=redis_cache.VOCABULARY_POOL)
                if controlled_voc_string:
                    cv = pickle.loads(controlled_voc_string)
                    log.info('Load controlled vocabulary mapping from cache')
                    self.__dict__.update(cv.__dict__)
            if active_cache !='true' or cv is None:
                self.controlled_file_types = retrieve_all_file_types()
                self.controlled_file_types_with_context = retrieve_all_file_types_with_context()
                self.controlled_frequencies = retrieve_all_frequencies()
                self.controlled_status = retrieve_all_datasets_status()
                self.controlled_languages = retrieve_all_languages()
                self.controlled_distribution_types = retrieve_all_distribution_types()
                self.controlled_documentation_types = retrieve_all_documentation_types()
                self.controlled_publishers = retrieve_all_publishers()
                self.controlled_country = retrieve_all_country_types()
                self.controlled_time_period = retrieve_all_time_periods()
                self.controlled_notation_types = retrieve_all_notation_types()
                self.controlled_license = retrieve_all_license()
                self.controlled_eurovoc_concepts= retrieve_all_aurovoc_concept()
                self.controlled_data_themes= retrieve_all_data_themes()
                self.controlled_access_rights = retrieve_all_access_rights()
                self.controlled_adms = retrieve_all_adms()
                self.controlled_datasets_types = retrieve_all_dataset_types()



                redis_cache.set_value_in_cache("ControlledVocabulary_Mapping",pickle.dumps(self),864000, pool=redis_cache.VOCABULARY_POOL)
        except BaseException as e:
            log.error("[ControlledVocabulary]. Build ControlledVocabulary mapping failed")
            traceback.print_exc(e)
        duration = time.time()-start
        log.info("[Duration] get Controlled vocabulary mapping took {0}".format(duration))

