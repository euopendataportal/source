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


import logging

from arhs_utils.arhs_email.email_sender import EmailSender
from dcatapop_to_datacite_mapper.dcatapop_to_datacite_mapper import DCATAPOPToDataCiteMapper
from doi.configuration.doi_configuration import DOIConfiguration
from doi.controllers.doi_controller import DOISController
from doi.domain.doi_object import DOI
from doi.exceptions.doi_registration_exception import DOIRegistrationException
from doi.generator.doi_generator import DOIGenerator
from doi.reporting.domain.registration_report import RegistrationReport
from doi.reporting.domain.registration_report_status import RegistrationReportStatus
from doi.reporting.service.report_service import ReportService
from doi.storage.doi_storage_sqlalchemy import DOIStorageSQLAlchemy
from doi.submission.doi_submission_service import DOISubmissionService
from doi.submission.doi_submission_service import SubmissionResult


class DOIFacade:

    def __init__(self, configuration):
        """
        Initialize the DOIFacade.
        :param DOIConfiguration configuration: the configuration to use
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self._configuration = configuration
        self._doi_registration_xml_generator = DCATAPOPToDataCiteMapper(self._configuration.submission_doi_sender_email,
                                                                        self._configuration.submission_doi_from_company,
                                                                        self._configuration.submission_doi_to_company)
        self._doi_submission_service = DOISubmissionService(self._configuration.submission_doi_ra_url,
                                                            self._configuration.submission_doi_ra_user,
                                                            self._configuration.submission_doi_ra_password)
        self._email_sender = EmailSender(self._configuration.email_host,
                                         self._configuration.email_port,
                                         self._configuration.email_is_authenticated,
                                         self._configuration.email_username,
                                         self._configuration.email_password)
        self._report_service = ReportService(self._configuration.report_log_directory,
                                             self._email_sender,
                                             self._configuration.report_sender_email,
                                             self._configuration.report_receiver_email)
        self._doi_controller = DOISController(DOIStorageSQLAlchemy(self._configuration.doi_db_connection_string),
                                              self._configuration.citation_formats,
                                              self._configuration.citation_resolver,
                                              self._configuration.citation_file_resolver,
                                              self._configuration.citation_style)
        self._doi_generator = DOIGenerator(self._doi_controller, self._configuration.doi_prefix)

    def generate_doi(self, provider_id, uri=None, suffix=None):
        """
        Generate a new DOI.
        :param str provider_id: The unique identifier of the provider.
        :param str uri: The uri of the element to generate a DOI for.
        :param str suffix: The second suffix of the DOI.
        :return str: The generated DOI
        """
        return str(self._doi_generator.generate(provider_id, uri, suffix))

    def assign_doi(self, doi_str, uri=None):
        """
        Assign a URI to an existing.
        :param str doi_str: The DOI to associate.
        :param str uri: The uri of the element to associate.
        """
        if self.is_external_doi(doi_str):
            return
        try:
            doi = DOI.doi_from_string(doi_str)
            self._doi_controller.set_doi_association(doi, uri)
        except BaseException as exception:
            error_message = 'DOI association failed: {0}'.format(exception.message)
            self._logger.error(error_message)
            raise DOIRegistrationException(error_message)

    def get_citation(self, doi_str, language):
        """
        Get a formatted citation from a DOI.
        :param str doi_str: The DOI to find.
        :param str language: Language of the requested citation.
        :raises: Exception: If the Citation can not be obtained.
        :return: The formatted citation got by a DOI.
        """
        return self._doi_controller.get_citation(doi_str, language)

    def download_citation(self, doi_str, style, language):
        """
        Get a downloadable citation from a DOI.
        :param str doi_str: The DOI to find.
        :param str style: Style of the requested citation.
        :param str language: Language of the requested citation.
        :raises: Exception: If the Citation can not be obtained.
        :return: A dict containing the result content as "content", the content type as "type" and the filename as "filename"
        """
        return self._doi_controller.download_citation(doi_str, style, language)

    def register_doi(self, doi, data):
        """
        Register the DOI with metadata.
        :param str doi: The DOI to register.
        :param dict data: The data for DOI registration.
        :return boolean: Whether the DOI was correctly registered.
        """
        if self.is_external_doi(doi):
            return
        try:
            registration_message_xml = self._doi_registration_xml_generator.generate_dataset_metadata(doi, data)
            submission_result = self._doi_submission_service.register_doi(
                registration_message_xml)  # type: SubmissionResult
            registration_report = RegistrationReport(doi,
                                                     RegistrationReportStatus.SUCCESS if submission_result.status == 200 else RegistrationReportStatus.FAILURE,
                                                     submission_result.message,
                                                     registration_message_xml)
            self._report_service.handle_registration_report(registration_report)
            return registration_report.status == RegistrationReportStatus.SUCCESS
        except BaseException as exception:
            error_message = 'DOI registration failed: {0}'.format(str(exception))
            self._logger.error(error_message)
            raise DOIRegistrationException(error_message)

    def registration_callback(self, report):
        """
        DOI registration callback for registration agency to submit registration report.
        :param report: The registration report
        """
        pass

    def is_external_doi(self, doi_str):
        """
        Check if the DOI is an external DOI.
        :param str doi_str: The DOI to check.
        :return boolean: True if the DOI isn't managed internally.
        """
        try:
            doi = DOI.doi_from_string(doi_str)
            return not self._doi_controller.doi_exists(doi)
        except BaseException as exception:
            return True
