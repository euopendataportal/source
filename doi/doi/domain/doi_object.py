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

from doi.exceptions.doi_parser_exception import DOIParserException
import re


class DOI:

    _PATH_SEPARATOR = '/'
    _SUFFIX_ELEMENT_VALIDATOR = re.compile("^[^ ;/?:@&=+$,*\"%#<>\'}{|\\\^\[\]\`\´]+$")

    def __init__(self, prefix, suffix_provider, suffix_element, uri=None):
        self._prefix = prefix
        self._suffix_provider = suffix_provider
        self._suffix_element = suffix_element
        self._uri = uri
        self._main_separator = '/'
        self._suffix_separator = '/'
        self.validate_syntax()

    def validate_syntax(self):
        if not (DOI._SUFFIX_ELEMENT_VALIDATOR.match(self.get_suffix_provider())):
            raise DOIParserException('DOI suffix contains a character not allowed.')
        if not (DOI._SUFFIX_ELEMENT_VALIDATOR.match(self.get_suffix_element())):
            raise DOIParserException('DOI suffix contains a character not allowed.')

    def get_prefix(self):
        """
        :return: The prefix of the DOI.
        """
        return self._prefix

    def get_suffix_provider(self):
        """
        :return: The provider sub suffix of the DOI.
        """
        return self._suffix_provider

    def get_suffix_element(self):
        """
        :return: The element sub suffix of the DOI.
        """
        return self._suffix_element

    def get_uri(self):
        """
        :return: The uri associated of the DOI.
        """
        return self._uri

    def set_uri(self, uri):
        self._uri = uri

    def is_published(self):
        """
        :return: True if this DOI exist in the DOIs register else False.
        """
        raise Exception('Not yet implemented.')

    @staticmethod
    def doi_from_string(doi):
        """
        Make a DOI object from a string, supported formats: 'prefix/suffix_provider/suffix_element', '.../prefix/suffix_provider/suffix_element'.
        :param string doi: The string to parse as a DOI object
        :raises: DOIParserException: If the DOI object cannot be created from the input.
        :return: DOI object.
        """

        # TODO adapt parsing to use _main_separator & _suffix_separator

        split = doi.split(DOI._PATH_SEPARATOR)

        if len(split) == 1:
            raise DOIParserException('The DOI "{0}" can not be parsed'.format(doi))

        # Remove eventual ending slash
        if len(split[-1]) == 0:
            split.pop()

        suffix_element = split.pop()
        suffix_provider = split.pop()
        prefix = split.pop()

        if suffix_element is None or len(suffix_element) < 1:
            raise DOIParserException('Second suffix can not be parsed from "{0}"'.format(doi))

        if suffix_provider is None or len(suffix_provider) < 1:
            raise DOIParserException('First suffix can not be parsed from "{0}"'.format(doi))

        if suffix_element is None or len(suffix_element) < 1:
            raise DOIParserException('Prefix can not be parsed from "{0}"'.format(doi))

        return DOI(prefix, suffix_provider, suffix_element)

    def __eq__(self, other):
        return self._prefix == other.get_prefix() and self._suffix_provider == other.get_suffix_provider() and self._suffix_element == other.get_suffix_element()

    def __str__(self):
        return unicode(str(self._prefix) + self._main_separator + str(self._suffix_provider) + self._suffix_separator + str(self._suffix_element))
