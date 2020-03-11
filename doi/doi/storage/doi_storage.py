# -*- coding: utf-8 -*-
# Copyright (C) 2018  ARhS-CUBE

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from doi.exceptions.interface_exception import InterfaceException


class DOIStorageInterface(object):

    def __init__(self):
        pass

    def save(self, doi):
        """
        Save a DOI.
        :param DOI doi: The DOI to save.
        :return: The saved DOI.
        """
        raise InterfaceException()

    def find(self, **args):
        """
        Get a list of DOIs.
        :param args: arguments to filter DOIs.
        :return: The array of found DOIs.
        """
        raise InterfaceException()

    def find_one(self, **args):
        """
        Get on DOI.
        :param args: arguments to filter DOIs.
        :return: The found DOI. None if not found.
        """
        raise InterfaceException()

    def next_doi(self, prefix, provider):
        """
        Get the next DOI and add it to the storage.
        :param str prefix: The prefix of the DOI to generate.
        :param str provider: The provider of the data excepting a new DOI
        :return: The next DOI.
        """
        raise InterfaceException()

    def delete(self, **args):
        """
        Delete one DOI.
        :param args: arguments to find the DOI to delete.
        """
        raise InterfaceException()

    def delete_all(self, **args):
        """
        Delete all DOI.
        :param args: arguments to filtering the DOIs to delete.
        """
        raise InterfaceException()
