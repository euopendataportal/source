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
DOI registration report repository.
"""


class ReportRepository:

    def __init__(self):
        pass

    def save(self, doi):
        """
        Save a DOI report.
        :param str doi: The DOI to save.
        :return: The saved DOI.
        """
        pass

    def find_by_doi(self, doi):
        """
        Find all reports.
        :param str doi: The DOI to save.
        :return: The saved DOI.
        """
        pass

    def find_by_uri(self, uri):
        """
        Find all reports.
        :param str doi: The DOI to save.
        :return: The saved DOI.
        """
        pass
