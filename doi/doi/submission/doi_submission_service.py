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
DOISubmissionService
"""
import logging

import requests

from doi.submission.domain.submission_result import SubmissionResult


class DOISubmissionService:

    def __init__(self, doi_ra_url, doi_ra_user, doi_ra_password):
        """
        Initialisation of the DOI submission service.
        :param str doi_ra_url: The DOI registration agency url.
        :param str doi_ra_user: The DOI registration agency username.
        :param str doi_ra_password: The DOI registration agency password.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._doi_ra_url = doi_ra_url
        self._doi_ra_user = doi_ra_user
        self._doi_ra_password = doi_ra_password

    def register_doi(self, doi_registration_message):
        """
        Register a DOI with metadata.
        :param string doi_registration_message: the doi registration message xml to register
        :returns a boolean success value
        """
        response_code = 0
        response_message = ''
        try:
            http_auth = self._doi_ra_user + ':' + self._doi_ra_password
            http_auth = 'Basic ' + http_auth.encode('base64').strip()

            headers = {'Content-Type': 'application/xml;charset=UTF-8', 'Authorization': http_auth}
            response = requests.post(self._doi_ra_url, headers=headers,
                                     data=doi_registration_message, verify=False)
            response_code = response.status_code
            response_message = response.text
        except BaseException as exception:
            error_message = 'Could not submit DOI registration request: {0}'.format(exception.message)
            self._logger.error(error_message)
            response_code = 500
            response_message = error_message
        finally:
            return SubmissionResult(response_code, response_message)
