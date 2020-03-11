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

import operator

import ckan.logic as logic
import ckan.model as model
import ckan.new_authz as new_authz
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import pylons

import ckanext.ecportal.helpers as helpers
import ckanext.ecportal.unicode_sort as unicode_sort

from ckanext.ecportal.lib import controlled_vocabulary_util
from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary, VIRTUOSO_VALUE_KEY
from ckanext.ecportal import homepage as homepage
from ckanext.ecportal.model.common_constants import DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP
from ckanext.ecportal.virtuoso.triplet import Triplet
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers, SUBJECT_WITH_SPACES, \
    OBJECT_WITH_SPACES
from validators import (ecportal_date_to_db,
                        ecportal_name_validator,
                        convert_to_groups,
                        convert_from_groups,
                        duplicate_extras_key,
                        keyword_string_convert,
                        rename,
                        update_rdf,
                        requires_field,
                        member_of_vocab,
                        map_licenses,
                        reduce_list,
                        group_name_unchanged,
                        ecportal_description_validator,
                        ecportal_uri_validator)

GEO_VOCAB_NAME = u'geographical_coverage'
EUROVOC_CONCEPTS_VOCAB_NAME = helpers.EUROVOC_CONCEPTS_VOCAB_NAME
EUROVOC_DOMAINS_VOCAB_NAME = helpers.EUROVOC_DOMAINS_VOCAB_NAME
DATASET_TYPE_VOCAB_NAME = u'dataset_type'
LANGUAGE_VOCAB_NAME = u'language'
STATUS_VOCAB_NAME = u'status'
INTEROP_VOCAB_NAME = u'interoperability_level'
TEMPORAL_VOCAB_NAME = u'temporal_granularity'

JSON_FORMAT = 'json'
RDF_FORMAT = 'rdf'
EXCEL_FORMAT = 'excel'
FORMATS = [{'format_id': RDF_FORMAT, 'format_desc': "RDF"}, {'format_id': JSON_FORMAT, 'format_desc': "JSON"},
           {'format_id': EXCEL_FORMAT, 'format_desc': "Excel"}]
UNICODE_SORT = unicode_sort.UNICODE_SORT


def _tags_and_translations(context, vocab, lang, lang_fallback):
    try:
        tags = logic.get_action('tag_list')(context, {'vocabulary_id': vocab})
        tag_translations = helpers.translate(tags, lang, lang_fallback)
        return sorted([(t, tag_translations[t]) for t in tags],
                      key=operator.itemgetter(1))
    except logic.NotFound:
        return []


class ECPortalDatasetForm(p.SingletonPlugin, tk.DefaultDatasetForm):
    p.implements(p.IDatasetForm)

    def setup_template_variables(self, context, data_dict=None, package_type=None):
        c = tk.c
        ckan_lang = str(helpers.current_locale())
        ckan_lang_fallback = str(helpers.fallback_locale())

        c.is_sysadmin = new_authz.is_sysadmin(c.user)

        factory = ControlledVocabularyFactory()

        #self.license = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.LICENSE) #type: ControlledVocabularyUtil

        # Initialize cache if needed
        self.license = controlled_vocabulary_util.retrieve_all_licenses(ckan_lang)

            # Initialize cache if needed
        self.geographical_coverage = controlled_vocabulary_util.retrieve_all_geographical_coverage(ckan_lang)

        self.controlled_keyword = controlled_vocabulary_util.retrieve_all_controlled_keyword(ckan_lang)

        self.domains_eurovoc = controlled_vocabulary_util.retrieve_all_themes(ckan_lang)

        self.status = controlled_vocabulary_util.retrieve_all_datasets_status(ckan_lang)

        self.type_of_dataset = controlled_vocabulary_util.retrieve_all_datasets_types(ckan_lang)

        self.languages = controlled_vocabulary_util.retrieve_all_languages(ckan_lang)

        self.frequency = controlled_vocabulary_util.retrieve_all_frequencies(ckan_lang)

        self.temporal_granularity = controlled_vocabulary_util.retrieve_all_time_periodicity(ckan_lang)

        #self.notation_skos = controlled_vocabulary_util.retrieve_all_notation_skos(ckan_lang)
        self.notation_skos = controlled_vocabulary_util.retrieve_all_notation_types(ckan_lang)

        self.formats = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.FILE_TYPE) #type: ControlledVocabularyUtil

        if (c.action in (u'edit', u'new', u'editresources', u'manage_package', u'update', 'bulk_update')):

            c.license = self.license
            c.geographical_coverage = self.geographical_coverage
            c.controlled_keyword = self.controlled_keyword
            c.domains_eurovoc = self.domains_eurovoc
            c.publishers = helpers.organizations_available(c.user)
            c.status = controlled_vocabulary_util.retrieve_all_datasets_status(ckan_lang)
            c.type_of_dataset = controlled_vocabulary_util.retrieve_all_datasets_types(ckan_lang)
            c.languages = controlled_vocabulary_util.retrieve_all_languages(ckan_lang)
            c.temporal_granularity = controlled_vocabulary_util.retrieve_all_time_periodicity(ckan_lang)
            c.groups = homepage.get_groups('display_name')
            c.frequency = self.frequency
            c.notation_skos = self.notation_skos
            c.formats = self.formats.get_all_values_for_form(ckan_lang)


            # datasets_titles_dict = self.retrieve_all_datasets_titles(c)
            # c.datasets = datasets_titles_dict

        if c.action in (u'dashboard'):
            c.formats = FORMATS

        # get new group name if group ID in query string
        new_group_id = pylons.request.params.get('groups__0__id')
        if new_group_id:
            try:
                data = {'id': new_group_id}
                new_group = p.toolkit.get_action('group_show')(context, data)
                c.new_group = new_group['name']
            except p.toolkit.ObjectNotFound:
                c.new_group = None

        # find extras that are not part of our schema
        c.additional_extras = []
        schema_keys = self.create_package_schema().keys()
        if c.pkg_dict:
            extras = c.pkg_dict.get('extras', [])
            if extras:
                for extra in extras:
                    if not extra['key'] in schema_keys:
                        c.additional_extras.append(extra)

        # This is messy as auths take domain object not data_dict
        context_pkg = context.get('package', None)
        pkg = context_pkg or c.pkg
        if pkg:
            try:
                if not context_pkg:
                    context['package'] = pkg
                logic.check_access('package_update', context)
                c.auth_for_change_state = True
            except logic.NotAuthorized:
                c.auth_for_change_state = False

    def retrieve_all_datasets_titles(self, c):
        triple_store_CRUD_helper = TripleStoreCRUDHelpers()
        triplet_list = [
            Triplet(predicate=NAMESPACE_DCATAPOP.rdf + 'type', object=NAMESPACE_DCATAPOP.dcat + 'Dataset'),
            Triplet(predicate=NAMESPACE_DCATAPOP.dcterms + 'title',
                    filter="FILTER(lang(?o) = '{0}')".format(c.language)), ]
        searched_fields = SUBJECT_WITH_SPACES + OBJECT_WITH_SPACES
        datasets_titles_dict = {}
        datasets = triple_store_CRUD_helper.find_any_in_graphs_for_where_clauses(
            [DCATAPOP_PUBLIC_GRAPH_NAME, DCATAPOP_PRIVATE_GRAPH_NAME], triplet_list,
            searched_fields)
        for dataset in datasets:
            datasets_titles_dict[dataset.get('s').get(VIRTUOSO_VALUE_KEY)] = dataset.get('o').get(VIRTUOSO_VALUE_KEY)
        return datasets_titles_dict

    def _modify_package_schema(self, schema):
        helpers.tags = None
        schema.update({
            'name': [unicode, ecportal_name_validator,
                     tk.get_validator('package_name_validator')],
            'license_id': [tk.get_validator('ignore_missing'), reduce_list, map_licenses, unicode],
            'keyword_string': [tk.get_validator('ignore_missing'), keyword_string_convert],
            'alternative_title': [tk.get_validator('ignore_missing'), unicode, tk.get_converter('convert_to_extras')],
            'capacity': [tk.get_validator('ignore_missing'), unicode, tk.get_validator('default')(u'private'),
                         convert_to_groups('capacity')],
            'description': [unicode, ecportal_description_validator],
            'url': [unicode, ecportal_uri_validator],
            'status': [tk.get_converter('convert_to_tags')(STATUS_VOCAB_NAME)],
            'identifier': [tk.get_validator('ignore_missing'), unicode, tk.get_converter('convert_to_extras')],
            'interoperability_level': [tk.get_validator('ignore_missing'),
                                       tk.get_converter('convert_to_tags')(INTEROP_VOCAB_NAME)],
            'type_of_dataset': [tk.get_validator('ignore_missing'),
                                tk.get_converter('convert_to_tags')(DATASET_TYPE_VOCAB_NAME)],
            'release_date': [tk.get_validator('ignore_missing'), ecportal_date_to_db,
                             tk.get_converter('convert_to_extras')],
            'modified_date': [tk.get_validator('ignore_missing'), ecportal_date_to_db,
                              tk.get_converter('convert_to_extras')],
            'accrual_periodicity': [tk.get_validator('ignore_missing'), unicode,
                                    tk.get_converter('convert_to_extras')],
            'temporal_coverage_from': [tk.get_validator('ignore_missing'), ecportal_date_to_db,
                                       tk.get_converter('convert_to_extras')],
            'temporal_coverage_to': [tk.get_validator('ignore_missing'), ecportal_date_to_db,
                                     tk.get_converter('convert_to_extras')],
            'temporal_granularity': [tk.get_validator('ignore_missing'),
                                     tk.get_converter('convert_to_tags')(TEMPORAL_VOCAB_NAME)],
            'geographical_coverage': [tk.get_validator('ignore_missing'),
                                      tk.get_converter('convert_to_tags')(GEO_VOCAB_NAME)],
            'concepts_eurovoc': [tk.get_validator('ignore_missing'),
                                 tk.get_converter('convert_to_tags')(EUROVOC_CONCEPTS_VOCAB_NAME)],
            'language': [tk.get_validator('ignore_missing'), tk.get_converter('convert_to_tags')(LANGUAGE_VOCAB_NAME)],
            'metadata_language': [tk.get_validator('ignore_missing'),
                                  member_of_vocab(LANGUAGE_VOCAB_NAME),
                                  tk.get_converter('convert_to_extras')],
            'version_description': [tk.get_validator('ignore_missing'), unicode,
                                    tk.get_converter('convert_to_extras')],
            'rdf': [tk.get_validator('ignore_missing'), unicode, update_rdf, tk.get_converter('convert_to_extras')],
            'contact_name': [tk.get_validator('ignore_missing'), unicode, tk.get_converter('convert_to_extras')],
            'contact_email': [tk.get_validator('ignore_missing'), requires_field('contact_name'),
                              unicode, tk.get_converter('convert_to_extras')],
            'contact_address': [tk.get_validator('ignore_missing'), requires_field('contact_name'),
                                unicode, tk.get_converter('convert_to_extras')],
            'contact_telephone': [tk.get_validator('ignore_missing'),
                                  requires_field('contact_name'),
                                  unicode, tk.get_converter('convert_to_extras')],
            'contact_webpage': [tk.get_validator('ignore_missing'), requires_field('contact_name'),
                                unicode, tk.get_converter('convert_to_extras')],
            'groups': [tk.get_validator('ignore_missing'), requires_field('groups'),
                       unicode, tk.get_converter('convert_to_extras')],
            '__after': [duplicate_extras_key,
                        rename('keywords', 'tags'),
                        rename('description', 'notes')],
        })

        # TODO: check if this still relevant in new model
        # schema['groups'].update({
        #     'type': [tk.get_validator('ignore_missing'), unicode, convert_resource_type]
        # })
        return schema

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(ECPortalDatasetForm, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(ECPortalDatasetForm, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(ECPortalDatasetForm, self).show_package_schema()
        schema['tags']['__extras'].append(tk.get_converter('free_tags_only'))
        schema.update({
            'id': [tk.get_validator('ignore_missing'), unicode],
            'alternative_title': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'status': [tk.get_converter('convert_from_tags')(STATUS_VOCAB_NAME), tk.get_validator('ignore_missing')],
            'identifier': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'interoperability_level': [tk.get_converter('convert_from_tags')(INTEROP_VOCAB_NAME),
                                       tk.get_validator('ignore_missing')],
            'type_of_dataset': [tk.get_converter('convert_from_tags')(DATASET_TYPE_VOCAB_NAME),
                                tk.get_validator('ignore_missing')],
            'capacity': [convert_from_groups('capacity')],
            'release_date': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'modified_date': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'accrual_periodicity': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'temporal_coverage_from': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'temporal_coverage_to': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'temporal_granularity': [tk.get_converter('convert_from_tags')(TEMPORAL_VOCAB_NAME),
                                     tk.get_validator('ignore_missing')],
            'geographical_coverage': [tk.get_converter('convert_from_tags')(GEO_VOCAB_NAME),
                                      tk.get_validator('ignore_missing')],
            'concepts_eurovoc': [helpers.filter_tags(EUROVOC_CONCEPTS_VOCAB_NAME),
                                 tk.get_validator('ignore_missing')],
            'domains_eurovoc': [helpers.filter_tags(EUROVOC_DOMAINS_VOCAB_NAME),
                                tk.get_validator('ignore_missing')],
            'language': [tk.get_converter('convert_from_tags')(LANGUAGE_VOCAB_NAME),
                         tk.get_validator('ignore_missing')],
            'metadata_language': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'version_description': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'rdf': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'contact_name': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'contact_email': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'contact_address': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'contact_telephone': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'contact_webpage': [tk.get_converter('convert_from_extras'), tk.get_validator('ignore_missing')],
            'license_url': [tk.get_validator('ignore_missing')],
            'license_title': [tk.get_validator('ignore_missing')],
            'views_total': [tk.get_validator('ignore_missing')],
            'download_total': [tk.get_validator('ignore_missing')],
            'metadata_created': [tk.get_validator('ignore_missing')],
            'metadata_modified': [tk.get_validator('ignore_missing')],
            '__after': [tk.get_validator('duplicate_extras_key'),
                        rename('tags', 'keywords'),
                        rename('notes', 'description')]
        })

        schema['resources'].update({
            'created': [tk.get_validator('ignore_missing')],
            'position': [],
            'last_modified': [tk.get_validator('ignore_missing')],
            'cache_last_updated': [tk.get_validator('ignore_missing')],
            'webstore_last_updated': [tk.get_validator('ignore_missing')],
            'download_total_resource':[tk.get_validator('ignore_missing')],
            'iframe_code': [tk.get_validator('ignore_missing')]
        })
        # schema['groups'].update({
        #     'type': [tk.get_validator('ignore_missing')],
        # })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []


class ECPortalPublisherForm(p.SingletonPlugin):
    p.implements(p.IGroupForm, inherit=True)
    p.implements(p.IRoutes)

    def before_map(self, map):
        controller = 'ckanext.organizations.controllers:OrganizationController'
        map.connect('/publisher/users/{id}', controller=controller,
                    action='users')
        map.connect('/publisher/apply/{id}', controller=controller,
                    action='apply')
        map.connect('/publisher/apply', controller=controller, action='apply')
        map.connect('/publisher/edit/{id}', controller='group', action='edit')
        map.connect('/publisher/history/{id}', controller='group',
                    action='history')
        map.connect('/publisher/new', controller='group', action='new')
        map.connect('/publisher/{id}', controller='group', action='read')
        map.connect('/publisher', controller='group', action='index')

        '''tag_controller = 'ckanext.ecportal.controllers:ECPortalTagController'
        map.connect('/domain/{id}', controller=tag_controller, action='search_domain')
        map.connect('/concept/{id}', controller=tag_controller, action='search_concept')'''

        map.redirect('/publishers', '/publisher')
        map.redirect('/organization/{url:.*}', '/publisher/{url}')
        return map

    def after_map(self, map):
        return map

    def group_types(self):
        return ['organization']

    def is_fallback(self):
        return True

    def show_package_schema(self):
        '''Custom group schema for EC portal.

        Does not allow an existing group's name to be changed.
        '''
        schema = super(ECPortalPublisherForm, self).show_package_schema()
        schema.update({
            'name': [unicode, group_name_unchanged],
            'title': [tk.get_validator('ignore_missing')],
            'capacity': [tk.get_validator('ignore_missing'), unicode]
        })

        return schema

    def _modify_package_schema(self, schema):
        schema['groups'].update({
            'capacity': [tk.get_validator('ignore_missing'), unicode]
        })
        return schema

    def update_package_schema(self):
        schema = super(ECPortalPublisherForm, self).update_package_schema()
        return self._modify_package_schema(schema);

    def create_package_schema(self):
        schema = super(ECPortalPublisherForm, self).create_package_schema()
        return self._modify_package_schema(schema);

    def setup_template_variables(self, context, data_dict):
        c = p.toolkit.c

        c.user_groups = c.userobj.get_groups('organization')
        local_ctx = {'model': model, 'session': model.Session,
                     'user': c.user or c.author}

        try:
            logic.check_access('group_create', local_ctx)
            c.is_superuser_or_groupadmin = True
        except logic.NotAuthorized:
            c.is_superuser_or_groupadmin = False

        if 'group' in context:
            group = context['group']

            # Only show possible groups where the current user is a member
            c.possible_parents = c.userobj.get_groups('organization', 'admin')
            c.parent = None
            grps = group.get_groups('organization')
            if grps:
                c.parent = grps[0]
            c.users = group.members_of_type(model.User)
