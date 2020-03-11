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
import cPickle as pickle
import time

import ckan
import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckanext.multilingual.plugin as multilingual
import pylons.config
import sqlalchemy
from ckan.common import _
from pylons import config
import ckanext.ecportal.lib.cache.redis_cache as redis_cache

import ckanext.ecportal.unicode_sort as unicode_sort
import ckanext.ecportal.lib.ui_util as ui_util
from ckanext.ecportal.multilingual.languages_constants import LanguagesConstants
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp, SchemaGeneric, DatasetSchemaDcatApOp, ResourceValue
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil

_and_ = sqlalchemy.and_
_or_ = sqlalchemy.or_

log = logging.getLogger(__file__)
UNICODE_SORT = unicode_sort.UNICODE_SORT

KEYS_TO_IGNORE = ['state', 'revision_id', 'id',  # title done seperately
                  'metadata_created', 'metadata_modified', 'site_id',
                  'data_dict', 'rdf', 'extras_rdf', 'validated_data_dict']


def should_ignore(key, value):
    skeys_to_ignore = (True, False, None, 'revision_id', 'approval_status', 'capacity', 'image_url', 'created', 'type',
                       'revision_timestamp', 'state', 'id', 'metadata_modified', 'metadata_created', 'modified_date',
                       'contact_webpage', 'release_date', 'temporal_coverage_to', 'temporal_coverage_from', 'rdf')
    if len(key) == 0:
        return True
    if key[0] in skeys_to_ignore:
        return True
    if key[0] == 'tags' or key[0] == 'keywords' or key[0] == 'resources':
        if len(key) > 2 and (key[2] == 'name' or key[2] == 'display_name' or key[2] == 'description'):
            return False;
        else:
            return True;
    if len(key) > 2 and (key[2] == 'id' or key[2] == 'revision_id'):
        return True;
    if key[0] == 'groups' and len(key) > 2 and key[2] in skeys_to_ignore:
        return True;
    if key[0] == 'extras':
        if len(key) > 2 and key[2] == 'value':
            if isinstance(value, basestring) and value.startswith("<rdf:RDF"):
                return True
            else:
                return False;
        if len(key) > 2 and key[2] in skeys_to_ignore:
            return True;
        if len(key) > 2 and key[2] == 'key':
            if value in skeys_to_ignore:
                return True
    return False


def translate_data_dict(data_dict):
    '''Return the given dict (e.g. a dataset dict) with as many of its fields
    as possible translated into the desired or the fallback language. Just translates
    the data_dict as the original function before.
    :data_dict: the data dictionary with the values to translate
    '''
    return _translate_data_dict(data_dict, False)


def translate_data_dict_for_resource(data_dict):
    ''' Return the given dict (e.g. a dataset dict) with as many of its fields
    as possible translated into the desired or the fallback language. Translates also
    the values with the key 'name' to the desired language. This is only ncessary for
    the resources data dict.
    :data_dict: the data dictionary with the values to translate
    '''
    return _translate_data_dict(data_dict, True)


def _translate_data_dict(data_dict, is_resource):
    '''Return the given dict (e.g. a dataset dict) with as many of its fields
    as possible translated into the desired or the fallback language. Its the private
    function to translate default data_dicts and resource data_dicts.
    :data_dict: the data dictionary with the values to translate
    :is_resource: the flag which indicats that it is a resource.
    '''
    desired_lang_code = pylons.request.environ['CKAN_LANG']
    fallback_lang_code = pylons.config.get('ckan.locale_default', 'en')
    if desired_lang_code == fallback_lang_code:
        codes = desired_lang_code
    else:
        codes = (desired_lang_code, fallback_lang_code)
    # Get a flattened copy of data_dict to do the translation on.
    flattened = ckan.lib.navl.dictization_functions.flatten_dict(
        data_dict)

    # Get a simple flat list of all the terms to be translated, from the
    # flattened data dict.
    terms = set()
    for (key, value) in flattened.items():
        ignore = should_ignore(key, value)
        if ignore:
            continue
        if value in ('', None, True, False):
            continue
        elif isinstance(value, basestring):
            terms.add(value)
        elif isinstance(value, (int, long)):
            continue
        else:
            for item in value:
                if item in (None, True, False):
                    continue
                else:
                    terms.add(item)

    # Get the translations of all the terms (as a list of dictionaries).
    translations = ckan.logic.action.get.term_translation_show(
        {'model': ckan.model},
        {'terms': terms,
         'lang_codes': codes})

    # Transform the translations into a more convenient structure.
    desired_translations = {}
    fallback_translations = {}
    for translation in translations:
        if translation['lang_code'] == desired_lang_code:
            desired_translations[translation['term']] = (
                translation['term_translation'])
        else:
            assert translation['lang_code'] == fallback_lang_code
            fallback_translations[translation['term']] = (
                translation['term_translation'])

    # Make a copy of the flattened data dict with all the terms replaced by
    # their translations, where available.
    translated_flattened = {}
    for (key, value) in flattened.items():

        # Don't translate names that are used for form URLs.
        if key == ('name',) and not is_resource:
            translated_flattened[key] = value
        elif (key[0] in ('tags', 'groups') and len(key) == 3
              and key[2] == 'name'):
            translated_flattened[key] = value

        elif value in (None, True, False):
            # Don't try to translate values that aren't strings.
            translated_flattened[key] = value

        elif isinstance(value, basestring):
            if value in desired_translations:
                translated_flattened[key] = desired_translations[value]
            else:
                translated_flattened[key] = fallback_translations.get(
                    value, value)

        elif isinstance(value, (int, long, dict)):
            translated_flattened[key] = value

        else:
            translated_value = []
            for item in value:
                if item in desired_translations:
                    translated_value.append(desired_translations[item])
                else:
                    translated_value.append(
                        fallback_translations.get(item, item)
                    )
            translated_flattened[key] = translated_value

    # Finally unflatten and return the translated data dict.
    translated_data_dict = (ckan.lib.navl.dictization_functions
                            .unflatten(translated_flattened))
    return translated_data_dict


class ECPortalMultilingualDataset(multilingual.MultilingualDataset):
    def before_index(self, search_data):
        '''

        :param DatasetDcatApOp search_data:
        :return:
        '''
        # same code as in ckanext multilingual except language codes and
        # where mareked
        result_dict = {}
        language_list = config.get('ckan.locales_offered',['en'])
        # translate title
        title = ui_util._get_translated_term_from_dcat_object(search_data.schema, 'title_dcterms', 'en')

        for lang in language_list.split(' '):
            translated_title = ui_util._get_translated_term_from_dcat_object(search_data.schema, 'title_dcterms', lang)
            if translated_title != title:
                result_dict['title_' + lang] = translated_title

        # EC change add sort order field.
        for lang in LanguagesConstants.LANGUAGES:
            title_field = 'title_' + lang
            title_value = result_dict.get(title_field)
            title_string_field = 'title_string_' + lang
            if not title_value:
                title_value = title

            # Strip accents first and if equivilant do next stage comparison.
            # Leaving space and concatonating is to avoid having todo a real
            # 2 level sort.
            sortable_title = \
                unicode_sort.strip_accents(title_value) + '   ' + title_value
            result_dict[title_string_field] = \
                sortable_title.translate(UNICODE_SORT)

        ##########################################

        # # TODO: translate rest
        result_list = search_data.create_multi_lang_full_text()
        for lang in LanguagesConstants.LANGUAGES:
            result_dict['text_{0}'.format(lang)] = result_list.get(lang,'').replace('----','')

        # all_terms = []
        # for key, value in search_data.iteritems():
        #     if key in KEYS_TO_IGNORE or key.startswith('title'):
        #         continue
        #     if not isinstance(value, list):
        #         value = [value]
        #     for item in value:
        #         if isinstance(item, basestring):
        #             all_terms.append(item)
        #
        # field_translations = p.toolkit.get_action('term_translation_show')(
        #     {'model': model},
        #     {'terms': all_terms,
        #      'lang_codes': LanguagesConstants.LANGUAGES})
        #
        # text_field_items = dict(('text_' + lang, []) for lang in LanguagesConstants.LANGUAGES)
        #
        # text_field_items['text_' + default_lang].extend(all_terms)
        #
        # for translation in sorted(field_translations):
        #     lang_field = 'text_' + translation['lang_code']
        #     text_field_items[lang_field].append(
        #         translation['term_translation'])
        #
        # for key, value in text_field_items.iteritems():
        #     search_data[key] = ' '.join(value)

        return result_dict

    def before_search(self, search_params):
        lang_set = set(LanguagesConstants.LANGUAGES)
        current_lang = None
        try:
            current_lang = pylons.request.environ['CKAN_LANG']
        except:
            pass
        # fallback to default locale if locale not in suported LanguagesConstant.LANGUAGES
        if not current_lang in lang_set:
            current_lang = pylons.config.get('ckan.locale_default')
        # fallback to english if default locale is not supported
        if not current_lang in lang_set:
            current_lang = 'en'
        # treat current lang differenly so remove from set
        lang_set.remove(current_lang)

        # weight current lang more highly
        query_fields = 'title_%s^8 text_%s^4' % (current_lang, current_lang)

        for lang in lang_set:
            query_fields += ' title_%s^2 text_%s' % (lang, lang)

        search_params['qf'] = query_fields

        search_string = search_params.get('q') or ''
        if not search_string and not search_params.get('sort'):
            search_params['sort'] = 'score desc, metadata_modified desc'

        return search_params

    def after_search(self, search_results, search_params):

        # Translate the unselected search facets.
        facets = search_results.get('search_facets')
        if not facets:
            return search_results

        desired_lang_code = pylons.request.environ['CKAN_LANG']
        fallback_lang_code = pylons.config.get('ckan.locale_default', 'en')
        if desired_lang_code == fallback_lang_code:
            codes = desired_lang_code
        else:
            codes = (desired_lang_code, fallback_lang_code)

        # Look up translations for all of the facets in one db query.
        overall_time = time.time()
        terms = set()
        for facet in facets.values():
            for item in facet['items']:
                terms.add(item['display_name'])
        translations = ckan.logic.action.get.term_translation_show(
            {'model': ckan.model},
            {'terms': terms,
             'lang_codes': codes})

        factory = ControlledVocabularyFactory()
        language = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.LANGUAGE) #type: ControlledVocabularyUtil
        country = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.COUNTRY) #type: ControlledVocabularyUtil
        eurovoc = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.EUROVOC) #type: ControlledVocabularyUtil
        themes = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.DATA_THEME) #type: ControlledVocabularyUtil
        format = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.FILE_TYPE) #type: ControlledVocabularyUtil

        controlled_vocabularries = {'vocab_theme': themes,
                                    'res_format': format,
                                    'vocab_concepts_eurovoc': eurovoc,
                                    'vocab_geographical_coverage': country,
                                    'vocab_language': language}

        for key, facet in facets.items():
            if key in 'vocab_theme, res_format, vocab_concepts_eurovoc, vocab_geographical_coverage, vocab_language':
                start = time.time()
                for item in facet['items']:
                    item['display_name'] = controlled_vocabularries[key].get_translation_for_language(item['name'], desired_lang_code, fallback_lang_code)
                log.info('mdr {0} facet translation took {1} sec'.format(key, (time.time() - start)))
            elif key == 'vocab_catalog':
                start = time.time()
                for item in facet['items']:
                    item['display_name']= ui_util._get_translaed_catalog(item['name'], desired_lang_code) or item['name']
                log.info('catalogue facet translation took {0} sec'.format(time.time() - start))
            elif key == 'tags':
                start = time.time()
                for item in facet['items']:
                    item['display_name'] = item['name']
                log.info('tags facet translation took {0} sec'.format(time.time() - start))
            else:
                start = time.time()
                for item in facet['items']:
                    if item['name'] == 'true':
                        item['display_name'] = _('ecodp.common.private')
                    elif item['name'] == 'false':
                        item['display_name'] = _('ecodp.common.public')

                    matching_translations = next((translation for
                                             translation in translations
                                             if translation['term'] == item['display_name']
                                             and translation['lang_code'] == desired_lang_code),'')
                    if not matching_translations:
                        matching_translations = next((translation for
                                                 translation in translations
                                                 if translation['term'] == item['display_name']
                                                 and translation['lang_code'] == fallback_lang_code), None)
                    if matching_translations:
                        item['display_name'] = (
                            matching_translations['term_translation'])
                log.info('rest of facets translation took {0} sec'.format(time.time() - start))
        log.info('overall facet translation took {0} sec'.format(time.time() - overall_time))
        return search_results

    def before_view(self, dataset_dict):
        '''
        Use this method to translate the URIs
        :param dict dataset_dict:
        :return dict:
        '''

        _get_publisher_lable(dataset_dict)

        _get_eurovoc_domain_lable(dataset_dict)

        _get_eurovoc_concept_lable(dataset_dict)

        _get_ckan_groups(dataset_dict)

        return dataset_dict


class ECPortalMultilingualGroup(multilingual.MultilingualGroup):
    def before_view(self, data_dict):
        translated_data_dict = translate_data_dict(data_dict)
        return translated_data_dict


class ECPortalMultilingualTag(multilingual.MultilingualTag):
    def before_view(self, data_dict):
        translated_data_dict = translate_data_dict(data_dict)
        return translated_data_dict


def _get_publisher_lable(dataset_dict):
    if not dataset_dict:
        return {}

    org = dataset_dict.get('dataset',{}).get('publisher_dcterms', {}).get('0', {}).get('uri', '')

    org_name = org.split('/')[-1].lower()

    try:
        locale = tk.request.environ['CKAN_LANG']
    except Exception:
        locale = config.get('ckan.locale_default', 'en')

    title = None
    if org_name:
        query1 = model.Session.query(model.Group.title).filter(model.Group.name == org_name)
        publisher_result = query1.all()
        if len(publisher_result) > 0:
            title = publisher_result[0].title
            dataset_dict['organization'] = {'title': title, 'name': org_name}
            # dataset_dict['title'] = title

    if title and 'en' != locale:
        q_trans_group = model.Session.query(model.term_translation_table.c.term_translation) \
            .filter(model.term_translation_table.c.term == title) \
            .filter(
            _or_(model.term_translation_table.c.lang_code == locale, model.term_translation_table.c.lang_code == None))

        translation = q_trans_group.all()

        if len(translation) > 0:
            dataset_dict['organization'] = {'title': translation[0].term_translation, 'name': org_name}
            # pkg_dict['organization']['title'] = translation[0].term_translation

    return dataset_dict


def _get_eurovoc_concept_lable(dataset_dict):
    log.warning('Not implemented yet')
    return dataset_dict


def _get_eurovoc_domain_lable(dataset_dict):
    log.warning('Not implemented yet')
    return dataset_dict


def _get_ckan_groups(dataset_dict):
    log.warning('Not implemented yet')
    return dataset_dict
