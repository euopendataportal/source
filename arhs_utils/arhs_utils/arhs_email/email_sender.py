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
import smtplib


class EmailSender:

    def __init__(self, email_host, email_port, with_authentication, email_user, email_password):
        """
        Initialize the email sender
        :param str email_host:
        :param int email_port:
        :param boolean with_authentication:
        :param str email_user:
        :param str email_password:
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self._email_host = email_host
        self._email_port = email_port
        self._email_user = email_user
        self._email_password = email_password
        self._with_authentication = with_authentication

    def send_email(self, sender, receivers, subject, body):
        """
        Send a simple email.
        :param str sender: The sender of th email.
        :param str or array receivers: The receivers of the email.
        :param str subject: The subject of the email.
        :param str body: The body of the email.
        """
        _email_server = smtplib.SMTP(self._email_host, self._email_port)

        # authenticate if necessary
        if self._with_authentication:
            _email_server.login(self._email_user, self._email_password)

        message = "From: %s\r\n" % sender \
                  + "To: %s\r\n" % receivers \
                  + "Subject: %s\r\n" % subject \
                  + "\r\n" \
                  + body

        _email_server.sendmail(sender, receivers, message)

        _email_server.quit()
