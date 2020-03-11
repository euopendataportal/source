# import pylons.config as config
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

# import time
# import redis
# import logging
# log = logging.getLogger()
#
# def _get_redis_connection():
#     try:
#         redis_host_url = config.get('ckan.cache.redis.server.url', 'localhost')
#         redis_host_port = config.get('ckan.cache.redis.server.port', 6379)
#         r = redis.StrictRedis(host=redis_host_url, port=redis_host_port, db=0)
#         return r
#     except:
#         log.info("ERROR REDIS: Connection ERROR")
#         return None
#
#
# def get_from_cache (cache_key):
#     # locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
#     active_cache = config.get('ckan.cache.active', 'true')
#     dict_string=None
#     try:
#         if active_cache == 'true':
#             r = _get_redis_connection()
#             # cache_key = 'recent_updates:{0}'.format(locale)
#             dict_string = r.get(cache_key)
#             if dict_string:
#                 log.info('REDIS Cache: Load {0} from the cache'.format(cache_key))
#     except:
#         log.info("ERROR REDIS: get from cache")
#         dict_string=None
#     return dict_string
#
# def set_value_in_cache(cache_key, value):
#     # locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
#     active_cache = config.get('ckan.cache.active', 'true')
#     try:
#         if active_cache == 'true':
#             redis_validity_time = config.get('ckan.cache.redis.validity.time',3600)
#             r = _get_redis_connection()
#             r.setex(cache_key, redis_validity_time, value)
#             log.info('REDIS Cache: Put the Variable Key: {0} in the cache'.format(cache_key))
#
#     except:
#         log.info("ERROR REDIS: set_value_in_cache")
#         pass
#
#
# def delete_variable_from_cache(cache_key):
#     active_cache = config.get('ckan.cache.active', 'true')
#     try:
#         if active_cache == 'true':
#             r= _get_redis_connection()
#             r.delete(cache_key)
#             log.info('REDIS Cache: Delete variable Key: {0} from the cache'.format(cache_key))
#
#     except:
#         log.info("ERROR REDIS: Delete variable : {0}".format(cache_key))
#         pass
# def get_count_cached_variables():
#     active_cache = config.get('ckan.cache.active', 'true')
#     try:
#         if active_cache == 'true':
#             r= _get_redis_connection()
#             list_keys = r.scan_iter("*")
#             count = sum (1 for i in list_keys)
#             log.info('REDIS Cache: count of cached variable')
#             return count
#
#     except:
#         log.info("ERROR REDIS: get count of variables")
#         return None
#         pass
# # set_value_in_cache("v1","1")
# # print get_from_cache("v1")
# # get_count_cached_variables()
# #
# # delete_variable_from_cache("v1")
# # print get_from_cache("v1")
# # get_count_cached_variables()
