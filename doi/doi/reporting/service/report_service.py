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


"""
Report service for handling registration reports.
"""

import logging

from doi.reporting.domain.registration_report import RegistrationReport

from arhs_utils.arhs_email.email_sender import EmailSender


class ReportService:

    def __init__(self, report_log_directory, email_sender, report_sender, report_receiver):
        """
        Initialise the report service.
        :param str report_log_directory: The directory where report logs will be stored.
        :param EmailSender email_sender: The email sender to be used.
        """
        self._report_log_directory = report_log_directory
        self._email_sender = email_sender
        self._report_sender = report_sender
        self._report_receiver = report_receiver
        self._logger = logging.getLogger(self.__class__.__name__)

    def handle_registration_report(self, report):
        """
        Handle a registration report.
        :param RegistrationReport report: The report data.
        :return: The generated log file location.
        """
        log_location = self._log_report_to_file(report)

        try:
            self._send_report_to_email(report)
        except Exception as exception:
            error_message = 'DOI SMTP server error: {0}'.format(str(exception))
            self._logger.error(error_message)

        return log_location

    def _log_report_to_file(self, report):
        """
        Log the report to a file.
        :param RegistrationReport report: The report data.
        :return: The generated log file location.
        """
        log_location = self._report_log_directory + '/' + report.doi.replace('/', '_') + '.log'
        log_file = open(log_location, 'w')
        log_file.write(str(report))
        log_file.close()

        return log_location

    def _send_report_to_email(self, report):
        """
        Send the report via email to configured reciever.
        :param RegistrationReport report: The report data.
        :return: The generated log file location.
        """
        email_subject = 'DOI registration report for DOI [{0}]'.format(report.doi)
        self._email_sender.send_email(self._report_sender, self._report_receiver, email_subject, str(report))
