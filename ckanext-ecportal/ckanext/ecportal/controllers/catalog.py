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
import traceback
import pickle

import ckan.lib.base as base
import ckan.lib.helpers as core_helpers
import ckan.lib.navl.dictization_functions
import ckan.lib.navl.dictization_functions as dict_func
import ckan.lib.search as search
import ckan.logic as logic
import ckan.plugins.toolkit as tk
import ckanext.ecportal.helpers as helpers
import ckanext.ecportal.lib.uri_util as uri_util
import ckanext.ecportal.query_solr_helpers as qsh
import pylons.config as config
import sqlalchemy
from ckan.common import _, request, c, g
from ckanext.ecportal.lib import controlled_vocabulary_util
from ckanext.ecportal.lib import ui_util
from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary
from ckanext.ecportal.lib.ui_util import _get_translated_term_from_dcat_object, DEFAULT_LANGUAGE, \
    _get_organization_translation_from_database
from ckanext.ecportal.model.catalog_dcatapop import CatalogDcatApOp
from ckanext.ecportal.model.dataset_dcatapop import SchemaGeneric, ResourceValue, DatasetDcatApOp
from ckanext.ecportal.model.schemas import RightsStatementSchemaDcatApOp
from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import OBJECT_WITH_SPACES

import ckanext.ecportal.lib.cache.redis_cache as redis_cache

from doi.facade import doi_facade
import ckanext.ecportal.helpers as ckanext_helpers
import ckanext.ecportal.configuration.configuration_constants as constants
from ckanext.ecportal.lib.ui_util import _get_doi_from_adms_identifier

all_languages = config.get('ckan.locales_offered').split(' ')
all_languages.remove('zh')

check_access = logic.check_access
render = base.render
abort = base.abort
redirect = base.redirect
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action
lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin
log = logging.getLogger(__name__)
_check_access = logic.check_access
_and_ = sqlalchemy.and_

from rdflib import XSD

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from ckanext.ecportal.configuration.configuration_constants import CKAN_PATH

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': CKAN_PATH + '/var/cache',
    'cache.lock_dir': CKAN_PATH + '/var/cache'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))


class ECPORTALCatalogController(base.BaseController):
    def read(self, id, limit=20):
        context = {'user': c.user, 'for_view': True }
        # Get Catalog details except data sets #
        language = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'catalog')
        name_or_id = '{0}/{1}'.format(uri_prefix, id)
        get_action('catalogue_show')(context, {'uri': name_or_id})
        catalogue = context.get('catalogue')
        c.catalog_dict = self._transform_catalog_schema_to_ui_schema(catalogue)

        c.catalog_dict['citation_styles'] = constants.DOI_CONFIG.citation_formats
        c.catalog_dict['citation'] = ui_util.get_citation(c.catalog_dict.get('doi', ''), language)

        # Show more / Show less mechanism for has_part field #
        c.NUM_HAS_PART_CATALOG = int(config.get('ckan.catalog.has_part', 5))

        # Build and execute SolR query #
        try:
            c.q = request.params.get('q', '')  # Save query in search box
            query_dict = qsh.initialize_query()
            qsh.update_template_ctx_before_query(query_dict)

            # Adapt manually the query: used to get data set if url does not contain vocab_catalog parameter #
            if 'vocab_catalog' not in query_dict.get('q'):
                query_dict['q'] += ' vocab_catalog:"%s"' % name_or_id

            # Build Solr query dict #
            solr_dict = {'q': query_dict.get('q'),
                         'facet.field': c.facet_titles.keys(),
                         'rows': limit,
                         'sort': c.sort_by_selected,
                         'start': (c.num_page - 1) * limit}

            query = qsh.execute_query(config.get('ckan.cache.active', 'false'), solr_dict, c.user or c.author)
            qsh.update_template_ctx_after_query(query, limit, g.facets_default_number)

        except search.SearchError as se:
            qsh.treat_search_error_exception('Catalog search error', se.args)

        return render('catalog/read.html')

    def new(self, data=None, errors=None, error_summary=None):
        context = {'model': 'catalog',
                   'user': c.user or c.author,
                   'save': 'save' in request.params,
                   'parent': request.params.get('parent', None)}
        try:
            _check_access('catalog_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a catalog'))

        if context['save'] and not data:
            return self._save_new(context, data)

        data = data or {}
        if not data.get('image_url', '').startswith('http'):
            data.pop('image_url', None)

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new'}

        # self._setup_template_variables(context, data)
        self.__setup_controller_parameter()
        c.form = render('catalog/snippets/new_catalog_form.html',
                        extra_vars=vars)
        return render('catalog/new.html')

    def edit(self, id, data=None, errors=None, error_summary=None):
        context = {'model': 'catalog',
                   'user': c.user or c.author,
                   'save': 'save' in request.params,
                   'parent': request.params.get('parent', None)}

        data_dict = {'id': id}

        try:
            _check_access('catalog_update', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a catalog'))

        if context['save'] and not data:
            return self._save_edit(id, context)

        uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'catalog')
        name_or_id = ''
        if data_dict.get("id"):
            name_or_id = '{0}/{1}'.format(uri_prefix, data_dict.get("id"))
        else:
            name_or_id = data_dict.get("uri")

        try:
            get_action('catalogue_show')(context, {'uri': name_or_id})
            old_ctl = catalog = context.get('catalogue')

            c.catalogtitle = old_ctl.schema.title_dcterms.get('0',ResourceValue('')).value_or_uri
            c.uri = old_ctl.catalog_uri
            c.name = old_ctl.catalog_uri.split('/')[-1]
            c.description = old_ctl.schema.description_dcterms.get('0',ResourceValue('')).value_or_uri

            data_dict = self._transform_catalog_schema_to_form_dict(old_ctl)

            # transform catalolg schema to ui dict

            data = data or old_ctl
        except NotFound:
            abort(404, _('Catalog not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read catalog %s') % '')
        except Exception:
            abort(400, _('Could not retrieve the data of the catalog %s') % '')

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data_dict, 'errors': errors,
                'error_summary': error_summary, 'action': 'edit'}

        self.__setup_controller_parameter(old_ctl)

        c.catalog_dict = data_dict

        c.form = render('catalog/snippets/new_catalog_form.html', extra_vars=vars)
        return render('catalog/new_update.html')

    def _transform_catalog_schema_to_ui_schema(self, catalog):
        import copy
        data_dict = self._transform_catalog_schema_to_form_dict(catalog)
        catalog_dict = copy.deepcopy(data_dict)
        catalog_dict['uri'] = catalog.catalog_uri
        catalog_dict['display_themes'] = ui_util._get_translated_term_from_dcat_object(catalog.schema,
                                                                                       'themeTaxonomy_dcat',
                                                                                       core_helpers.lang())
        catalog_dict['display_languages'] = ui_util._get_translated_term_from_dcat_object(catalog.schema,
                                                                                          'language_dcterms',
                                                                                          core_helpers.lang())
        catalog_dict['display_is_part_of'] = dict(
            {'name': ui_util._get_translaed_catalog(data_dict.get('is_part_of'), core_helpers.lang()),
             'uri': data_dict.get('is_part_of').split('/')[-1]})
        catalog_dict['publisher'] = catalog.schema.publisher_dcterms.get('0', SchemaGeneric('')).uri
        catalog_dict['display_has_part'] = [
            dict({'name': ui_util._get_translaed_catalog(catalog_uri, core_helpers.lang()),
                  'uri': catalog_uri.split('/')[-1],
                  'vocab': catalog_uri})
            for catalog_uri in data_dict.get('has_part')]
        return catalog_dict

    def _transform_catalog_schema_to_form_dict(self, catalog):
        '''
        trandform the dcat catalog object to data dict
        :param catalog:
        :return:
        '''

        try:
            data_dict = {}
            data_dict['release_date'] = catalog.schema.issued_dcterms.get("0", ResourceValue('')).value_or_uri
            data_dict['modified_date'] = catalog.schema.modified_dcterms.get("0",
                                                                             ResourceValue('')).value_or_uri
            data_dict['organization'] = _get_organization_translation_from_database(catalog.schema,
                                                                                    "publisher_dcterms",
                                                                                    DEFAULT_LANGUAGE) or {}
            data_dict['theme'] = [theme.uri for theme in catalog.schema.themeTaxonomy_dcat.values()]
            data_dict['language'] = [language.uri for language in catalog.schema.language_dcterms.values()]
            data_dict['licence'] = [licence.uri for licence in catalog.schema.license_dcterms.values()]
            data_dict['rights'] = catalog.schema.rights_dcterms.get('0', RightsStatementSchemaDcatApOp(
                '')).label_rdfs.get('0', ResourceValue(
                '')).value_or_uri

            data_dict['is_part_of'] = catalog.schema.isPartOf_dcterms.get('0', SchemaGeneric('')).uri
            data_dict['has_part'] = [catalog_part.uri for catalog_part in catalog.schema.hasPart_dcterms.values()]
            data_dict['geographical_coverage'] = [geo_cov.uri for geo_cov in catalog.schema.spatial_dcterms.values()]

            if hasattr(catalog.schema, "identifier_adms") and catalog.schema.identifier_adms:
                data_dict['doi'] =  _get_doi_from_adms_identifier (catalog.schema.identifier_adms).value_or_uri

            if hasattr(catalog.schema, "homepage_foaf") and catalog.schema.homepage_foaf:
                home_page = catalog.schema.homepage_foaf.get('0', SchemaGeneric(''))
                if isinstance(home_page, ResourceValue):
                    data_dict['home_page'] = home_page.value_or_uri
                else:
                    home_page.get_description_from_ts()
                    if hasattr(home_page, "url_schema") and home_page.url_schema:
                        data_dict['home_page'] = home_page.url_schema.get('0', ResourceValue('')).value_or_uri
            else:
                data_dict['home_page'] = catalog.schema.homepage_foaf.get('0', ResourceValue('')).value_or_uri

            for lang in all_languages:
                title = _get_translated_term_from_dcat_object(catalog.schema, 'title_dcterms', lang,
                                                              for_form=True)
                if title and DEFAULT_LANGUAGE == lang:
                    data_dict['title'] = title
                elif title:
                    data_dict['title-{0}'.format(lang)] = title

                description = _get_translated_term_from_dcat_object(catalog.schema, 'description_dcterms',
                                                                    lang,
                                                                    for_form=True)
                if description and DEFAULT_LANGUAGE == lang:
                    data_dict['description'] = description
                elif description:
                    data_dict['description-{0}'.format(lang)] = description

            return data_dict
        except BaseException as e:
            log.error("Can not transform catalog object to form dict")
            import traceback
            log.error(traceback.print_exc())

    def _transform_data_dict_to_catalog(self, data_dict, old_uri=None):
        '''

        :param data_dict:
        :return:
        '''

        def get_lang(catalog_prop):
            '''
            get the langagne of the property
            :param property_name:
            :return:
            '''
            lang = DEFAULT_LANGUAGE
            if catalog_prop.partition('-')[2]:
                lang = catalog_prop.partition('-')[2]
            return lang

        if not data_dict.get('title') or not data_dict.get('description'):
            raise ValidationError('Mandatory fields not set')

        try:
            title = data_dict.get('title', '')
            if old_uri:
                uri = old_uri
            else:
                uri, name = uri_util.new_cataloge_uri_from_title(title)

            catalog = CatalogDcatApOp(uri)
            if data_dict.get('release_date'):
                catalog.schema.issued_dcterms['0'] = ResourceValue(data_dict.get('release_date'),
                                                                   datatype=XSD.date)
            if data_dict.get('modified_date'):
                catalog.schema.modified_dcterms['0'] = ResourceValue(data_dict.get('modified_date'),
                                                                     datatype=XSD.date)
            if data_dict.get('licence'):
                catalog.schema.license_dcterms['0'] = SchemaGeneric(data_dict.get('licence'))

            if data_dict.get('is_part_of'):
                catalog.schema.isPartOf_dcterms['0'] = SchemaGeneric(data_dict.get('is_part_of'))

            has_part = data_dict.get('has_part')
            if has_part:
                for has_part_uri in has_part.split(" "):
                    if has_part_uri:
                        has_part_length = str(len(catalog.schema.hasPart_dcterms))
                        catalog.schema.hasPart_dcterms[has_part_length] = SchemaGeneric(has_part_uri)

            catalog.set_doi(data_dict.get('doi', None))
            catalog.set_home_page(data_dict)
            catalog.set_rights(data_dict)
            catalog.set_spatial(data_dict)

            if data_dict.get("owner_org"):
                ds = DatasetDcatApOp('uri')  # just to use the converstion of publisher
                from ckanext.ecportal.lib.dataset_util import set_publisher_to_dataset_from_dict
                owner_org = data_dict.get("owner_org")
                set_publisher_to_dataset_from_dict(ds, data_dict)  # TODO get the publisher URI
                catalog.schema.publisher_dcterms = ds.schema.publisher_dcterms

            # create multi lang values of the catalog DCATAP object
            for catalog_prop in data_dict:
                ind = 0
                if 'title' in catalog_prop:
                    lang = get_lang(catalog_prop)
                    catalog.schema.title_dcterms[str(ind)] = ResourceValue(data_dict[catalog_prop],
                                                                               lang=lang)
                    ind += 1
                ind = 0
                if 'description' in catalog_prop:
                    lang = get_lang(catalog_prop)
                    catalog.schema.description_dcterms[str(ind)] = ResourceValue(data_dict[catalog_prop], lang=lang)
                    ind += 1

            themes = data_dict.get('theme', None)
            if themes:
                if not isinstance(themes, list):
                    themes = [themes]
                ind = 0
                for theme in themes:
                    catalog.schema.themeTaxonomy_dcat[str(ind)] = SchemaGeneric(theme)
                    ind += 1

            languages = data_dict.get('language', None)
            if languages:
                if not isinstance(languages, list):
                    languages = [languages]
                ind = 0
                for language in languages:
                    catalog.schema.language_dcterms[str(ind)] = SchemaGeneric(language)
                    ind += 1

            return catalog
        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error('Can not transform the dict to catalog')

    def _save_new(self, context, data):
        try:
            data_dict = self.__transform_to_data_dict(request.POST)
            context['message'] = data_dict.get('log_message', '')
            data_dict['users'] = [{'name': c.user, 'capacity': 'admin'}]
            catalog = self._transform_data_dict_to_catalog(data_dict)

            result = catalog.save_to_ts()
            if result:
                active_cache = config.get('ckan.cache.active', 'false')
                if active_cache == 'true':
                    redis_cache.flush_all_from_db(redis_cache.MISC_POOL)
                    redis_cache.set_value_no_ttl_in_cache(catalog.catalog_uri, pickle.dumps(catalog), pool=redis_cache.DATASET_POOL)
                if data_dict.get('doi'):
                    get_action('assign_doi')(context, catalog)
                    get_action('publish_doi')(context, catalog)

                url = core_helpers.url_for(controller='ckanext.ecportal.controllers.catalog:ECPORTALCatalogController',
                                           action='dashboard_catalogs')
                base.redirect(url)
                self.dashboard_catalogs()
            if not result:
                self.new(data_dict)

        except NotAuthorized:
            abort(401, _('Unauthorized to read catalog %s') % '')
        except NotFound, e:
            abort(404, _('Catalog not found'))
        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new(data_dict, errors, error_summary)
        return

    def _save_edit(self, id, context):
        try:
            data_dict = self.__transform_to_data_dict(request.POST)
            context['message'] = data_dict.get('log_message', '')
            # title = data_dict.get('title', '')
            # catalog = CatalogDcatApOp(uri)
            # catalog.get_description_from_ts()
            # catalog.schema.title_dcterms['0'] = ResourceValue(title, lang='en')
            # if data_dict.get('description'):
            #     catalog.schema.description_dcterms['0'] = ResourceValue(data_dict['description'], lang='en')

            uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'catalog')
            name_or_id = ''
            name_or_id = '{0}/{1}'.format(uri_prefix, id)
            get_action('catalogue_show')(context, {'uri': name_or_id})
            old_ctl = catalog = context.get('catalogue')
            old_dict = self._transform_catalog_schema_to_form_dict(old_ctl)

            if old_dict.get('doi'):
                if old_dict.get('doi') != data_dict.get('doi'):
                    raise ValidationError({"DOI": [_("ckan.catalog.doi.invalid")]})

            edit_catalog = self._transform_data_dict_to_catalog(data_dict, name_or_id)
            old_ctl.schema = edit_catalog.schema

            result = old_ctl.save_to_ts()
            if result:
                active_cache = config.get('ckan.cache.active', 'false')
                if active_cache == 'true':
                    redis_cache.flush_all_from_db(redis_cache.MISC_POOL)
                    redis_cache.set_value_no_ttl_in_cache(old_ctl.catalog_uri, pickle.dumps(old_ctl), pool=redis_cache.DATASET_POOL)
                if data_dict.get('doi'):
                    get_action('publish_doi')(context, edit_catalog)
                url = core_helpers.url_for(controller='ckanext.ecportal.controllers.catalog:ECPORTALCatalogController',
                                           action='dashboard_catalogs')
                base.redirect(url)
                self.dashboard_catalogs()

        except NotAuthorized:
            abort(401, _('Unauthorized to read catalog %s') % id)
        except NotFound, e:
            abort(404, _('Catalog not found'))

        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.edit(id, data_dict, errors, error_summary)

    def __transform_to_data_dict(self, reqest_post):
        '''
        Transform the POST body to data_dict usable by the actions ('package_update', 'package_create', ...)
        :param the POST body of the request object
        :return: a dict usable by the actions
        '''

        # Initialize params dictionary
        data_dict = logic.parse_params(reqest_post)

        for key in data_dict.keys():
            if 'template' in key:
                data_dict.pop(key, None)

        try:
            data_dict = logic.tuplize_dict(data_dict)
        except Exception, e:
            log.error(e.message)

        data_dict = dict_func.unflatten(data_dict)
        data_dict = logic.clean_dict(data_dict)

        return data_dict

    def __setup_controller_parameter(self, catalog=None):
        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        c.languages = controlled_vocabulary_util.retrieve_all_languages(locale)

        c.licences = controlled_vocabulary_util.retrieve_all_licenses(locale)

        c.domains_eurovoc = controlled_vocabulary_util.retrieve_all_themes(locale)

        # Initialize cache if needed
        c.geographical_coverage = controlled_vocabulary_util.retrieve_all_geographical_coverage(locale)

        c.publishers = helpers.organizations_available(c.user)
        c.domain = '{0}/catalog/'.format(config.get('ckan.ecodp.uri_prefix', ''))
        c.catalog_dict = {}
        translations = {}
        if catalog:
            for schema in catalog.schema.title_dcterms.values():  # type: ResourceValue
                if schema.lang and schema.lang != 'en':
                    translations['title-{0}'.format(schema.lang)] = schema.value_or_uri
            for schema in catalog.schema.description_dcterms.values():  # type: ResourceValue
                if schema.lang and schema.lang != 'en':
                    translations['title-{0}'.format(schema.lang)] = schema.value_or_uri

        c.translations = translations
        c.publishers = helpers.organizations_available(c.user)
        c.catalogs = CatalogDcatApOp.get_ui_list_catalogs(locale)

    def dashboard_catalogs(self):
        context = {'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj, 'no_datasets': True}
        data_dict = {'user_obj': c.userobj}
        # self._setup_template_variables(context, data_dict)

        # transform the list to UI

        self.__setup_controller_parameter()

        return render('catalog/dashboard_catalog.html')

    def generate_doi(self, uri=None):
        """
        Assign a DOI to a catalog
        :param context:
        :return: a new generated doi
        """
        publisher = request.POST.get("publisher")
        uri = request.POST.get("uri")
        try:
            doi = doi_facade.DOIFacade(constants.DOI_CONFIG)
            orgs = ckanext_helpers.get_organization({"id": publisher})
            if orgs:
                if uri is not None:
                    return doi.generate_doi(orgs[0], uri)
                else:
                    return doi.generate_doi(orgs[0])
        except Exception as e:
            log.error("Error while generating doi")
            log.error(traceback.print_exc())

    def get_citation(self, id, style, language='en'):
        uri_prefix = '{0}/{1}'.format(config.get('ckan.ecodp.uri_prefix'), 'catalog')
        name_or_id = ''
        name_or_id = '{0}/{1}'.format(uri_prefix, id)
        context = {'user': c.user, 'for_view': True }
        get_action('catalogue_show')(context, {'uri': name_or_id})
        catalog = catalog = context.get('catalogue')
        catalog_dict = self._transform_catalog_schema_to_ui_schema(catalog)

        doi_str = catalog_dict.get('doi', '')
        language = request.GET.get("language") or language
        return ui_util.download_citation(doi_str, style, language)
