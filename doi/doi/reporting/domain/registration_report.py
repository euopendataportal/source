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
DOI registration report object.
"""


class RegistrationReport:

    def __init__(self, doi, status, message, registration_message_xml):
        """
        Initialise a registration report.
        :param str doi: The DOI for which the report was generated.
        :param str status: The registration result status.
        :param str message: A description message.
        :param str registration_message_xml: The registration message xml used for registration.
        """
        self.doi = doi
        self.status = status
        self.message = message
        self.registration_message_xml = registration_message_xml

    def __str__(self):
        return unicode("ODP DOI Registration report for '{0}'\n\tStatus: {1}\n\tMessage: {2}\n\n----------------\n\nRegistration message:\n\n{3}"
                       .format(self.doi, self.status, self.message, self.registration_message_xml))
