# -*- coding: utf-8 -*-
#    Copyright (C) <2019>  <Publications Office of the European Union>
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

from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp, SchemaGeneric, ResourceValue, \
    RevisionSchemaDcatApOp, DistributionSchemaDcatApOp

import traceback
import logging

import ckan.logic as logic
import ckan.logic.action
import ckan.plugins as plugins
import ckan.model as model
from ckanext.ecportal.lib.search.dcat_index import PackageSearchIndex

import ckanext.ecportal.lib.cache.redis_cache as redis_cache

import pickle

package_index = PackageSearchIndex()

log = logging.getLogger(__file__)

from ckanext.ecportal.action.ecportal_save import update_exisiting_dataset


class DatasetUtils(object):
    '''
    A class to deal with some common actions on dataset.
    '''

    def rollback_dataset_to_revision(self, dataset_uri):
        """
        rollback the dataset to the selected revision
        :param dataset:
        :param revision_id:
        :return:
        """



        try:
            revision = self.get_first_valid_revision(dataset_uri=dataset_uri) or {}
            revision_dataset = revision.get('dataset', None)
            if revision_dataset:
                context = {"ignore_auth": True}
                result = update_exisiting_dataset(revision_dataset, None, context, {"uri": dataset_uri})
                if result:
                    log.info("[ROLLBACK Dataset] [Successful] [URI:<{0}>]".format(dataset_uri))
                else:
                    log.error("[ROLLBACK Dataset] [Failed] [Updating dataset][URI:<{0}>]".format(dataset_uri))
            else:
                # Remove dataset
                log.error("[ROLLBACK Dataset] [Revision None] [Try to delete Dataset][URI:<{0}>]".format(dataset_uri))
                try:
                    dataset_to_remove = DatasetDcatApOp(dataset_uri)
                    result = dataset_to_remove.get_description_from_ts()
                    if result:
                        dataset_to_remove.delete_from_ts()
                        log.info("[ROLLBACK Dataset] [Delete Dataset] [Successful] [URI:<{0}>]".format(dataset_uri))
                        redis_cache.delete_value_from_cache(dataset_to_remove.dataset_uri)
                        package_index.remove_dict(dataset_to_remove)
                except BaseException as e:
                    log.error(traceback.print_exc(e))
                    log.error("[ROLLBACK Dataset] [Delete dataset] [Failed] [URI:<{0}>]".format(dataset_uri))

        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error("[ROLLBACK Dataset] [Failed] [Revision None][URI:<{0}>]".format(dataset_uri))

    def get_first_valid_revision(self, dataset_uri):
        '''

        :param str dataset_uri:
        :return: DatasetDcatApOp
        '''
        try:
            dataset = DatasetDcatApOp(dataset_uri)
            list_revisions = dataset.get_list_revisions_ordred()
            revision_dataset = DatasetDcatApOp("")
            i = 0
            for revision in list_revisions:
                i = i + 1
                revision_dataset = revision.get("dataset")  # type:DatasetDcatApOp
                ckanName = ""
                try:
                    ckanName = revision_dataset.schema.ckanName_dcatapop.get('0', ResourceValue("")).value_or_uri
                    catalog_modified = revision_dataset.schema_catalog_record.modified_dcterms.get('0', ResourceValue(
                        '')).value_or_uri
                except:
                    ckanName = ""
                if ckanName and catalog_modified:
                    revision_schema = revision.get('revision')  # type:RevisionSchemaDcatApOp
                    revision_uri = revision_schema.uri
                    log.info(
                        "[Dataset] [Get Revision] [Find the first valid revision] [Successful] [datset URI:<{0}>] [Revision URI:<{1}>]".
                            format(dataset_uri, revision_uri))
                    return revision

            log.error("[Dataset] [Get Revision] [Find the first valid revision] [Failed] [datset URI:<{0}>]".
                      format(dataset_uri))
            # delete dataset


        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error("[Dataset] [Get Revision] [Can not get first valid revision] [URI:<{0}>]".format(dataset_uri))

    def create_dataset_from_rdf(self, rdf_xml):
        '''
        Create a dataset usig the RDF content
        :param rdf_xml:
        :return:
        '''

    def calculate_hash_code_from_publisher_uri(self, publisher_uri):
        '''
        Calculate the hash code of the publisher uri.
        We implement the algo of rdf2ckan
        To be used in the mapping between old ckan-name (local part of the ODP URI) and the ODP URI of the dataset.

        :param publisher_uri:
        :return:
        '''

        import hashlib
        import base64
        import re
        imput_string = publisher_uri
        md5_hash = hashlib.md5()
        md5_hash.update(imput_string.encode('utf-8'))
        md5_string = md5_hash.hexdigest()
        md5_byte = md5_hash.digest()
        base64_str = base64.standard_b64encode(md5_byte)
        base64_str = re.sub('[^a-zA-Z0-9]', "", base64_str)
        return base64_str

    def get_list_empty_datasets(self):
        # list_datasets = ["http://data.europa.eu/88u/dataset/cordisH2020projects"]
        from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers

        try:
            tsch = TripleStoreCRUDHelpers()

            sparql_query = """
            select  ?dataset from <dcatapop-public> where {
            ?dataset a <http://www.w3.org/ns/dcat#Dataset>.

            optional{
                ?cr <http://xmlns.com/foaf/0.1/primaryTopic> ?dataset .
                ?cr <http://purl.org/dc/terms/modified> ?o .
            }   
          filter (!bound(?o))
    }

    """
            result = tsch.execute_select_query_auth(sparql_query)
            list_datasets = [ds.get('dataset').get('value') for ds in result]

            return list_datasets
        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error('[Rollback Dataset] [get_list_empty_datasets] [Failed]')


    def rollback_empty_datasets(self):
        list_empty_datasets = self.get_list_empty_datasets()
        # list_empty_datasets = ["http://data.europa.eu/88u/dataset/490bc7b5-0947-46b5-96d0-e1f450ebb2f1"]

        try:
            for dataset_uri in list_empty_datasets:
                r = self.rollback_dataset_to_revision(dataset_uri)
        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error("[rollback_empty_datasets] [failed]")

    def load_dataset(self, dataset_uri):
        '''
        Load dataset from Triple store or the cache
        :return: type: DatasetDcatApOp
        '''

        dataset = None  # type: DatasetDcatApOp
        dataset_string = redis_cache.get_from_cache(dataset_uri, pool=redis_cache.MISC_POOL)
        if dataset_string:
            dataset = pickle.loads(dataset_string)
            log.info('[Dataset] [LOAD from cache] [URI:<{0}>]'.format(dataset_uri))

        if not dataset or not dataset.schema:
            dataset = DatasetDcatApOp(dataset_uri)
            loaded_from_public = dataset.get_description_from_ts()
            if not loaded_from_public:
                dataset.set_state_as_private()
                loaded_from_private = dataset.get_description_from_ts()
                log.info("[Dataset] [Load from private] [URI:<{0}>]".format(dataset_uri))

        return dataset

    def find_duplicated_datasets(self, path_file):
        """
        To find the duplicated datasets
        :param str path_file
        :return:
        """
        import json

        qparql_query = """


        """
        list_duplications = []
        import csv
        with open(path_file) as f:
            csv_reader = csv.reader(f, delimiter=',')
            for duplication in csv_reader:
                list_duplications.append({"old": duplication[0], "new": duplication[1]})

        # duplicated_datasetes = {"old_dataset_uri": "namespac/barca", "new_dataset_uri": "namespace/alge_$setif"}
        # list_duplications = [duplicated_datasetes]

        return list_duplications

    def update_statistics_of_duplicated_datasets(self, file_duplication=""):
        """
        Update the statistics of the new duplicated dataset.
        :param str old_dataset_uri:
        :param str new_dataset_uri:
        :return:
        """
        log.info("[DUPLICATED_DATASETS] [UPDATE STATISTIC]")
        import time

        import ckan.model as model
        from ckanext.ecportal.action.ecportal_delete import package_delete
        list_duplicated_datasets = self.find_duplicated_datasets(file_duplication)
        session = model.Session

        for duplicated_dataset in list_duplicated_datasets:
            start = time.time()
            old_uri = duplicated_dataset.get('old', '')
            new_uri = duplicated_dataset.get('new', '')
            old_id = old_uri.split('/')[-1]
            new_id = new_uri.split('/')[-1]
            if old_id and new_id:
                try:
                    str_query = "update tracking_raw set url = REPLACE(url,:old_id,:new_id) where url like '%{0}%'".format(
                        old_id)
                    result = session.execute(str_query, {'old_id': old_id, 'new_id': new_id})

                    str_query = "update tracking_summary set url = REPLACE(url,:old_id,:new_id) where url like '%{0}%'".format(
                        old_id)
                    result = session.execute(str_query, {'old_id': old_id, 'new_id': new_id})

                    str_query = "update tracking_summary set package_id = REPLACE(package_id,:old_id,:new_id) where package_id like '%{0}%'".format(
                        old_id)
                    result = session.execute(str_query, {'old_id': old_id, 'new_id': new_id})

                    session.commit()
                    log.info(
                        "[UPDATE STATISTICS] [update tracking_raw successful] [oldURI:<{0}>, NewURI:<{1}>]".format(
                            old_id,
                            new_id))
                    duration = time.time() - start
                    log.info("[UPDATE STATISTICS] [oldURI:<{0}>, NewURI:<{1}>] [Duration:{2}]".format(old_id, new_id,
                                                                                                      duration))
                    context = {"model": model, 'user': 'api', 'ignore_auth': True}
                    data_dict = {'id': old_id}
                    result = package_delete(context, data_dict)
                    if result:
                        log.info('[UPDATE STATISTICS] [Delete Dataset successful] [URI:<{0}>]'.format(old_uri))
                        log.info(
                            "[UPDATE STATISTICS] [update statistics successful] [oldURI:<{0}>, NewURI:<{1}>]".format(
                                old_id,
                                new_id))
                    else:
                        log.warn('[UPDATE STATISTICS] [Dataset deleted failed] [URI:<{0}>]'.format(old_uri))

                except logic.NotFound as nf:
                    session.rollback()
                    log.warn(
                        "[UPDATE STATISTICS] [update statistics failed] [Dataset not found] [oldURI:<{0}>, NewURI:<{1}>]".format(
                            old_id,
                            new_id))
                except BaseException as e:
                    session.rollback()
                    log.log(
                        "[UPDATE STATISTICS] [update statistics failed] [oldURI:<{0}>, NewURI:<{1}>]".format(old_id,
                                                                                                             new_id))
                    log.log(traceback.print_exc(e))
            else:
                log.warn("[UPDATE STATISTICS] [Failed, old and new uris are not valid]")

    def update_number_downloads(self):
        """
        Update the number of downloads of resources
        :return:
        """

        def get_list_datasets_update_number_download():
            # list_datasets = ["http://data.europa.eu/88u/dataset/cordisH2020projects"]
            from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers

            try:
                tsch = TripleStoreCRUDHelpers()

                sparql_query = """
                select  ?dataset from <dcatapop-public> from <dcatapop-private> where {
                ?dataset a <http://www.w3.org/ns/dcat#Dataset>

        }

        """
                result = tsch.execute_select_query_auth(sparql_query)
                list_datasets = [ds.get('dataset').get('value') for ds in result]
                log.info('[Dataset] [get_list_datasets_update_number_download] [SUCCESS] [Number of datasets: {0}]'
                         .format(len(list_datasets)))
                list_datasets = list(map(lambda ds:ds.split('/')[-1],list_datasets))
                return list_datasets
            except BaseException as e:
                log.error(traceback.print_exc(e))
                log.error('[Dataset] [get_list_datasets_update_number_download] [Failed]')

        list_datasets = get_list_datasets_update_number_download()
        number_of_datasets = len(list_datasets)
        i = 0
        success = 0
        failed = 0
        for uri_dataset in list_datasets:
            try:
                result = self._update_number_download_dataset(uri_dataset)
                # log.info("[Dataset] [Update number of downloads SUCCESS] [SUCCESS] [DatasetURI<{0}>]".format(uri_dataset))
                if result:
                    success = success +1
                else:
                    failed = failed +1
            except BaseException as e:
                failed = failed + 1
                log.error(
                    "[Dataset] [Update number of downloads FAILED] [Failed] [DatasetURI<{0}>]".format(uri_dataset))
                log.error(traceback.print_exc(e))

            i = i+1
            log.info('[PROGRESS][Update number of download] [{0} / {1}])'.format(i, number_of_datasets))
        log.info('[Dataset] [Update number of downloads END] [Total Success:{0}] [Total Failed:{1}]'.format(success,failed))

    def _update_number_download_dataset(self, uri_dataset):
        """
        Update the number the download of resources  for the dataset with
        :param str uri_dataset:
        :return:
        """
        log.info("[Dataset] [Update number download START] [Dataset URI<{0}>]".format(uri_dataset))

        try:
            context = {"model": model, 'user': 'api', 'ignore_auth': True}
            data_dict = {'id': uri_dataset}

            pkg_dict = logic.get_action('package_show')(context, data_dict)
            existing_dataset = context['package']  # type: DatasetDcatApOp
            list_revisions = existing_dataset.get_list_revisions_ordred()
            for main_resource in existing_dataset.schema.distribution_dcat.values():  # type: DistributionSchemaDcatApOp
                total_number_download = self._get_total_number_download_of_resource(existing_dataset, main_resource,
                                                                                    list_revisions)
                if total_number_download:
                    main_resource.numberOfDownloads_dcatapop['0'] = ResourceValue(total_number_download, None,
                                                                                  'typed-literal',
                                                                                  'http://www.w3.org/2001/XMLSchema#integer')

            context = {"ignore_auth": True}
            result = update_exisiting_dataset(existing_dataset, None, context, {"uri": existing_dataset.dataset_uri},
                                              force_update=True)
            if result:
                log.info('[Dataset] [Update number download SUCCESS] [Dataset URI:<{0}>]'.format(uri_dataset))
                return True
            else:
                log.info('[Dataset] [Update number download FAILED] [Dataset URI:<{0}>]'.format(uri_dataset))
                return False
        except BaseException as e:
            log.error('[Dataset] [Update number download FAILED] [Dataset URI:<{0}>]'.format(uri_dataset))
            log.error(traceback.print_exc(e))

    def _get_total_number_download_of_resource(self, dataset, resource, list_revisions):
        """

        :param DatasetDcatApOp dataset:
        :param DistributionSchemaDcatApOp resource:
        :param list list_revisions
        :return int:
        """

        try:

            log.info('[Dataset] [Get total number of download of resource START] [Dataset URI:<{0}>] [Resource URI<{1}>]'.
                     format(dataset.dataset_uri, resource.uri))
            list_number_download_in_revisions = []
            # dataset = DatasetDcatApOp(dataset_uri)
            revision_dataset = DatasetDcatApOp("")
            i = 0
            total_number_downlaod = int(resource.numberOfDownloads_dcatapop.get('0', ResourceValue('0')).value_or_uri)
            list_number_download_in_revisions = [total_number_downlaod]
            add_number = False
            number_of_download = 0
            for revision in list_revisions:
                revision_dataset = revision.get("dataset")  # type:DatasetDcatApOp
                resource_revision = self._get_similar_resource(resource, revision_dataset)
                if resource_revision:
                    number_of_download = int(
                        resource_revision.numberOfDownloads_dcatapop.get('0', ResourceValue("0")).value_or_uri)
                    list_number_download_in_revisions.append(number_of_download)
                    if number_of_download == 0:
                        add_number = True

                    elif add_number:
                        total_number_downlaod = total_number_downlaod + number_of_download
                        add_number = False
                else:
                    log.info('[Dataset] [Get total number of download of resource FAILED] [Dataset URI:<{0}>] [Resource URI<{1}>]'.
                     format(dataset.dataset_uri, resource.uri))

            # get the initial value
            initial_number_download = self._get_initial_number_download(dataset, resource)
            if not isinstance(initial_number_download, long):
                initial_number_download = 0
            if number_of_download < initial_number_download:
                total_number_downlaod = total_number_downlaod + initial_number_download

            log.info('[Dataset] [Get total number of download of resource SUCCESS] [Dataset URI<{0}>] '
                     '[Resources URI<{1}>] [New  Value:{2}] [trace values:{3}]'.
                     format(dataset.dataset_uri,resource.uri,total_number_downlaod, str(list_number_download_in_revisions)))
            return total_number_downlaod

        except BaseException as e:
            log.error('[Dataset] [Get total number of download of resource] [Failed] [Dataset URI:<{0}>] '
                      '[Resource URI<{1}>]'.
                      format(dataset.dataset_uri, resource.uri))
            log.error(traceback.print_exc(e))

    def _get_similar_resource(self, main_resource, revision_dataset):
        """
        Get the similar in the revision_dataset
        :param DistributionSchemaDcatApOp main_resource:
        :param DatasetDcatApOp revision_dataset:
        :return: DistributionSchemaDcatApOp
        """

        log.info('[Dataset] [Get the similar resource] [Resource URI<{0}>]'.format(main_resource.uri))
        list_resources_in_revision = revision_dataset.schema.distribution_dcat.values()
        for resource in list_resources_in_revision:  # type: DistributionSchemaDcatApOp
            access_url_main = main_resource.accessURL_dcat.get('0', SchemaGeneric('')).uri
            access_url_resource = resource.accessURL_dcat.get('0', SchemaGeneric('')).uri

            if main_resource.uri == resource.uri:
                log.info('[Dataset] [Get the similar resource] [SUCCESS] [Resource URI<{0}>]'.format(main_resource.uri))
                return resource
            elif access_url_main and access_url_resource and (access_url_main == access_url_resource):
                log.info('[Dataset] [Get the similar resource] [SUCCESS] [Resource URI<{0}>]'.format(main_resource.uri))
                return resource
                # Guess!
        log.info('[Dataset] [Get the similar resource] [Failed] [Resource URI<{0}>]'.format(main_resource.uri))
        return None

    def _get_initial_number_download(self, dataset, resource):
        """

        :param dataset:
        :param resource:
        :return:
        """

        from ckan import model
        session = model.Session
        initial_number_download = 0
        sql = '''select rr.resource_count
                  from package pr
                    join resource_group rg on rg.package_id = pr.id
                    join resource rr on rr.resource_group_id = rg.id
                  where pr.name = :ds_name
                    and (rr.id = :rr_id
                        or rr.url = :rr_url )
                    and rr.resource_count > 0;'''

        try:
            # Daniel stuff
            ds_name = dataset.dataset_uri.split('/')[-1]
            rr_id = resource.uri.split('/')[-1]
            rr_url = resource.accessURL_dcat.get('0', SchemaGeneric('')).uri
            rows = session.execute(sql, {'ds_name': ds_name, 'rr_id': rr_id, 'rr_url': rr_url})
            for row in rows:
                initial_number_download = row[0]
                break
            return initial_number_download

        except BaseException as e:
            log.error(
                '[Dataset] [get initial number of download FAILED] [Dataset URI:<{0}>][Resource URI:<{1}>]'.format(
                    dataset.dataset_uri, resource.uri))
            return 0L

    def fix_uri_encoded(self):
        '''
        Fix the uri value if it containe bad url encoded with the multiple encoded issue
        :return:
        '''
        def uncode_uri(uri_value):
            '''
            uncode a uri
            :param str uri_value:
            :return str:
            '''
            import urllib
            end_decoding = False
            while not end_decoding:
                uncode_url = urllib.unquote(uri_value)
                if uncode_url == uri_value:
                    end_decoding = True
                else:
                    uri_value = uncode_url
            return uri_value

    def get_list_incorrect_datasets_issued_date(self):
        from ckanext.ecportal.virtuoso.utils_triplestore_crud_helpers import TripleStoreCRUDHelpers
        try:
            tsch = TripleStoreCRUDHelpers()
            sparql_query = """
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            select ?dataset ?cr ?issued ?modified from <dcatapop-public> from <dcatapop-private>
            where 
            {

            ?cr a <http://www.w3.org/ns/dcat#CatalogRecord> .
            ?cr <http://xmlns.com/foaf/0.1/primaryTopic> ?dataset .
            ?cr <http://purl.org/dc/terms/issued> ?issued .
            ?cr <http://purl.org/dc/terms/modified> ?modified
              filter ((?issued = ?modified) && (str(?issued) > "2019-07-10T12:59:20"))
            }
            order by ?modified

    """
            result = tsch.execute_select_query_auth(sparql_query)
            list_datasets = [ds.get('dataset').get('value') for ds in result]
            return list_datasets
        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error('[get_list_incorrect_datasets_issued_date] [Failed]')


    def get_valid_issued_date(self, dataset):
        '''

        :param  :DatasetDcatApOp
        :return: str
        '''
        try:
            RELEASE_DATE = "2019-07-10T09:07:00"
            list_revisions = dataset.get_list_revisions_ordred()
            revision_dataset = DatasetDcatApOp("")
            i = 0
            incorrect_issued_date = dataset.schema_catalog_record.issued_dcterms.get('0',ResourceValue('')).value_or_uri
            for revision in list_revisions:

                issued_date =''
                i = i + 1
                revision_dataset = revision.get("dataset")  # type:DatasetDcatApOp
                try:
                    rollback_issued_date = revision_dataset.schema_catalog_record.issued_dcterms.get('0',ResourceValue('')).value_or_uri
                except BaseException as e:
                    log.error(traceback.print_exc(e))
                    log.error("Cannot extract modified date or issued date from revision: URI: {0}".format(i))
                if incorrect_issued_date and rollback_issued_date  and rollback_issued_date < RELEASE_DATE and incorrect_issued_date != rollback_issued_date:
                    log.info(
                        "[Dataset] [Get correct issued date] [Successful] [dataset URI:<{0}>] [issued date: {1}]".
                            format(dataset.dataset_uri, rollback_issued_date))
                    return rollback_issued_date
            log.info("[Dataset] [Get correct issued date] [Failed] [dataset URI:<{0}>]".format(dataset.dataset_uri))
            return ''
        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error("[Fix incorrect issued date] [Failed] [Dataset][URI:<{0}>]".format(dataset.dataset_uri))



    def fix_incorrect_issued_date_for_dataset(self, uri_dataset):
        '''

        :param str dataset_uri:
        :return: Boulean
        '''


        context = {"model": model, 'user': 'api', 'ignore_auth': True}
        data_dict = {'id': uri_dataset.split('/')[-1]}
        package = logic.get_action('package_show')(context, data_dict) # type: DatasetDcatApOp
        dataset = context['package']
        correct_issued_date = self.get_valid_issued_date(dataset)
        if not correct_issued_date:
            log.info("[fix_incorrect_issued_date_for_dataset] [failed] [Dataset] [{0}]".format(uri_dataset))
            return False
        else:
            dataset.schema_catalog_record.issued_dcterms['0'].value_or_uri = correct_issued_date
            context = {"ignore_auth": True}
            result = update_exisiting_dataset(dataset, None, context, {"uri": dataset.dataset_uri},
                                              force_update=True)
            if result:
                log.info('[Dataset] [Update incorrect issued date SUCCESS] [Dataset URI:<{0}>]'.format(uri_dataset))
                return True
            else:
                log.info('[Dataset] [Update incorrect issued date FAILED] [Dataset URI:<{0}>]'.format(uri_dataset))
                return False




    def fix_all_incorrect_issued_date(self):
        '''
        To fix the incorrect issued date which has been updated vi th the same value of the modified date.

        :return:
        '''

        list_incorrect_datasets = self.get_list_incorrect_datasets_issued_date()
        # list_incorrect_datasets = ['http://data.europa.eu/88u/dataset/stress-dexia']
        try:
            i=0
            total = len(list_incorrect_datasets)
            failed_update = []
            for uri_dataset in list_incorrect_datasets:
                i+=1
                try:
                    result = self.fix_incorrect_issued_date_for_dataset(uri_dataset)
                    if result:
                        log.info("[fix_all_incorrect_issued_date] [Successful] [Dataset:{0}]".format(uri_dataset))
                    else:
                        log.error(traceback.print_exc(e))
                        log.info(
                            "[fix_all_incorrect_issued_date][Failed] [Dataset:{0}]".format(uri_dataset))
                except BaseException as e:
                    log.error(traceback.print_exc(e))
                    log.error("[fix_all_incorrect_issued_date] [Failed] [Dataset:{0}]".format(uri_dataset))
                log.info(
                    "[fix_all_incorrect_issued_date] [***** Progress][{0}/{1}] [Dataset:{2}]".format(i,total,uri_dataset))

        except BaseException as e:
            log.error(traceback.print_exc(e))
            log.error("[fix_incorrect_issued_date] [failed]")
