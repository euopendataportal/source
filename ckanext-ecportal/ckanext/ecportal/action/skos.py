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
import time

import ujson as json
from ordereddict import OrderedDict
import ckan.new_authz as auth
import ckanext.ecportal.lib.cache.redis_cache as cache

from ckanext.ecportal.virtuoso.utils_triplestore_query_helpers import TripleStoreQueryHelpers
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import CorporateBodiesUtil


KEYWORD = 0

log = logging.getLogger(__file__)

def get_skos_hierarchy(context,max_element=None):
    """

    :param context:
    :param max_element:
    :return:
    """
    result = OrderedDict()

    ts_query_helper = TripleStoreQueryHelpers()
    user = context.get('user',None)
    cache_key = ''
    if user:
        cache_key = 'skos_hierarchy_{0}'.format(user)
    else:
        cache_key = 'skos_hierarchy'
    dict_string=cache.get_from_cache(cache_key, pool=cache.MISC_POOL)
    if dict_string:
        start_time = time.time()
        result = json.loads(dict_string)
        duration = time.time()-start_time
        log.info("[DB] Loading json took {0}".format(duration))
    else:
        try:
            graph_list = []
            graph_list.append('dcatapop-public')
            start1 = time.time()
            package_count_public = ts_query_helper.get_package_count_by_publisher(graph_list)
            log.info('1st package count query took {0}s'.format(time.time()-start1))


            graph_list.append('dcatapop-private')
            start2 = time.time()
            packag_count_all = ts_query_helper.get_package_count_by_publisher(graph_list)
            log.info('2nd package count query took {0}s'.format(time.time()-start2))

            factory = ControlledVocabularyFactory()
            publ_mdr = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.CORPORATE_BODY) #type: CorporateBodiesUtil
            publ_hierarchie = publ_mdr.get_publisher_hierarchy()

            for top_level, children in publ_hierarchie.items():
                sum_count = 0
                pub_id = top_level.split('/')[-1].lower()
                if auth.has_user_permission_for_group_or_org(pub_id, user, 'read') :
                    sum_count += packag_count_all.get(top_level) or 0
                else:
                    sum_count += package_count_public.get(top_level) or 0
                interim = {'children': []}
                for child in children:
                    count = 0
                    pub_id = child.split('/')[-1].lower()
                    if auth.has_user_permission_for_group_or_org(pub_id, user, 'read') :
                        count += packag_count_all.get(child) or 0
                    else:
                        count += package_count_public.get(child) or 0
                    if count > 0:
                        interim['children'].append((child,count))
                        sum_count += count
                interim['total'] = sum_count
                result[top_level] = interim

            cache.set_value_in_cache(cache_key,json.dumps(result ), pool=cache.MISC_POOL)
        except Exception, e:
           log.error('Error during querying the groups in get_skos_hierarchy: %s' % e)
           import traceback
           log.error(traceback.print_exc())
           return {}

    return result