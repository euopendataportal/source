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
import urlparse
import sqlalchemy
import cPickle as pickle
import re

import pylons.config as config
import ujson as json

import ckan.lib.navl.dictization_functions
import ckanext.ecportal.helpers as helpers
from ckan.lib.base import model
import ckan.plugins as plugins
import ckan.model as model
import ckan.plugins.toolkit as tk
import ckanext.ecportal.lib.ui_util as ui_util

from ckan.lib.search.common import  SearchError, SearchQueryError
from ckanext.ecportal.lib.search.solr_search import SchemaSearchQuery


from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp, SchemaGeneric, DatasetSchemaDcatApOp, ResourceValue
from odp_common import RESOURCE_TYPE_VISUALIZATION

log = logging.getLogger(__name__)
_validate = ckan.lib.navl.dictization_functions.validate
_and_ = sqlalchemy.and_
_or_ = sqlalchemy.or_

QUERY_FIELDS = "name^4 title^4 tags^2 groups^2 text"
REMOVAL_TERMS = ['AND', 'OR', 'and', 'or', '&&', '||']

def _vocabularies(tag_name):
    '''
    Return a list containing the names of each vocabulary that
    contains the tag tag_name.

    Returns an empty list if tag_name does not belong to any vocabulary.

    If no such tag exists, throws a ckan.plugins.toolkit.ObjectNotFound
    exception.
    '''
    query = model.Session.query(model.tag.Tag.name,
                                model.vocabulary.Vocabulary.name)\
        .filter(model.tag.Tag.name == tag_name)\
        .filter(model.tag.Tag.vocabulary_id == model.vocabulary.Vocabulary.id)
    return [t[1] for t in query]

def _get_filename_and_extension(resource):
    url = resource.get('url').rstrip('/')
    if '?' in url:
        return '', ''
    if 'URL' in url:
        return '', ''
    url = urlparse.urlparse(url).path
    split = url.split('/')
    last_part = split[-1]
    ending = last_part.split('.')[-1].lower()
    if len(ending) in [2, 3, 4] and len(last_part) > 4 and len(split) > 1:
        return last_part, ending
    return '', ''

def _change_resource_details(resource):
    formats = helpers.resource_mapping().keys()
    resource_format = resource.get('format', '').lower().lstrip('.')
    filename, extension = _get_filename_and_extension(resource)
    if not resource_format:
        resource_format = extension
    if resource_format in formats:
        resource['format'] = helpers.resource_mapping()[resource_format][0]
        if resource.get('name', '') in ['Unnamed resource', '', None] and resource.get('description', '') in ['', None]:
            resource['name'] = helpers.resource_mapping()[resource_format][2]
    elif resource.get('name', '') in ['Unnamed resource', '', None] and resource.get('description', '') in ['', None]:
        if extension and not resource_format:
            if extension in formats:
                resource['format'] = helpers.resource_mapping()[extension][0]
            else:
                resource['format'] = extension.upper()
        resource['name'] = 'Web Page'

    if filename and not resource.get('description'):
        resource['description'] = filename



class ECPortalDatasetController(plugins.SingletonPlugin):
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IRoutes, inherit=True)

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def after_show(self, context, pkg_dict):


        def order_key(resource):
            return resource.get('name', resource.get('description', ''))

        if 'resources' in pkg_dict:
            pkg_dict['resources'].sort(key=order_key)

        for resource in pkg_dict.get('resources', {}):
            _change_resource_details(resource)
        return pkg_dict

    def before_search(self, search_params):
        raw_fq = search_params.get('fq', '')
        # check against solr fields and rasie exception for wrong fields
        # to avoid server error
        # http://10.2.0.113:8983/solr/admin/luke?numTerms=0
        slr = SchemaSearchQuery()
        field_list = slr.run()
        matcher_list = list(re.finditer(r"\w+:(?:(?!( \+?\w+:)).)+", raw_fq))
        # pa_li = matcher.search(str(raw_fq))
        # for param in pa_li.groups():
        #     field = param.split(":",1)


        for matcher in matcher_list:
            query_param = matcher.group(0)
            query_param_list = query_param.split(":",1)
            param = query_param_list[0]
            # if param not in field_list and param not in ['+dataset_type', 'groups']:
            #    raise SearchError('Unknowen field: {0}'.format(param))

        return search_params


    def after_search(self, search_results, search_params):
        """
        Used to adjust and update values of the dataset dict after a search.
        :param search_results:
        :param search_params:
        :return:
        """
        # adjust the value of id from the uri value
        if 'groups' in search_results:
            list_groups = search_results.get("groups",{})
            for group in list_groups:
                list_docs = list_groups.get(group).get("doclist",{}).get("docs",[])
                for doc in list_docs:
                    if 'id' in doc:
                        uri = doc['id']
                        doc['id'] = uri.split("/")[-1]

        for ds in search_results['results']:
            if 'rdf' in ds or 'id' not in ds:
                continue
            uri = ds.get('id')
            ds['id'] = uri.split('/')[-1]
            ds['tracking_summary'] = ds.get('views_total','')
            ds['viz_resources'] = [r for r in ds.get('resources', []) if r.get('resource_type','') == RESOURCE_TYPE_VISUALIZATION]
        return search_results

    def before_index(self, pkg_dict):
        '''

        :param DatasetDcatApOp pkg_dict:
        :return:
        '''
        # save a validated version of the package dict in the search index
        result_dict = {}
        result_dict['resource_list'] = []
        result_dict['resources_accessed_total'] = 0
        for resource in pkg_dict.schema.distribution_dcat.itervalues():
                result_dict['resources_accessed_total'] += int(ui_util._get_translated_term_from_dcat_object(resource, 'numberOfDownloads_dcatapop', 'en') or '0')


        resource_list = []
        for value in [ ui_util._transform_resources_to_ui_schema(res, 'en') for res in pkg_dict.schema.distribution_dcat.values()]:
            value['is_open'] = True
            resource_list.append(json.dumps(value ))

        for value in [ ui_util._transform_resources_page_foaf_to_ui_schema(res, 'en') for res in pkg_dict.schema.page_foaf.values()]:
            value['is_open'] = True
            resource_list.append(json.dumps(value ))

        result_dict['resource_list'] = resource_list

        return result_dict

    def before_map(self, m):
        # Edit resources for package
        m.connect('/dataset/editresources/{id}', controller= 'ckanext.ecportal.controllers.resources:ECPortalEditResourceController', action ='editresources')
        m.connect('/_download_count', controller= 'ckanext.ecportal.controllers.resources:ECPortalEditResourceController', action ='download_ressource')
        return m

    def before_view(self, pkg_dict):
        # To add the download total to the package object, we need to retrieve it via the tracking summary method.
        pkg_id = pkg_dict.get('name',None)
        # only if we have a valid pkg_id
        if pkg_id != None:
            # returns 0 in total if no value is there so, we don't care if the value is missing
            input_list = [] #[int(resource.get('download_total_resource', '0') or '0') for resource in pkg_dict.get('resources',[])]
            for resource in pkg_dict.get('resources',[]):
                value = resource.get('download_total_resource', '0') or '0'
                if not isinstance(value, list):
                    count = int(value)
                    input_list.append(count)
            if not input_list:
                input_list = [0]
            download_count = reduce(lambda x, y: x + y, input_list)
            pkg_dict['download_total'] = download_count

        if not pkg_dict.get('tracking_summary'):
            pkg_dict['tracking_summary'] = model.TrackingSummary.get_for_package(pkg_dict['uri'])

        return pkg_dict

    def after_create(self, context, data):
        '''
        This function is present only to prevent errors in case it is called and not present.
        Currently, there is nothing it could do.
        '''
        pass

    def after_update(self, context, data):
        '''
        This function is present only to prevent errors in case it is called and not present.
        Currently, there is nothing it could do.
        '''
        pass

    def after_delete(self, context, data):
        '''
        This function is present only to prevent errors in case it is called and not present.
        Currently, there is nothing it could do.
        '''
        #TODO implement purge after delete here:
        # purge data in steps:
        # history, resource, dataset
        pass


class ECPortalResourcePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceController)

    def before_show(self, resource_dict):

        return resource_dict
