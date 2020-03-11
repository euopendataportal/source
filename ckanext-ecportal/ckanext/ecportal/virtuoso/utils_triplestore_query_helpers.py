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
import dateutil.parser
import traceback
import cPickle as pickle
import ckanext.ecportal.lib.cache.redis_cache as redis_cache

from ckanext.ecportal.virtuoso.utils_triplestore_crud_core import VirtuosoCRUDCore


log = logging.getLogger(__file__)


class TripleStoreQueryHelpers(VirtuosoCRUDCore):

    def get_package_count_by_publisher(self, graph_list):
        try:
            from_query = ''
            if graph_list:
                for graph in graph_list:
                    from_query += ' from <{0}> '.format(graph)

            select_query = "select (count(DISTINCT ?s) as ?count) ?pub {0} where {{?s ?p ?o . " \
                          "?s a <http://www.w3.org/ns/dcat#Dataset> . " \
                          "?s <http://purl.org/dc/terms/publisher> ?pub}} GROUP BY ?pub".format(from_query)
            result = self.execute_select_query_auth(select_query)
            if not result:
                return {}
            else:
                res = {}
                for package_count in result:
                    res[package_count.get('pub').get('value')] = int(package_count.get('count').get('value'))

                return res

        except BaseException as e:
            return False

    def get_uri_datasets(self, graph_name='<dcatapop-public>'):
       try:
            select_query = 'SELECT ?s FROM {0} where {{ {{?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/dcat#Dataset>}} }}'.format(graph_name)
            result = self.execute_select_query_auth(select_query)
            if not result:
                return []
            else:
                res = []
                for uri in result:
                    res.append(uri.get('s').get('value'))
                return res
       except BaseException as e:
           log.error("[TS Helper] [get list of URIs] [Failed]")
           log.error(traceback.print_exc(e))
           return False

    def get_resources_of_datasets(self, publisher='none', graph_name='<dcatapop-public>'):
        '''

        :param graph_name:
        :return: type list
        '''
        result = []
        try:
            str_res = redis_cache.get_from_cache('get_resources_of_datasets:{0}'.format(publisher), pool=redis_cache.MISC_POOL)
            if str_res:
                result = pickle.loads(str_res)
                return result
        except Exception as e:
            import traceback
            log.error('{0}'.format(e))
            log.error(traceback.print_exc())


        try:
            select_query = " select ?resource ?dataset_name ?dataset_title ?publisher from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://www.w3.org/ns/dcat#distribution> ?resource ." \
                           " ?ds <http://purl.org/dc/terms/title> ?dataset_title ." \
                           " ?ds <http://purl.org/dc/terms/publisher> ?publisher ." \
                           " ?ds <http://data.europa.eu/88u/ontology/dcatapop#ckanName> ?dataset_name" \
                           " filter (lang(?dataset_title) in ('en',''))" \
                           " }}" \
                           " union " \
                           " {{" \
                           "  ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds foaf:page ?resource ." \
                           " ?ds <http://purl.org/dc/terms/title> ?dataset_title ." \
                           " ?ds <http://data.europa.eu/88u/ontology/dcatapop#ckanName> ?dataset_name ." \
                           " ?ds <http://purl.org/dc/terms/publisher> ?publisher ." \
                           " filter (lang(?dataset_title) in ('en',''))" \
                           " }} }}".format(graph_name)


            result = self.execute_select_query_auth(select_query)
            list_final = None
            if publisher != 'none':
                list_final = []
                for res in result:
                    if res.get('publisher').get('value').split('/')[-1].lower() == publisher:
                        list_final.append({'dataset_name': res['dataset_name']['value'], 'dataset_title': res['dataset_title']['value'],
                         'resource': res['resource']['value'], 'publisher': res['publisher']['value']})
                #list_final =  (x for x in result if x.get('publisher').split('/')[-1].lower() == publisher)
            else:
                list_final = {}
                for res in result:
                    list_final[res['resource']['value'].split('/')[-1]] = {'dataset_name': res['dataset_name']['value'], 'dataset_title': res['dataset_title']['value'],
                         'resource': res['resource']['value'], 'publisher': res['publisher']['value']}
                    # list_final.append(
                    #     {'dataset_name': res['dataset_name']['value'], 'dataset_title': res['dataset_title']['value'],
                    #      'resource': res['resource']['value'], 'publisher': res['publisher']['value']})
            redis_cache.set_value_in_cache('get_resources_of_datasets:{0}'.format(publisher),pickle.dumps(list_final), 86400, pool=redis_cache.MISC_POOL)
            return list_final
        except BaseException as e:
            import traceback
            log.error('{0}'.format(e))
            log.error(traceback.print_exc())
            return None


    def get_resource_formats(self, graph_name='<dcatapop-public>'):

        query = 'select ?format (count(?format) as ?result) from {0} where {{' \
              ' ?rs <http://purl.org/dc/terms/format> ?format .' \
              ' }}' \
              ' GROUP  by ?format'.format(graph_name)

        try:
            result = self.execute_select_query_auth(query)
            list_final = []
            for res in result:
                list_final.append(
                    {'format': res['format']['value'],
                     'count': res['result']['value']})
            return list_final
        except BaseException as e:
            return None

    def get_dataset_ids_with_issued_date(self, graph_name='<dcatapop-public>'):

        select_query = " select ?dataset ?issued_date  from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#CatalogRecord> ." \
                           " ?ds <http://xmlns.com/foaf/0.1/primaryTopic> ?dataset ." \
                           " ?ds <http://purl.org/dc/terms/issued> ?issued_date ." \
                           " }} }} ORDER BY ASC(?issued_date)".format(graph_name)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            dataset_id = res.get('dataset',{}).get('value')
            date_string = res.get('issued_date',{}).get('value')
            date = dateutil.parser.parse(date_string)
            result_list.append((dataset_id,date))
            #log.debug(u'{0}'.format(result))
        return result_list

    def get_revision_ids_with_issued_date(self, graph_name='<dcatapop-revision>'):

        select_query = " select ?rv ?timestamp  from {0} where {{ " \
                           " {{ " \
                           " ?rv a  <http://data.europa.eu/88u/revision#> ." \
                           " ?rv <http://data.europa.eu/88u/revision#timestamp> ?timestamp ." \
                           " }} }} ORDER BY ASC(?timestamp)".format(graph_name)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            dataset_id = res.get('rv',{}).get('value')
            date_string = res.get('timestamp',{}).get('value')
            date = dateutil.parser.parse(date_string)
            result_list.append((dataset_id,date))
            #log.debug(u'{0}'.format(result))
        return result_list


    def get_revision_count_for_datastet(self, limit=10, graph_name='<dcatapop-revision>'):

        select_query = " select ?dataset count(?rv) as ?count from {0} where {{ " \
                           " {{ " \
                           " ?rv a  <http://data.europa.eu/88u/revision#> ." \
                           " ?rv <http://data.europa.eu/88u/revision#isRevisionOf> ?dataset ." \
                           " }} }} ORDER BY DESC(count(?rv)) LIMIT {1}".format(graph_name, limit)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            dataset_id = res.get('dataset',{}).get('value')
            count = res.get('count',{}).get('value')
            result_list.append((dataset_id,count))
            #log.debug(u'{0}'.format(result))
        return result_list


    def get_top_groups(self, limit=10, graph_name='<dcatapop-public>'):

        select_query = " select ?group count(?group) as ?count from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://data.europa.eu/88u/ontology/dcatapop#datasetGroup> ?group ." \
                           " }} }} ORDER BY DESC(count(?group)) LIMIT {1}".format(graph_name, limit)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            group_id = res.get('group',{}).get('value')
            count = res.get('count',{}).get('value')
            result_list.append((group_id,count))
            #log.debug(u'{0}'.format(result))
        return result_list


    def get_top_keywords(self, limit=10, graph_name='<dcatapop-public>'):

        select_query = " select ?key count(?key) as ?count from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://www.w3.org/ns/dcat#keyword> ?key ." \
                           " }} }} ORDER BY DESC(count(?key)) LIMIT {1}".format(graph_name, limit)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            group_id = u'{0}@{1}'.format(res.get('key',{}).get('value'), res.get('key',{}).get('xml:lang'))
            tag = res.get('key',{}).get('value')
            count = res.get('count',{}).get('value')
            result_list.append((group_id,tag, count))
            #log.debug(u'{0}'.format(result))
        return result_list

    def get_top_themes(self, limit=10, graph_name='<dcatapop-public>'):
        #import ckanext.ecportal.lib.controlled_vocabulary_util as mdr_util
        #from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary

        select_query = " select ?theme count(?theme) as ?count from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://www.w3.org/ns/dcat#theme> ?theme ." \
                           " }} }} ORDER BY DESC(count(?theme)) LIMIT {1}".format(graph_name, limit)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            group_id = res.get('theme',{}).get('value')

            count = res.get('count',{}).get('value')
            result_list.append((group_id,count))
            #log.debug(u'{0}'.format(result))
        return result_list


    def get_top_languages(self, limit=10, graph_name='<dcatapop-public>'):
        #import ckanext.ecportal.lib.controlled_vocabulary_util as mdr_util
        #from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary

        select_query = " select ?language count(?language) as ?count from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://purl.org/dc/terms/language> ?language ." \
                           " }} }} ORDER BY DESC(count(?language)) LIMIT {1}".format(graph_name, limit)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            group_id = res.get('language',{}).get('value')

            count = res.get('count',{}).get('value')
            result_list.append((group_id,count))
            #log.debug(u'{0}'.format(result))
        return result_list

    def get_top_countries(self, limit=10, graph_name='<dcatapop-public>'):
        #import ckanext.ecportal.lib.controlled_vocabulary_util as mdr_util
        #from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary

        select_query = " select ?spatial count(?spatial) as ?count from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://purl.org/dc/terms/spatial> ?spatial ." \
                           " }} }} ORDER BY DESC(count(?spatial)) LIMIT {1}".format(graph_name, limit)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            group_id = res.get('spatial',{}).get('value')

            count = res.get('count',{}).get('value')
            result_list.append((group_id,count))
            #log.debug(u'{0}'.format(result))
        return result_list

    def get_top_subjects(self, limit=10, graph_name='<dcatapop-public>'):
        #import ckanext.ecportal.lib.controlled_vocabulary_util as mdr_util
        #from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary

        select_query = " select ?subject count(?subject) as ?count from {0} where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://purl.org/dc/terms/subject> ?subject ." \
                           " }} }} ORDER BY DESC(count(?subject)) LIMIT {1}".format(graph_name, limit)

        result = self.execute_select_query_auth(select_query)

        result_list = []
        for res in result:
            group_id = res.get('subject',{}).get('value')

            count = res.get('count',{}).get('value')
            result_list.append((group_id,count))
            #log.debug(u'{0}'.format(result))
        return result_list


    def is_ckanName_unique(self, name, limit=10):
        #import ckanext.ecportal.lib.controlled_vocabulary_util as mdr_util
        #from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary

        select_query = ' select ?ds  from <dcatapop-public> from <dcatapop-private> where {{ ' \
                           ' {{ ' \
                           ' ?ds a  <http://www.w3.org/ns/dcat#Dataset> .' \
                           ' ?ds <http://data.europa.eu/88u/ontology/dcatapop#ckanName> "{0}" . ' \
                           ' }} }} LIMIT {1}'.format(name, limit)

        result = self.execute_select_query_auth(select_query)

        if not result:
            return True
        return False

    def is_DOI_unique(self, uri, limit=10):
        #import ckanext.ecportal.lib.controlled_vocabulary_util as mdr_util
        #from ckanext.ecportal.lib.controlled_vocabulary_util import Controlled_Vocabulary

        select_query = ' select ?ds  from <dcatapop-public> from <dcatapop-private> where {{ ' \
                           ' {{ ' \
                           ' ?ds a  <http://www.w3.org/ns/dcat#Dataset> .' \
                           ' ?ds <http://www.w3.org/ns/adms#identifier> ?id . ' \
                           ' ?id <http://www.w3.org/2004/02/skos/core#notation> ?doi . ' \
                           ' FILTER(DATATYPE(?doi) = <http://publications.europa.eu/resource/authority/notation-type/DOI> AND STR(?doi) = "{0}") ' \
                           ' }} }} LIMIT {1}'.format(uri, limit)

        result = self.execute_select_query_auth(select_query)

        if not result:
            return True
        return False

    def get_all_keywords(self, graph_name='dcatapop-public'):
        import uuid
        select_query = " select distinct ?key from <{0}> where {{ " \
                           " {{ " \
                           " ?ds a  <http://www.w3.org/ns/dcat#Dataset> ." \
                           " ?ds <http://www.w3.org/ns/dcat#keyword> ?key ." \
                           " }} }} ".format(graph_name)

        rew_result = self.execute_select_query_auth(select_query)

        result = {}
        for res in rew_result:
            value = res.get('key',{}).get('value')
            lang = res.get('key',{}).get('xml:lang')
            tag = res.get('key',{}).get('value')

            result[uuid.uuid4()] = value
            #log.debug(u'{0}'.format(result))
        return result