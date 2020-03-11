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
#import json
import sqlalchemy.exc
import cPickle as pickle
import re


import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.config.routing as routing
#import ckanext.multilingual.plugin as multilingual

import ckanext.ecportal.action.skos as skos
import ckanext.ecportal.action.resource_term_translation as resource_term_translation
import ckanext.ecportal.logic as ecportal_logic
import ckanext.ecportal.auth as ecportal_auth
import ckanext.ecportal.searchcloud as searchcloud
import ckanext.ecportal.helpers as helpers
import ckanext.ecportal.unicode_sort as unicode_sort
import ckanext.ecportal.action.customsearch as customsearch
import ckanext.ecportal.action.ecportal_validation as validation
import ckanext.ecportal.action.selected_datasets_storage as selected_datasets_storage
import ckanext.ecportal.action.ingestion as ingestion
import ckanext.ecportal.action.ecportal_get as ecportal_get
import ckanext.ecportal.action.ecportal_update as ecportal_update
import ckanext.ecportal.action.ecportal_create as ecportal_create
import ckanext.ecportal.action.ecportal_delete as ecportal_delete
import ckanext.ecportal.action.auth.ecodp_get as ecportal_get_auth
import ckanext.ecportal.action.revision as ecportal_revision
import ckanext.ecportal.lib.ui_util as ui_util
from ckanext.ecportal.action import ecportal_save
import ckanext.ecportal.action.auth.ecodp_create as ecodp_create_auth
import ckanext.ecportal.action.auth.ecodp_update as ecodp_update_auth

OPENNESS_CONTROLLER = 'ckanext.ecportal.controllers.openness:ECPORTALOpennessController'
PACKAGE_CONTROLLER = 'ckanext.ecportal.controllers.package:ECPORTALPackageController'
GROUP_CONTROLLER = 'ckanext.ecportal.controllers.group:ECODPGroupController'
FEEDS_CONTROLLER = 'ckanext.ecportal.controllers.feeds:ECPortalFeedsController'
HOME_CONTROLLER = 'ckanext.ecportal.controllers.home:ECODPHomeController'
SEARCH_CLOUD_CONTROLLER = 'ckanext.ecportal.controllers.searchcloud:ECPortalSearchCloudAdminController'
ORGANIZATION_CONTROLLER = 'ckanext.ecportal.controllers.organization:ECODPOrganizationController'
CONFIGURATION_CONTROLLER = 'ckanext.ecportal.controllers.configuration:ECPORTALConfiguration'
INGESTION_PACKAGE_CONTROLLER = 'ckanext.ecportal.controllers.ingestion_package:ECPortalIngestion_PackageController'
USER_CONTROLLER = 'ckanext.ecportal.controllers.user:ECPortalUserController'
REVISION_CONTROLLER = 'ckanext.ecportal.controllers.revision:ECODPRevisionController'
TRACKING_CONTROLLER = 'ckanext.ecportal.controllers.tracking:ECODPTrackingController'
CATALOG_CONTROLLER = 'ckanext.ecportal.controllers.catalog:ECPORTALCatalogController'
API_CONTROLLER = 'ckanext.ecportal.controllers.ecodp_api:ECPORTALApiController'
STATS_CONTROLLER = 'ckanext.ecportal.controllers.ecodp_stats:ECODPStatsController'

ODP_CONTROLLERS = [OPENNESS_CONTROLLER, PACKAGE_CONTROLLER, GROUP_CONTROLLER, FEEDS_CONTROLLER,
                   HOME_CONTROLLER, SEARCH_CLOUD_CONTROLLER, ORGANIZATION_CONTROLLER, CONFIGURATION_CONTROLLER,
                   INGESTION_PACKAGE_CONTROLLER, USER_CONTROLLER, CATALOG_CONTROLLER]

log = logging.getLogger(__file__)
UNICODE_SORT = unicode_sort.UNICODE_SORT

LANGS = ['en', 'fr', 'de', 'it', 'es', 'pl', 'ga', 'lv', 'bg',
         'lt', 'cs', 'da', 'nl', 'et', 'fi', 'el', 'hu', 'mt',
         'pt', 'ro', 'sk', 'sl', 'sv', 'hr']

KEYS_TO_IGNORE = ['state', 'revision_id', 'id',  # title done seperately
                  'metadata_created', 'metadata_modified', 'site_id',
                  'data_dict', 'rdf']


class ECPortalPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)

    def get_auth_functions(self):
        return {
            'package_update': ecportal_auth.package_update,
            'package_revision_list': ecportal_get_auth.package_revision_list,
            'show_dataset_edit_button': ecportal_auth.show_package_edit_button,
            'package_search_private_datasets':
                ecportal_auth.package_search_private_datasets,
            'group_create': ecportal_auth.group_create,
            'user_create': ecportal_auth.user_create,
            'purge_publisher_datasets': ecportal_auth.purge_publisher_datasets,
            'purge_revision_history': ecportal_auth.purge_revision_history,
            'purge_package_extra_revision':
                ecportal_auth.purge_revision_history,
            #'purge_task_data': ecportal_auth.purge_task_data,
            'openness': ecportal_auth.openness
        }

    def get_actions(self):
        return {
            'organization_list': ecportal_logic.organization_list,
            'purge_publisher_datasets':	ecportal_logic.purge_publisher_datasets,
            'purge_revision_history': ecportal_logic.purge_revision_history,
            'purge_package_extra_revision':
                ecportal_logic.purge_package_extra_revision,
            'purge_task_data': ecportal_logic.purge_task_data,
            'user_create': ecportal_logic.user_create,
            'user_update': ecportal_logic.user_update,
            # 'package_show': ecportal_logic.package_show,
            # 'package_show_unaltered': ecportal_logic.package_show_unaltered,
            #'resource_show': ecportal_logic.resource_show,
            'vocabulary_show_without_package_detail':ecportal_logic.vocabulary_show_without_package_detail,
            'tag_dictize_without_package_detail':ecportal_logic.tag_dictize_without_package_detail,
            'domain_list': ecportal_logic.domain_list,
            'group_list': ecportal_logic.group_list,
            'next_group_list': ecportal_logic.next_group_list,
            'skos_hierarchy_update': ecportal_logic.skos_hierarchy_update,
            'get_skos_hierarchy': skos.get_skos_hierarchy,
            'custom_package_search': customsearch.custom_package_search,
            'check_solr_result':customsearch.check_solr_result,
            'resource_term_translation_create' : resource_term_translation.resource_term_translation_create,
            'resource_term_translation_create_multiple' : resource_term_translation.resource_term_translation_create_multiple,
            'get_langs_for_resource' : resource_term_translation.get_langs_for_resource,
            'get_translated_field' : resource_term_translation.get_translated_field,
            'get_resources_with_translation' : resource_term_translation.get_resources_with_translation,
            'is_multi_languaged_resource' : resource_term_translation.is_multi_languaged_resource,
            'package_owner_org_update' : ecportal_update.package_owner_org_update,
            'group_show_read': ecportal_get.group_show_read

            #'validate_dataset': validation.validate_dataset
        }


    def update_config(self, config):
        tk.add_template_directory(config, 'theme/templates')
        tk.add_public_directory(config, 'theme/public')
        tk.add_resource('theme/public', 'ecportal')

        # ECPortal should use group auth
        config['ckan.auth.profile'] = 'publisher'

    def before_map(self, map):
        '''
        Method used to add mappings used by this plugin.
        Things given here OVERRIDE the possibly existent config from the core (ckan/config/routing.py)

        :param map:
        :return:
        '''

        with routing.SubMapper(map, controller=ORGANIZATION_CONTROLLER) as m:
            m.connect('publishers_index', '/publisher', action='index')
            m.connect('/publisher/list', action='list')
            m.connect('/publisher/broken_links', action='broken_links')
            m.connect('/publisher/get_broken_links', action='get_broken_links')
            m.connect('/publisher/new', action='new')
            m.connect('publisher_read', '/publisher/{id}', action='read')
            m.connect('publisher_read', '/publisher/{id}', action='read',
                      ckan_icon='sitemap')

        with routing.SubMapper(map, controller='organization') as m:

            m.connect('/publisher/list', action='list')
            #deactivate manual creation of publisher
            #m.connect('/publisher/new', action='new')
            m.connect('/publisher/{action}/{id}',
                      requirements=dict(action='|'.join([
                          'delete',
                          'admins',
                          'member_new',
                          'member_delete',
                          'history'
                      ])))
            m.connect('publisher_activity', '/publisher/activity/{id}',
                      action='activity', ckan_icon='time')
            #m.connect('publisher_read', '/publisher/{id}', action='read')
            m.connect('publisher_about', '/publisher/about/{id}',
                      action='about', ckan_icon='info-sign')
            #m.connect('publisher_read', '/publisher/{id}', action='read',
            #          ckan_icon='sitemap')
            #deactivvate manual edit of publisher
            m.connect('publisher_edit', '/publisher/edit/{id}',
                      action='edit', ckan_icon='edit')
            #m.connect('publisher_edit',
             #         action='edit', ckan_icon='edit')

            m.connect('publisher_members', '/publisher/members/{id}',
                      action='members', ckan_icon='group')
            m.connect('publisher_bulk_process',
                      '/publisher/bulk_process/{id}',
                      action='bulk_process', ckan_icon='sitemap')

        # disable user list, password reset and user registration pages
        map.redirect('/user', '/not_found')
        map.redirect('/user/reset', '/not_found')
        map.redirect('/user/register', '/not_found')
        # Skip the logout screen
        map.redirect('/user/logged_out_redirect', '/')

        # disable dataset history page
        # map.redirect('/dataset/history/{url:.*}', '/not_found')
        map.redirect('/dataset/history_ajax/{url:.*}', '/not_found')

        map.redirect('/organization', '/publisher')
        map.redirect('/organization/{url:.*}', '/publisher/{url:.*}')

        # redirect for dashboard
        map.redirect('/dashboard', '/dashboard/datasets')

        # search cloud map
        with routing.SubMapper(map, controller=SEARCH_CLOUD_CONTROLLER) as m:
            m.connect('/searchcloud', action='index')
            m.connect('/searchcloud/', action='index')
            m.connect('/searchcloud/{action}')

        # search index home page
        with routing.SubMapper(map, controller=HOME_CONTROLLER) as m:
            m.connect('/', action='index')

        # feeds ECPORTAL
        # Override the /feeds/ routings (from the core) which need to be adapted
        with routing.SubMapper(map, controller=FEEDS_CONTROLLER) as m:
            m.connect('/feeds/custom.atom', action='custom')
            m.connect('/feeds/group/{id}.atom', action='group')
            m.connect('/dataset/history/{id}', action='history')
            m.connect('/dataset/history/{id}', action='history')

        # changing group search
        with routing.SubMapper(map, controller=GROUP_CONTROLLER) as m:
            m.connect('group_index', '/group', action='index',
                  highlight_actions='index search')
            m.connect('group_list', '/group/list', action='list')
            m.connect('/group/new', action='new')
            m.connect('/group/{id}', action='read')
            m.connect('group_edit', '/group/edit/{id}', action='edit',
                  ckan_icon='edit')
            #m.connect('/dataset/history/{id}', action='history')

        with routing.SubMapper(map, controller=PACKAGE_CONTROLLER) as m:
            m.connect( '/dataset', action ='search')
            #m.submapper( controller='package')

        with routing.SubMapper(map, controller=OPENNESS_CONTROLLER) as m:
            m.connect('/openness', action='publisher_list')
            m.connect('/openness/{id}', action='dataset_list')
            m.connect('/global_report', action='global_export')
            m.connect('/publisher_report', action='publisher_export')

        return map

    def after_map(self, map):
        return map

    def before_search(self, search_params):
        # search_string = search_params.get('q') or ''
        #
        # # for search cloud we don't make any changes to the search_params,
        # # just log the search string to the database for later analysis.
        #
        # # do some clean up of the search string so that the analysis
        # # will be easier later
        # search_string = searchcloud.unify_terms(search_string, max_length=200)
        # if not search_string:
        #     return search_params
        # lang = str(helpers.current_locale())
        # try:
        #     # Unfortunately a nested session doesn't behave the way we want,
        #     # failing to actually commit the change made.
        #     # We can either create a separate connection for this
        #     # functionality on each request (potentially costly),
        #     # or just commit at this point on the basis that for a search
        #     # request, no changes that can't be committed will have been
        #     # saved to the database. For now, we choose the latter.
        #     # # model.Session.begin_nested() # establish a savepoint
        #     searchcloud.track_term(model.Session, lang, search_string)
        # except sqlalchemy.exc.ProgrammingError, e:
        #     # We don't want the non-existence of the search_query table to
        #     # crash searches, we just won't log queries
        #     log.error(e)
        #     if 'relation "search_query" does not exist' in str(e):
        #         log.error('Please run the paster searchcloud-install-tables '
        #                   'command to set up the correct tables for '
        #                   'search logging')
        #         model.Session.rollback()
        #     else:
        #         raise
        # except Exception, e:
        #     # Exceptions from here don't appear to bubble up, so we make sure
        #     # to log them so that someone debugging a problem has a chance to
        #     # find the source error.
        #     log.error(e)
        #     raise
        # else:
        #     model.Session.commit()
        #     log.debug(
        #         'Inserted the term %r into the search_query table'
        #         ' and committed successfully',
        #         search_string
        #     )

        return search_params

    def before_index(self, pkg_dict):
        title = ui_util._get_translated_term_from_dcat_object(pkg_dict.schema, 'title_dcterms', 'en')
        # Strip accents first and if equivalant do next stage comparison.
        # Leaving space and concatenating is to avoid having todo a real
        # 2 level sort.
        result_dict = {}
        result_dict['title_sort'] = (unicode_sort.strip_accents(title) +
                                  '   '
                                  + title).translate(UNICODE_SORT)

        # set 'metadata_modified' field to value of metadata_modified if
        # not present (this field is used to sort datasets according to
        # their last update date).
        if not 'modified_date' in result_dict:
            import datetime
            modified_date = datetime.datetime.now().isoformat()
            try:
                modified_date = helpers.ecportal_date_to_iso(
                    ui_util._get_translated_term_from_dcat_object(pkg_dict.schema_catalog_record,
                                                                  'modified_dcterms', 'en'))
            except BaseException as e:
                log.error("[Indexation before index] [Failed] []use current date as fallback")
            result_dict['modified_date'] = modified_date

        if re.search(r".*T.*Z$", result_dict['modified_date']):
            pass # date format OK (verified with basic check)
        elif result_dict['modified_date']:
            # modify dates (SOLR is quite picky with dates, and only accepts
            # ISO dates with UTC time (i.e trailing Z)
            result_dict['modified_date'] = helpers.ecportal_date_to_iso(result_dict['modified_date']) + 'Z'
        else:
            result_dict.pop('modified_date',None)

        # def change_format(format):
        #     if format in helpers.resource_mapping():
        #         format = helpers.resource_mapping()[format][1]
        #     return format
        #
        # pkg_dict['res_format'] = [change_format(format) for format in
        #                           pkg_dict.get('res_format', [])]

        return result_dict

    def get_helpers(self):
        '''Register the most_popular_groups() function above as a template helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'current_locale': helpers.current_locale,
                'current_locale_bcp47': helpers.current_locale_bcp47,
                'current_url': helpers.current_url,
                'root_url': helpers.root_url,
                'filter_keywords_no_voc_id': helpers.filter_keywords_no_voc_id,
                'get_keywords_name': helpers.get_keywords_name,
                'get_viz_resources':helpers.get_viz_resources,
                'is_viz_resource':helpers.is_viz_resource,
                'is_non_doc_resource': helpers.is_non_doc_resource,
                'get_non_viz_resources':helpers.get_non_viz_resources,
                'get_non_viz_resources2': helpers.get_non_viz_resources2,
                'get_doc_resources': helpers.get_doc_resources,
                'is_web_page_resource': helpers.is_web_page_resource,
                'domain_render_link_list': helpers.domain_render_link_list,
                'domain_render_link_search': helpers.domain_render_link_search,
                'group_render_link_list': helpers.group_render_link_list,
                'resource_display_format': helpers.resource_display_format,
                'format_display_name': helpers.format_display_name,
                'resource_mapping': helpers.resource_mapping,
                'resource_mapping_json': helpers.resource_mapping_json,
                'group_facets_by_field': helpers.group_facets_by_field,
                'get_selected_facets_translation': helpers.get_selected_facets_translation,
                'get_facet_title': helpers.get_facet_title,
                'search_url_params': helpers.search_url_params,
                'dataset_resource_formats': helpers.dataset_resource_formats,
                'list_tags': helpers.list_tags,
                'most_viewed_datasets': helpers.most_viewed_datasets,
                'recent_updates': helpers.recent_updates,
                'approved_search_terms': helpers.approved_search_terms,
                'ecportal_date_to_iso': helpers.ecportal_date_to_iso,
                'top_publishers': helpers.top_publishers,
                'organizations_available': helpers.organizations_available,
                'sort_array': helpers.sort_array,
                'get_resources_num_res': helpers.get_resources_num_res,
                'names_from_tags': helpers.names_from_tags,
                'id_from_tags': helpers.id_from_tags,
                'starts_with_tel': helpers.starts_with_tel,
                'get_catalog_url': helpers.get_catalog_url,
                'get_dataset_url': helpers.get_dataset_url,
                'resource_dropdown': helpers.resource_dropdown,
                'resource_dropdown_list': helpers.resource_dropdown_list,
                'get_domain_id': helpers.get_domain_id,
                'get_extra_fields': helpers.get_extra_fields,
                'remove_url_param_for_group_read': helpers.remove_url_param_for_group_read,
                'add_url_param_for_group_read': helpers.add_url_param_for_group_read,
                'filter_groups_by_type': helpers.filter_groups_by_type,
                'is_sysadmin': helpers.is_sysadmin,
                'getSurveyLinkTarget': helpers.getSurveyLinkTarget,
                'unicode2string': helpers.unicode2string,
                'getExternalLinkURL' : helpers.getExternalLinkURL,
                'is_metadatatool_plugin_activated': helpers.is_metadatatool_plugin_activated,
                'get_available_locales': helpers.get_available_locales,
                'get_skos_hierarchy':helpers.get_skos_hierarchy,
                'get_last_word': helpers.get_last_word,
                'get_langs_for_resource': helpers.get_langs_for_resource,
                'get_translated_field': helpers.get_translated_field,
                'fallback_locale': helpers.fallback_locale,
                'get_english_resource_url' : helpers.get_english_resource_url,
                'is_multi_languaged_resource' : helpers.is_multi_languaged_resource,
                'get_random_number': helpers.get_random_number,
                'format_error_message': helpers.format_error_message,
                'format_error_message_for_ingestion_report': helpers.format_error_message_for_ingestion_report,
                'resources_type_list_from_resource_type' : helpers.resources_type_list_from_resource_type,
                'resources_type_name_from_resource_type' : helpers.resources_type_name_from_resource_type,
                'get_athorized_groups': helpers.get_athorized_groups,
                'correct_ATTO_message': helpers.correct_ATTO_message,
                'merge_error_dicts': helpers.merge_error_dicts,
                'get_count_dataset':helpers.get_count_dataset,
                'has_more_facets_' :helpers.has_more_facets_,
                'get_external_class':helpers.get_external_class,
                'get_new_uri_with_class':helpers.get_new_uri_with_class,
                'get_controller_category': helpers.get_controller_category,
                'get_value_from_config': helpers.get_value_from_config,
                'get_array_json_from_config': helpers.get_array_json_from_config,
                'has_accepted_cookies': helpers.has_accepted_cookies,
                'check_access': helpers.check_access,
                'translate_controlled_vocabulary': helpers.translate_controlled_vocabulary,
                'get_all_languages' : helpers.get_all_languages,
                'get_all_status' : helpers.get_all_status,
                'get_all_eurovoc_domains': helpers.get_all_eurovoc_domains,
                'get_all_formats' : helpers.get_all_formats,
                'get_all_licenses' : helpers.get_all_licenses,
                'ecportal_render_datetime': helpers.ecportal_render_datetime,
                'render_datetime': helpers.render_datetime_fix,
                'resource_display_name': helpers.resource_display_name,
                'resource_preview': helpers.resource_preview,
                'get_users_organizations_ids': helpers.get_users_organizations_ids,
                'load_json_ld': helpers.load_json_ld,
                'load_opoce_json_ld': helpers.load_opoce_json_ld,
                'load_breadcrumb_item_json_ld': helpers.load_breadcrumb_item_json_ld
                }


class RDFTPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)


    def update_config(self, config):
        tk.add_template_directory(config, 'theme/templates')
        tk.add_public_directory(config, 'theme/public')
        tk.add_resource('theme/public', 'ecportal')

        # ECPortal should use group auth
        config['ckan.auth.profile'] = 'publisher'

    def get_auth_functions(self):
        return {
            'dataset_show': ecportal_get_auth.package_show,
            'rdft_dataset_update': ecportal_auth.rdft_package_update,
            'catalog_create': ecodp_create_auth.catalog_create,
            'catalog_update': ecodp_update_auth.catalog_update
        }

    def get_actions(self):
        return {
            'validate_dataset': validation.validate_dataset,
            # 'change_selected_datasets': selected_datasets_storage.change_selected_datasets,
            # 'unselect_all_dataset': selected_datasets_storage.unselect_all_dataset,
            'ingest_package': ingestion.ingest_package,
            'legacy_package_show': ecportal_get.legacy_package_show,
            'package_show': ecportal_get.package_show,
            'package_search': ecportal_get.package_search,
            'package_update': ecportal_update.package_update,
            'package_save': ecportal_save.package_save,
            'package_create': ecportal_create.package_create,
            'publish_doi': ecportal_create.publish_doi,
            'assign_doi': ecportal_create.assign_doi,
            'package_delete': ecportal_delete.package_delete,
            'user_show':ecportal_get.user_show,
            'current_package_list_with_resources': ecportal_get.current_package_list_with_resources,
            'package_revision_list':ecportal_revision.package_revision_list,
            'resource_show':ecportal_get.resource_show,
            'legacy_term_translation_update_many':ecportal_update.term_translation_update_many,
            'term_translation_update_many':ecportal_update.dcat_term_translation_update_many,
            'theme_list': ecportal_get.theme_list,
            'vocabulary_list': ecportal_get.vocabulary_list,
            'tag_list': ecportal_get.tag_list,
            'package_list':ecportal_get.package_list,
            'group_show': ecportal_get.group_show,
            'catalogue_list': ecportal_get.catalogue_list,
            'catalogue_show': ecportal_get.catalogue_show,
            'package_show_rest': ecportal_get.package_show_rest,
            'organization_delete': ecportal_delete.organization_delete
        }

    def after_map(self, map):
        return map

    def before_map(self, map):
        '''
        Method used to add mappings used by this plugin.
        Things given here OVERRIDE the possibly existent config from the core (ckan/config/routing.py)

        :param map:
        :return:
        '''

        GET_POST = dict(method=['GET', 'POST'])
        # /api ver 3 or none
        with routing.SubMapper(map, controller=API_CONTROLLER, path_prefix='/api{ver:/3|}',
                       ver='/3') as m:
            m.connect('/action/{logic_function}', action='legacy_action',
                      conditions=GET_POST)

        with routing.SubMapper(map, controller=API_CONTROLLER, path_prefix='/apiodp',
                       ver='/4') as m:
            m.connect('/action/{logic_function}', action='action',
                      conditions=GET_POST)


        with routing.SubMapper(map, controller=PACKAGE_CONTROLLER) as m:
            # Introduce the dataste modification pages
            m.connect('/dataset/{action}/{id}/{revision}', action='read_ajax',
                  requirements=dict(action='|'.join([
                      'read',
                      'edit',
                      'history',
                  ])))
            m.connect('/dataset/{action}/{id}',
                  requirements=dict(action='|'.join([
                      'new_metadata',
                      'new_resource',
                      'history',
                      'read_ajax',
                      'history_ajax',
                      'follow',
                      'activity',
                      'groups',
                      'unfollow',
                      'delete',
                      'api_data',
                  ])))

            m.connect('search', '/dataset', action='search',
                  highlight_actions='index search')
            m.connect('/dataset/{id}/resource/{resource_id}', action='resource_read')
            m.connect('/dataset/new', action='new')
            m.connect('/dataset/{id}/resource/{resource_id}', action='resource_read')
            m.connect('/dataset/{id}.{format}', action='read')
            m.connect('/dataset/edit/{id}', action='update')
            m.connect('/dataset/validate', action='validate')
            m.connect('/dataset/validate_import_dataset', action='validate_import_dataset')
            m.connect('/dataset/import_selected_dataset_in_zip', action='import_selected_dataset_in_zip')
            m.connect('/dataset/export', action='export')
            m.connect('/dataset/bulk/delete', action='delete')
            m.connect('/dataset/bulk/privacy-state', action='change_privacy_state')
            m.connect('/dataset/bulk/edit', action='bulk_update')
            m.connect('/dataset/bulk/assign-doi', action='assign_doi')
            m.connect('/dataset/import', action='package_import')
            m.connect('/dataset/{id}', action='read')
            m.connect('/dataset/doi/generate', action="generate_doi", conditions=GET_POST)
            m.connect('/dataset/{id}/citation/{style}', action="get_citation")

        with routing.SubMapper(map, controller=USER_CONTROLLER) as m:
            # Override the dataset dashboard from the ECPortal extension
            m.connect('/dashboard/datasets', action='dashboard')
            m.connect('user_dashboard_groups', '/dashboard/groups',
                  action='dashboard_groups', ckan_icon='group')
            m.connect('user_dashboard_organizations', '/dashboard/organizations',
                  action='dashboard_organizations', ckan_icon='building')
            m.connect('/dashboard/{offset}', action='dashboard')
            m.connect('user_dashboard_datasets', '/dashboard/datasets', action='dashboard',
                      ckan_icon='sitemap')
            m.connect('login', '/user/login', action='login')
            m.connect('/user/_logout', action='logout')
            m.connect('/user/logged_in', action='logged_in')
            m.connect('/user/logged_out', action='logged_out')
            m.connect('/user/logged_out_redirect', action='logged_out_page')
            m.connect('user_datasets', '/user/{id}', action='read',
                      ckan_icon='sitemap')
            m.connect('user_contact_info', '/contact_info/{id}', action='read_contact_info',
                      ckan_icon='sitemap')

        with routing.SubMapper(map, controller=INGESTION_PACKAGE_CONTROLLER) as m:
            m.connect('/ingestion_package/manage_package', action='manage_package')
            m.connect('/ingestion_package/upload_package', action='upload_package')
            m.connect('/ingestion_package/create_ingestion_package', action='create_ingestion_package')
            m.connect('/ingestion_package/get_dataset_information', action='get_dataset_information')

        with routing.SubMapper(map, controller=CONFIGURATION_CONTROLLER) as m:
            # Override the dataset dashboard from the ECPortal extension
            m.connect('/configuration', action='vocabularies')
            m.connect('/configuration/validation', action='validationRules')


        with routing.SubMapper(map, controller= REVISION_CONTROLLER) as m:
            m.connect('/revision', action='index')


        with routing.SubMapper(map, controller= TRACKING_CONTROLLER) as m:
            m.connect('/_tracking', action='tracking')

        with routing.SubMapper(map, controller= CATALOG_CONTROLLER) as m:
            m.connect('/catalogue/new', action='new')
            m.connect('/catalogue/dashboard_catalogs', action='dashboard_catalogs')
            m.connect('/catalogue/edit/{id}', action='edit')
            m.connect('/catalogue/{id}', action='read')
            m.connect('/catalog/doi/generate', action="generate_doi", conditions=GET_POST)
            m.connect('/catalogue/{id}/citation/{style}', action="get_citation")

        with routing.SubMapper(map, controller= STATS_CONTROLLER) as m:
            m.connect('stats', '/stats', action='index')
            m.connect('stats_action', '/stats/{action}')

        return map

