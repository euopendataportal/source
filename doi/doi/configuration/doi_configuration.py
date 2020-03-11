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
DOI configuration object.
"""


class DOIConfiguration:

    def __init__(self):
        pass

    # DOI generator
    doi_prefix = ''  # type: str
    doi_db_connection_string = ''  # type: str

    # Email configuration
    email_host = ''  # type: str
    email_port = 0  # type: int
    email_is_authenticated = False  # type: bool
    email_username = ''  # type: str
    email_password = ''  # type: str

    # Report service configuration
    report_log_directory = ''  # type: str
    report_sender_email = ''  # type: str
    report_receiver_email = ''  # type: str

    # Submission service configuration
    submission_doi_ra_url = ''  # type: str
    submission_doi_ra_user = ''  # type: str
    submission_doi_ra_password = ''  # type: str
    submission_doi_sender_email = ''  # type: str
    submission_doi_from_company = ''  # type: str
    submission_doi_to_company = ''  # type: str

    citation_formats = {}  # type: dict [str, dict ["name":str, "format":str, "extension":str]]
    citation_resolver = ''  # type: str
    citation_file_resolver = ''  # type: str
    citation_style = ''  # type: str
