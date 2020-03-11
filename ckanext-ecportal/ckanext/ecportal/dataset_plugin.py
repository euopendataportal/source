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
import operator

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckan.model as model
import ckanext.ecportal.helpers as helpers
import ckanext.ecportal.unicode_sort as unicode_sort
import ckan.logic as logic

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
FORMATS = [{'format_id':RDF_FORMAT, 'format_desc' : "RDF"}, {'format_id' : JSON_FORMAT, 'format_desc': "JSON"}, {'format_id' : EXCEL_FORMAT, 'format_desc' : "Excel"}]
UNICODE_SORT = unicode_sort.UNICODE_SORT

def _tags_and_translations(context, vocab, lang, lang_fallback):
    try:
        tags = logic.get_action('tag_list')(context, {'vocabulary_id': vocab})
        tag_translations = helpers.translate(tags, lang, lang_fallback)
        return sorted([(t, tag_translations[t]) for t in tags],
                key=operator.itemgetter(1))
    except logic.NotFound:
        return []


class DatasetPlugin(plugins.SingletonPlugin, tk.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def setup_template_variables(self, context, data_dict=None,
                             package_type=None):
        '''
        Use this function to set up site properties, make use of Redis cache
        '''
        c = tk.c