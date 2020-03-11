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


import shutil
import tempfile
import unittest
import os.path

from doi.reporting.domain.registration_report import RegistrationReport
from doi.reporting.domain.registration_report_status import RegistrationReportStatus
from doi.reporting.service.report_service import ReportService

from arhs_utils.arhs_email.email_sender import EmailSender


class ReportServiceTest(unittest.TestCase):

    _EMAIL_SENDER = EmailSender('ms1.cube-lux.lan', 25, True, '', '')

    _TEST_LOG = "ODP DOI Registration report for '10.1234/odp/test'\n" \
                + "\tStatus: SUCCESS\n" \
                + "\tMessage: This is a test report\n\n" \
                + "----------------\n\n" \
                + "Registration message:\n\n" \
                + "<DoiRegistrationMessage></DoiRegistrationMessage>"

    _TEST_DOI = '10.1234/odp/test'
    _TEST_STATUS = RegistrationReportStatus.SUCCESS
    _TEST_MESSAGE = 'This is a test report'
    _TEST_XML = '<DoiRegistrationMessage></DoiRegistrationMessage>'

    def setUp(self):
        self._test_dir = tempfile.mkdtemp()
        print('Temp dir: ' + self._test_dir)
        self._report_service = ReportService(self._test_dir,
                                             ReportServiceTest._EMAIL_SENDER,
                                             'OP.Project-ODP@arhs-cube.Com',
                                             'OP.Project-ODP@arhs-cube.Com')

    def tearDown(self):
        shutil.rmtree(self._test_dir)


    def test_handle_registration_report(self):
        test_report = RegistrationReport(ReportServiceTest._TEST_DOI,
                                         ReportServiceTest._TEST_STATUS,
                                         ReportServiceTest._TEST_MESSAGE,
                                         ReportServiceTest._TEST_XML)
        generated_location = self._report_service.handle_registration_report(test_report)

        # Assert log file exists
        self.assertTrue(os.path.isfile(generated_location))

        # Assert log file content
        generated_report_log = open(generated_location, "r")
        generated_content = generated_report_log.read()
        generated_report_log.close()
        self.assertEquals(ReportServiceTest._TEST_LOG, generated_content)
