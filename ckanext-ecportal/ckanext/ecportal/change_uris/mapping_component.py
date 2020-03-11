# -*- coding: utf-8 -*-
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

import csv

import logging

import traceback

import os

from ckanext.ecportal.model.identifier_mapping import DatasetIdMapping

from ckanext.ecportal.action.ecportal_get import package_show

from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp

logging.basicConfig(level=logging.WARN)
log = logging.getLogger("ESTAT_MAPPER")

CSV_DELIMITER = ";"

HISTORY_DATASETS_FILE_NAME = "history_dataset.data"


class MappingURIS:
    """
    Class to manage the mapping of uris.

    Validation and building the mapping object
    """

    log_factory = None

    def __init__(self, action, report_folder_path, job_str, csv_row):
        """

        :param str action:
        :param str report_folder_path:
        :param str job_str:
        :param list csv_row_str:
        """
        self.action = action
        self.lagacy_dataset_code =""
        self.new_dataset_code =""
        self.uri_dataset = ""
        self.old_uri = ""
        self.new_uri = ""
        self.publisher = ""
        self.mapping_info = ""
        self.dataset = DatasetDcatApOp("")
        self.is_valid = False
        self.report_folder_path = report_folder_path
        self.job_str = job_str
        self.csv_row = csv_row
        self.log = self.__configure_log()

    def __configure_log(self):
        """
        Configuration of the logger. new
        :return:
        """
        import shutil
        import os

        if not MappingURIS.log_factory:
            name = "DETAILED-MAPPING-JOB:<{0}>".format(self.job_str)
            _log = logging.getLogger(name)
            _log.setLevel(logging.DEBUG)
            report_file_name = self.job_str + "-detailed-" + ".log"
            job_report_folder = self.report_folder_path+"/"+self.job_str
            file_handler = logging.FileHandler(job_report_folder + "/" + report_file_name, "a")
            formatter = logging.Formatter('[%(name)s] [%(asctime)s] [%(levelname)s] %(message)s')
            file_handler.setFormatter(formatter)
            _log.addHandler(file_handler)
            MappingURIS.log_factory = _log

        return MappingURIS.log_factory

    def build_mapping_uri(self):

        """
        Build the mapping object
        :return:
        """
        csv_row_str = CSV_DELIMITER.join(self.csv_row)
        self.log.info("[Building the mapping object from the csv row] [CSV:<{0}>]".format(csv_row_str))
        csv_row = self.csv_row
        if self.validate_mapping():
            self.publisher = csv_row[0]
            # action = csv_row[1]
            self.lagacy_dataset_code = csv_row[2]
            self.new_dataset_code = csv_row[3]
            ckan_name = csv_row[4]
            self.old_uri = csv_row[5]
            self.new_uri = csv_row[6]
            self.uri_dataset = "http://data.europa.eu/88u/dataset/{0}".format(ckan_name)
            self.log.info("[Building the mapping object done for csv row] [CSV:<{0}>]".format(csv_row_str))
        else:
            self.log.info("[Building the mapping object failed for csv row] [CSV:<{0}>]".format(csv_row_str))

        return self

    def validate_mapping(self):
        """
        Validate the mapping object
        At least all values should be not empty
        :return:
        """

        is_correct_csv_element = True
        mapping_row = self.csv_row
        csv_row_str = CSV_DELIMITER.join(self.csv_row)
        is_size_csv_element_correct = True
        is_correct_csv_element = True
        error_message = ""
        self.log.info("[Start Validation of csv row] [CSV:<{0}>]".format(
            csv_row_str))
        if len(mapping_row) != 7:
            is_size_csv_element_correct = False
            self.log.info("[Preparation of the mapping from csv row failed. Size of the csv row incorrect] [CSV:<{0}>]".format(csv_row_str))
            error_message = "{0}{1} ".format(error_message,"(Size of csv row incorrect)")

        if is_size_csv_element_correct:
            for csv_element in mapping_row:
                if csv_element == "":
                    is_correct_csv_element = False
                    self.log.info("[Preparation of the mapping from csv row failed. Empty element found] [CSV:<{0}>]".format(csv_row_str))
                    error_message = "{0}{1} ".format(error_message, "(Size of csv row incorrect)")
            action = mapping_row[1] #type: str
        if action.lower() != "update":
            is_correct_csv_element = False
            self.log.info("[Preparation of the mapping from csv row failed. Action is not UPDATE] [CSV:<{0}>]".format(csv_row_str))
            error_message = "{0}{1} ".format(error_message, "(Action is not UPDATE)")

        is_mapping_valid = True if is_size_csv_element_correct and is_correct_csv_element else False
        self.is_valid = is_mapping_valid
        self.mapping_info = "Validation of mapping:[{0}]{1}".format( error_message,self.mapping_info)
        self.log.info("[Validation of mapping:{0}] [CSV:<{1}>]".format(is_mapping_valid,csv_row_str))
        return self.is_valid



    def load_dataset(self):
        """
        Load Dataset from ODP
        :return:
        """
        uri_datasetdo = ""
        uri_dataset = self.uri_dataset
        context = {"ignore_auth": True}
        try:
            dataset = package_show(context, data_dict={"uri": uri_dataset})
            self.dataset = context.get("package")
            self.log.info("[Load Dataset:<{0}>]".format(self.uri_dataset))
        except BaseException as e:
            self.dataset = None
            self.log.error("Loading dataset failed for the dataset <{0}>.".format(self.uri_dataset))
            self.log.error(traceback.print_exc(e))

    def to_string(self):
        """
        reate a string version of the Mapping
        :return:
        """
        csv_str =CSV_DELIMITER.join(self.csv_row)
        message = "[MAPPING-URI:<{0}>] [MAPPING-ACTION:<{1}>] [CSV:<{2}>] [MAPPING-INFO:<{3}>] ".format(self.uri_dataset,self.action, csv_str, self.mapping_info)
        return message

    def update_dataset_url(self):
        """
        update the dataset using the mapping info
        This will also update the mapping in the table dataset_id_mappig important  to avoid the problem of duplication
        :return:
        """

        try:
            from ckanext.ecportal.action.ecportal_save import update_exisiting_dataset
            from ckanext.ecportal.model.schemas import DocumentSchemaDcatApOp
            from ckanext.ecportal.model.schemas.generic_schema import ResourceValue
            self.log.info("[START: Update ESTAT Dataset] {0}".format(self.uri_dataset))

            if self.action == "update":
                new_value = self.new_uri
                old_value = self.old_uri
                new_identifier = self.new_dataset_code
            else:
                new_value = self.old_uri
                old_value = self.new_uri
                new_identifier = self.lagacy_dataset_code


            status_mapping = "FAILED"
            self.load_dataset()
            if not self.dataset:
                status_mapping = "FAILED"
                self.log.warn("[STATUS UPDATING DATASET:{0}] [Cannot load Dataset. URI:<{1}>]".format(status_mapping, self.uri_dataset))
                return False
            updated_dataset = self.dataset
            exiting_url = updated_dataset.schema.landingPage_dcat \
                .get('0', DocumentSchemaDcatApOp("")).url_schema \
                .get('0', ResourceValue("")).value_or_uri
            # if (exiting_url==self.old_uri):
            result = False
            if exiting_url:
                updated_dataset.schema.landingPage_dcat.get('0', DocumentSchemaDcatApOp("")).url_schema.get('0',
                                                                                                            ResourceValue(
                                                                                                                "")).value_or_uri = new_value
                updated_dataset.schema.identifier_dcterms['0'].value_or_uri = new_identifier
                context = {"ignore_auth": True}
                result = update_exisiting_dataset(self.dataset, None, context, {"uri": self.uri_dataset})
                if result:
                    mapping_table = DatasetIdMapping.by_internal_id(self.dataset.dataset_uri.split('/')[-1])
                    mapping_table.external_id = new_value
                    mapping_table.update_db()

                status_mapping = "SUCCESS" if result else "FAILED"
                self.log.info("[STATUS UPDATING DATASET:{0}] [URI:<{1}>]".format(status_mapping, self.uri_dataset))
            else:
                status_mapping = "FAILED"
                self.log.error("[STATUS UPDATING DATASET:{0}] [Dataset not loaded] [URI:<{1}>]".format(status_mapping, self.uri_dataset))
            return result
        except BaseException as e:
            status_mapping = "FAILED"
            self.log.error(traceback.print_exc(e))
            self.log.error("[STATUS UPDATING DATASET:{0}] [URI:<{1}>]".format(status_mapping, self.uri_dataset))
            return False


class MappingESTAT:
    """
    Build and manage of the list of mapping extracted from the csv file.
    """

    def __init__(self, csv_mapping_file, action, report_folder_path, publisher):
        """
        Create the Mapping manager object using the csv file and the action
        :param str csv_mapping_file:
        :param str action:
        :param str report_folder_path:
        :param str publisher:
        """
        import datetime
        self.list_mappings = []  # type:list[MappingURIS]
        self.csv_mapping_file = csv_mapping_file
        self.action = action
        self.publisher = publisher
        self.report_folder_path = report_folder_path
        self.job_str = "JOB-" + datetime.datetime.now().strftime("%Y_%m_%d___%H-%M-%S")
        self.report_log = self.__log_configuration()
        self.done_history_mappings = {}
        self.nbr_of_mappings_in_csv = 0
        self.number_of_valid_mappings = 0
        self.number_of_mappings_todo = 0

    def __log_configuration(self):
        """
        Configuration of the logger to be used as a report.
        For each mapping indicate the beginning the end and the status of the mapping
        :return:
        """
        name = "[ESTAT MAPPER] [{0}] ".format(self.job_str)
        log_report = logging.getLogger(name)
        format_message_log = "%(message)s"

        report_file_name = self.job_str + ".log"
        import shutil
        job_report_folder = self.report_folder_path + "/" + self.job_str
        if os.path.exists(job_report_folder):
            shutil.rmtree(job_report_folder)
        os.mkdir(job_report_folder)

        file_handler_report = logging.FileHandler(job_report_folder + "/" + report_file_name, mode="w")
        formatter = logging.Formatter(format_message_log)
        file_handler_report.setFormatter(formatter)
        log_report.addHandler(file_handler_report)
        return log_report

    def build_mapping_from_csv(self):
        """
        Build the mapping from the CSV file.
        The CSV file should follow  the correct structure
        ["dataset_uri", "old_uri", "new_uri", "publisher", "ckan_name" ],
        :return:
        """
        import json
        import os.path as path
        self.report_log.info("\n==============================================================================="
                             "\n********** START PREPARATION AND VALIDATION OF CSV MAPPING. **********\n ")
        number_of_mappings_in_csv = 0
        number_of_valid_mappings = 0
        number_of_mappings_todo = 0

        history_path = self.report_folder_path + "/" + HISTORY_DATASETS_FILE_NAME
        if path.exists(history_path):
            with open(history_path) as history_data_file:
                self.done_history_mappings = json.load(history_data_file)
        else:
            self.done_history_mappings = {"success": {}, "failed": {}}

        csv_path = self.csv_mapping_file
        mapping_rows = csv.reader(open(csv_path,'r'), delimiter = CSV_DELIMITER)
        csv_row_number = 0
        for csv_row in mapping_rows:

            mapping_uri = MappingURIS(action=self.action, report_folder_path=self.report_folder_path,
                                      job_str=self.job_str,csv_row=csv_row)
            mapping_uri.build_mapping_uri()
            if mapping_uri.is_valid:
                number_of_valid_mappings +=1

            is_mapping_done = self.done_history_mappings.get(('success'),{}).has_key(mapping_uri.uri_dataset)
            if is_mapping_done:
                if mapping_uri.action=="update":
                    mapping_uri.mapping_info = mapping_uri.mapping_info + " (Mapping already done) "
                else:
                    self.done_history_mappings.get(('success'),{}).pop(mapping_uri.uri_dataset)
                    is_mapping_done = False

            is_correct_publisher = True
            if self.publisher not in [mapping_uri.publisher, "all"]:
                mapping_uri.mapping_info = mapping_uri.mapping_info + " (Not the expected publisher)"
                is_correct_publisher = False

            # add only valid and n ot done mappings
            if is_correct_publisher and mapping_uri.is_valid and not is_mapping_done:
                self.list_mappings.append(mapping_uri)
                number_of_mappings_todo +=1
            else:
                self.report_log.error("[Preparation of the mapping failed] {0}".
                                      format(mapping_uri.to_string()))
            number_of_mappings_in_csv += 1

        self.nbr_of_mappings_in_csv = number_of_mappings_in_csv
        self.number_of_valid_mappings = number_of_valid_mappings
        self.number_of_mappings_todo = number_of_mappings_todo
        self.report_log.info("\n********** END PREPARATION AND VALIDATION OF CSV MAPPING. ********** "
                             "\n===============================================================================")

    def get_mapping_by_old_uri(self, old_uri):
        """

        :param str old_uri:
        :return:
        """
        for mapping_uri in self.get_list_of_mappings():
            if mapping_uri.old_uri == old_uri:
                return mapping_uri
        log.error("Mapping not found for {0}".format(old_uri))
        return ""

    def get_mapping_by_new_uri(self, new_uri):
        """

        :param str new_uri:
        :return:
        """
        for mapping_uri in self.get_list_of_mappings():
            if mapping_uri.new_uri == new_uri:
                return mapping_uri
        log.error("Mapping not found for {0}".format(new_uri))
        return ""

    def get_mapping_by_dataset_uri(self, dataset_uri):
        """

        :param str new_uri:
        :return:
        """
        for mapping_uri in self.get_list_of_mappings():
            if mapping_uri.new_uri == dataset_uri:
                return mapping_uri
        log.error("Mapping not found for Dataset URI {0}".format(dataset_uri))
        return ""

    def update_estat_datasets(self):
        """
        The main function to update the list of dataset using the mapping list loaded
        :return:
        """
        list_mappings = self.get_list_of_mappings()
        self.report_log.info("\n===============================================================================\n"
                             "********** START UPDATING DATASETS **********"
                             "\n-JOB:{4}"
                             "\n-Publisher:{5}"
                             "\n-Action: {0}. "
                             "\n-Number of mappings in CSV:{1} "
                             "\n-Number of valid mappings:{2}"
                             "\n-Number of mappings to perform (not already done):{3}"
                             "\n==============================================================================="
                             "\n********** SECTION: PROGRESSION Of MAPPING: START\n".
                             format(self.action, self.nbr_of_mappings_in_csv,self.number_of_valid_mappings, self.number_of_mappings_todo, self.job_str, self.publisher))
        i = 1
        success = 0
        failed = 0

        for mapping_uri in list_mappings:
            try:
                result = mapping_uri.update_dataset_url()
                if result:
                    success += 1
                    status_mapping = "SUCCESS"
                    if mapping_uri.action =="update":
                        self.done_history_mappings["success"][mapping_uri.uri_dataset] = "{0} [JOB:{1}]".format(mapping_uri.to_string(),self.job_str)
                    self.done_history_mappings["failed"].pop(mapping_uri.uri_dataset,None)
                else:
                    failed += 1
                    status_mapping = "FAILED"
                    self.done_history_mappings["failed"][mapping_uri.uri_dataset] = "{0} [JOB:{1}]".format(mapping_uri.to_string(),self.job_str)
                self.report_log.info(
                    "[PROGRESS_MAPPING-{0}] [Status:{1}] {2}".format(i, status_mapping, mapping_uri.to_string()))
            except BaseException as e:
                self.report_log.error("[ERROR Performing the mapping] {0}".format(mapping_uri.to_string()))
                self.report_log.error(traceback.print_exc(e))

            i += 1

        str_end = "\n********** SECTION: PROGRESSION OF MAPPING: END " \
                  "\n===============================================================================" \
                  "\n-********** END UPDATING DATASETS. FINAL REPORT **********" \
                  "\n-Action:{0}." \
                  "\n-Publisher:{4}" \
                  "\n-Number of mappings:{1}" \
                  "\n-Successful mappings:{2}" \
                  "\n-Failed mappings:{3} " \
                  "\n===============================================================================".\
                format(self.action, self.number_of_mappings_todo, success, failed, self.publisher)

        self.__save_history_done_mappings()
        self.report_log.info(str_end)

    def get_list_of_mappings(self):
        return self.list_mappings

    def __save_history_done_mappings(self):
        try:
            import json
            histoy_datasets_path = self.report_folder_path + "/" + HISTORY_DATASETS_FILE_NAME
            with open(histoy_datasets_path,"w") as json_file:
                json.dump(self.done_history_mappings, json_file, indent=4)
                log.info("Save history of mappings in {0}".format(self.report_folder_path+"/"+HISTORY_DATASETS_FILE_NAME))
                return True
        except BaseException as e:
            log.error("Error when saving the history of mapped datasets")
            log.error(traceback.print_exc(e))
            return False
