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


import unittest

from arhs_utils.email.email_sender import EmailSender


class EmailSenderTest(unittest.TestCase):

    _EMAIL_SENDER = EmailSender('ms1.cube-lux.lan', 25, False, '', '')

    def test_send_email(self):
        EmailSenderTest._EMAIL_SENDER.send_email('test1@arhs-cube.com',
                                      'test2@arhs-cube.com',
                                      'ODP email message',
                                      'Hello from ODP CKAN mail')
        # TODO find python dumbster alternative to assert email
