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

import ckan.lib.navl.dictization_functions
import logging
import sqlalchemy
import os
import shutil
import csv
import time

import ckan.plugins.toolkit as tk
import pylons.config as config
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import cPickle as pickle
import ckanext.ecportal.lib.cache.redis_cache as cache
from ckanext.ecportal.virtuoso.utils_triplestore_query_helpers import TripleStoreQueryHelpers

import json
from sqlalchemy import func
from ckan.common import OrderedDict, _, request, c, g

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
_validate = ckan.lib.navl.dictization_functions.validate
_check_access = logic.check_access
_and_ = sqlalchemy.and_


class ECPORTALOpennessController(base.BaseController):
    def publisher_list(self):
        package_type = 'dataset'
        try:
            context = {'model': model, 'user': c.user or c.author,
                       'auth_user_obj': c.userobj}

            check_access('openness', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        c.pkg_dict = {}
        c.publishers = logic.get_action('organization_list')(context, {'all_fields': True})

        report = {}

        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        cache_key = 'global_openness:{0}'.format(locale)
        g_start_time = time.time()
        dict_string = cache.get_from_cache(cache_key, pool=cache.MISC_POOL)
        if dict_string:
            start_time = time.time()
            report = pickle.loads(dict_string)
            duration = time.time()-start_time
            log.info("Loading json took {0}".format(duration))
        else:
            osp_start  = time.time()
            rows = self._openness_sores_for_publisher()
            osp_duration = time.time()- osp_start
            log.info("_openness_sores_for_publisher took {0}".format(osp_duration))

            ps_start  = time.time()
            publishers = model.Group.all(group_type='organization')
            dict_pub = {}
            for publisher in publishers:
                dict_pub[publisher.name] = publisher

            for ds_name, obj in rows.iteritems():
                if not obj.get('owner_org'):
                    continue
                publisher = dict_pub.get(obj.get('owner_org').split('/')[-1].lower(),model.Group())
                #publisher = next((pub for pub in publishers if pub.name == model.Group.get(obj.get('owner_org').split('/')[-1].lower())),None)

                publ_report = report.get(publisher.name or publisher.id, {'publisher_name': publisher.title,
                                                                          'publisher_id': publisher.name or publisher.id,
                                                                          'zero': 0,
                                                                          'one': 0,
                                                                          'two': 0,
                                                                          'three': 0,
                                                                          'four': 0,
                                                                          'five': 0,
                                                                          'sum': 0,
                                                                          'avg': 0})

                column_key = self._set_dataset_score(obj['sum_value'])
                publ_report[column_key] += 1
                publ_report = self.calculate_sum(publ_report)
                publ_report = self.calculate_avg(publ_report)
                report[publisher.name] = publ_report


            #cache.set_value_in_cache(cache_key,pickle.dumps(report), pool=redis_cache.MISC_POOL)
            ps_duration = time.time()- ps_start
            log.info("publisher list 1st loop took {0}".format(ps_duration))

        totals = {'zero': 0,
              'one': 0,
              'two': 0,
              'three': 0,
              'four': 0,
              'five': 0}
        for publ, value in report.iteritems():
            totals['zero'] = value['zero'] + totals['zero']
            totals['one'] = value['one'] + totals['one']
            totals['two'] = value['two'] + totals['two']
            totals['three'] = value['three'] + totals['three']
            totals['four'] = value['four'] + totals['four']
            totals['five'] = value['five'] + totals['five']


        common_formats = self.get_format_summary_list()

        result = {}
        result['table'] = report
        result['totals'] = totals
        result['json'] = json.dumps(totals)
        result['common_formats'] = json.dumps(common_formats)

        c.pkg_dict = result

        self._setup_template_variables(context, {},
                                       package_type=package_type)
        g_duration = time.time()-g_start_time
        log.info("Global Loading took {0}".format(g_duration))
        # c.form = base.render(self._package_form(package_type='upload_package'), extra_vars=vars)
        return base.render('openness/publisher_list.html')

    def get_format_summary_list(self):
        ts_helper = TripleStoreQueryHelpers()

        raw_result = ts_helper.get_resource_formats()

        common_formats = {}
        for result in raw_result:
            key = result['format'] or 'No format'
            common_formats[key] = result['count']

        return common_formats


    def dataset_list(self, id):
        package_type = 'dataset'
        try:
            context = {'model': model, 'user': c.user or c.author,
                       'auth_user_obj': c.userobj}

            check_access('openness', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        publisher = model.Group.get(id)

        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        cache_key = 'global_openness:{0}:{1}'.format(locale, id)
        dict_string = cache.get_from_cache(cache_key, pool=cache.MISC_POOL)
        result = None
        if dict_string:
            start_time = time.time()
            result = pickle.loads(dict_string)
            duration = time.time()-start_time
            log.info("Loading json took {0}".format(duration))
        else:

            result = self._openness_sores_for_dataset(id)
            result['owner_org'] = publisher.id
            result['owner_org_name'] = publisher.name
            result['json'] = json.dumps(result['totals'])
            #cache.set_value_in_cache(cache_key,pickle.dumps(result), pool=redis_cache.MISC_POOL)

        c.pkg_dict = result

        c.publishers = logic.get_action('organization_list')(context, {'all_fields': True})

        self._setup_template_variables(context, {},
                                       package_type=package_type)
        # c.form = base.render(self._package_form(package_type='upload_package'), extra_vars=vars)
        return base.render('openness/dataset_list.html')

    def global_export(self):

        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        cache_key = 'global_export:{0}'.format(locale)
        dict_string = cache.get_from_cache(cache_key, pool=cache.MISC_POOL)
        data_list = None
        if dict_string:
            start_time = time.time()
            data_list = pickle.loads(dict_string)
            duration = time.time()-start_time
            log.info("Loading json took {0}".format(duration))
        else:


            query_string = '''select d.id, d.name, d.title, p.name, p.title, r.id, r.name, r.resource_type, r.url, r.format, r.mimetype, r.last_modified, r.size, tem.score, tem.reason
                        from package d join resource_group rg on d.id = rg.package_id join resource r on rg.id = r.resource_group_id join "group" p on d.owner_org = p.id
                        join (select sr.entity_id, sr.value as score, ds.value as reason from task_status sr join task_status ds on sr.entity_id = ds.entity_id	where sr.key = 'openness_score' and ds.key = 'openness_score_reason') tem on tem.entity_id = r.id
                        order by p.name, d.name'''
            rows = model.Session.execute(query_string)
            try:
                data_list = [{'dataset_id': (row[0] or '').encode('utf8'),
                              'dataset_name': (row[1] or '').encode('utf8'),
                              'dataset_title': (row[2] or '').encode('utf8'),
                              'publisher_name': (row[3] or '').encode('utf8'),
                              'publisher_title': (row[4] or '').encode('utf8'),
                              'resource_id': (row[5] or '').encode('utf8'),
                              'resource_name': (row[6] or '').encode('utf8'),
                              'resource_resource_type': (row[7] or '').encode('utf8'),
                              'resource_url': (row[8] or '').encode('utf8'),
                              'resource_format': (row[9] or '').encode('utf8'),
                              'resource_mimetype': (row[10] or '').encode('utf8'),
                              'resource_last_modidied': str(row[11]) or '',
                              'resource_size': row[12] or '',
                              'openness_score': row[13] or '',
                              'openness_reason': row[14] or '',} for row in rows]
                cache.set_value_in_cache(cache_key,pickle.dumps(data_list), pool=cache.MISC_POOL)
            except Exception, e:
                log.info('halt')

        name = ''
        if 'csv' in request.params:
            file, name = self._create_csv_file_from_list_of_dict(data_list)
            base.response.headers['Content-type'] = str('text/csv')
        elif 'json' in request.params:
            file, name = self._create_json_file_from_list_of_dict(data_list)
            base.response.headers['Content-type'] = str('application/json')
        try:
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(name)
            with open(name, 'r') as f:
                shutil.copyfileobj(f, base.response)
            base.response.headers['Content-Length'] = str(size)
            base.response.headers['Content-Disposition'] = str('attachment; filename="%s"' % name)

            return
        except Exception, e:
            abort(417, e.message)
        finally:
            os.remove(name)

    def publisher_export(self):

        publisher = request.params.get('publisher', '')

        locale = tk.request.environ['CKAN_LANG'] or config.get('ckan.locale_default', 'en')
        cache_key = 'global_export:{0}:{1}'.format(locale, publisher)
        dict_string = cache.get_from_cache(cache_key, pool=cache.MISC_POOL)
        result = None
        if dict_string:
            start_time = time.time()
            result = pickle.loads(dict_string)
            duration = time.time()-start_time
            log.info("Loading json took {0}".format(duration))
        else:

            query_string = '''select d.id, d.name, d.title, p.name, p.title, r.id, r.name, r.resource_type, r.url, r.format, r.mimetype, r.last_modified, r.size, tem.score, tem.reason
                        from package d join resource_group rg on d.id = rg.package_id join resource r on rg.id = r.resource_group_id join "group" p on d.owner_org = p.id
                        join (select sr.entity_id, sr.value as score, ds.value as reason from task_status sr join task_status ds on sr.entity_id = ds.entity_id	where sr.key = 'openness_score' and ds.key = 'openness_score_reason') tem on tem.entity_id = r.id
                        where p.name = '%s'
                        order by p.name, d.name  ''' % (publisher)
            rows = model.Session.execute(query_string)
            try:
                data_list = [{'dataset_id': (row[0] or '').encode('utf8'),
                              'dataset_name': (row[1] or '').encode('utf8'),
                              'dataset_title': (row[2] or '').encode('utf8'),
                              'publisher_name': (row[3] or '').encode('utf8'),
                              'publisher_title': (row[4] or '').encode('utf8'),
                              'resource_id': (row[5] or '').encode('utf8'),
                              'resource_name': (row[6] or '').encode('utf8'),
                              'resource_resource_type': (row[7] or '').encode('utf8'),
                              'resource_url': (row[8] or '').encode('utf8'),
                              'resource_format': (row[9] or '').encode('utf8'),
                              'resource_mimetype': (row[10] or '').encode('utf8'),
                              'resource_last_modidied': str(row[11]) or '',
                              'resource_size': row[12] or '',
                              'openness_score': row[13] or '',
                              'openness_reason': row[14] or '',} for row in rows]
                cache.set_value_in_cache(cache,pickle.dumps(data_list), pool=cache.MISC_POOL)
            except Exception, e:
                log.info('halt')

        name = ''
        if 'csv' in request.params:
            file, name = self._create_csv_file_from_list_of_dict(data_list)
        elif 'json' in request.params:
            file, name = self._create_json_file_from_list_of_dict(data_list)

        try:
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(name)
            with open(name, 'r') as f:
                shutil.copyfileobj(f, base.response)
            base.response.headers['Content-Length'] = str(size)
            base.response.headers['Content-Disposition'] = str('attachment; filename="%s"' % name)

            return
        except Exception, e:
            abort(417, e.message)
        finally:
            os.remove(name)

        return

    def _create_csv_file_from_list_of_dict(self, data_list):
        field_names = ['dataset_id',
                       'dataset_name',
                       'dataset_title',
                       'publisher_name',
                       'publisher_title',
                       'resource_id',
                       'resource_name',
                       'resource_resource_type',
                       'resource_url',
                       'resource_format',
                       'resource_mimetype',
                       'resource_last_modidied',
                       'resource_size',
                       'openness_score',
                       'openness_reason']
        file_name = 'openness_report.csv'

        with open(file_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writerow(dict((fn, fn) for fn in field_names))
            for item in data_list:
                writer.writerow(item)
        base.response.headers['Content-type'] = str('text/csv')
        return file, file_name

    def _create_json_file_from_list_of_dict(self, data_list):
        file_name = 'openness_report.json'
        with open(file_name, 'w') as jsonfile:
            jsonfile.write(json.dumps(data_list, sort_keys=True,
                                      indent=4, separators=(',', ': ')))

        base.response.headers['Content-type'] = str('application/json')
        return file, file_name

    def _openness_sores_for_publisher(self):

        ts_helper = TripleStoreQueryHelpers()
        # score = model.Session.execute('select DISTINCT sr.entity_id, sr.value as score, ds.value as reason from task_status sr	join task_status ds on sr.entity_id = ds.entity_id	where sr.key = :score and ds.key = :reason',{'score':'openness_score',
        #                                 'reason': 'openness_score_reason'})
        sc_start = time.time()
        query = model.Session.query(model.TaskStatus.entity_id,func.max(model.TaskStatus.value).label('value'))\
            .filter(model.TaskStatus.key == u'openness_score').group_by(model.TaskStatus.entity_id)

        result = query.distinct()
        sc_duration = time.time()-sc_start
        log.info("openness score query took {0}, {1} results".format(sc_duration, result.count()))

        sc_start = time.time()
        ts_data =ts_helper.get_resources_of_datasets()
        sc_duration = time.time()-sc_start
        log.info("ts data took {0}, {1} results".format(sc_duration, len(ts_data)))
        res_dict = {}
        sc_start = time.time()
        for row in result:
            #log.info(row)
            resource = ts_data.get(row[0],None)

            if resource and not res_dict.get(resource['dataset_name']):

                res_dict[resource['dataset_name']] = {'ds_title': resource['dataset_title'],
                                'resource_list': [{'rs_id': row[0],
                                                   'value': row[1]}],
                                 'sum_value': 0,
                                 'owner_org': resource['publisher']}
            elif resource:
                res_dict[resource['dataset_name']]['resource_list'].append({'rs_id': row[0],
                                                   'value': row[1]})
        sc_duration = time.time()-sc_start
        log.info("openness score query 1st loop took {0}, {1} results".format(sc_duration, len(res_dict)))
        sc_start = time.time()
        for ds in res_dict.values():

            ds['sum_value'] = str(reduce((lambda x, y: x+y), [int(rs['value']) for rs in  ds['resource_list']]) / len(ds['resource_list']))

        sc_duration = time.time()-sc_start
        log.info("openness score query 2nd loop took {0}".format(sc_duration))
        return res_dict

    def _openness_sores_for_dataset(self, group_id):
        ts_helper = TripleStoreQueryHelpers()
        ts_data =ts_helper.get_resources_of_datasets(publisher=group_id)


        result = {'table': [],
                  'totals': ''}
        totals = {'zero': 0,
                  'one': 0,
                  'two': 0,
                  'three': 0,
                  'four': 0,
                  'five': 0}

        #input_list = (x for x in ts_data if x.get('publisher').split('/')[-1].lower() == group_id)

        result_dict = {}
        for dataset in ts_data:
        #     if not result_dict.get(dataset['dataset_name']):
        #             result_dict[dataset['dataset_name']] = {'dataset_name':dataset['dataset_name'],
        #                                                     'package_title': dataset['dataset_title'],
        #                                                       'publisher': dataset['publisher'],
        #                                                     }
        #     else:
        #         continue
        #
        #
        # for key,value in result_dict.iteritems():

            score = model.Session.execute(
                "select DISTINCT sr.entity_id, sr.value as score, ds.value as reason from task_status sr	join task_status ds on sr.entity_id = ds.entity_id	where sr.key = :score and ds.key = :reason and sr.entity_id = :entity",
                {'entity': dataset['resource'].split('/')[-1],
                 'score': 'openness_score',
                 'reason': 'openness_score_reason'})

            for row in score:
                    tmp = {'package_name': dataset['dataset_name'],
                           'package_title': dataset['dataset_title'],
                           'score': row[1],
                           'reason': row[2]}
                    result['table'].append(tmp)
                    totals_key = self._set_dataset_score(row[1])
                    totals[totals_key] += 1
                    break



        result['totals'] = totals
        return result

    def _setup_template_variables(self, context, data_dict, package_type=None):
        return lookup_package_plugin(package_type).setup_template_variables(context, data_dict)

    def _package_form(self, package_type=None):
        log.debug(str(package_type) + " / " +
                  str(lookup_package_plugin(package_type)) + " / " +
                  str(lookup_package_plugin(package_type).package_form()))
        if package_type == 'ingestion_package':
            return 'user/manage_package_form.html'
        elif package_type == 'upload_package':
            return 'user/upload_package_form.html'

        return lookup_package_plugin(package_type).package_form()

    def _set_dataset_score(self, value):
        if '0' == value:
            return 'zero'
        elif '1' == value:
            return 'one'
        elif '2' == value:
            return 'two'
        elif '3' == value:
            return 'three'
        elif '4' == value:
            return 'four'
        elif '5' == value:
            return 'five'

    def calculate_sum(self, report_dict):
        report_dict['sum'] = report_dict['one'] + \
                             (report_dict['two'] * 2) + \
                             (report_dict['three'] * 3) + \
                             (report_dict['four'] * 4) + \
                             (report_dict['five'] * 5)

        return report_dict

    def calculate_avg(self, report_dict):

        star_sum = report_dict['one'] + \
                   report_dict['two'] + \
                   report_dict['three'] + \
                   report_dict['four'] + \
                   report_dict['five']

        report_dict['avg'] = report_dict['sum'] / star_sum if 0 != star_sum else 0
        return report_dict
