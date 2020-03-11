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

from doi.domain.doi_object import DOI
import requests


class DOISController(object):

    def __init__(self, storage, citation_formats, citation_resolver, citation_file_resolver, citation_style):
        self._storage = storage
        self._citation_formats = citation_formats
        self._citation_resolver = citation_resolver
        self._citation_file_resolver = citation_file_resolver
        self._citation_style = citation_style

    def next_doi(self, prefix, provider):
        """
        Give the next available DOI.
        :param str prefix: The prefix of the DOI to generate.
        :param str provider: The provider of the data excepting a new DOI
        :return: The next available DOI.
        """
        return self._storage.next_doi(prefix=prefix, provider=provider)

    def get_doi_by_uri(self, uri):
        """
        Get a DOI from a given URI.
        :param str uri: The URI associated to the excepted DOI.
        :return: The DOI associated to the given URI if exists else None.
        """
        return self._storage.find_one(uri=uri)

    def get_uri_by_doi(self, doi):
        """
        Get a URI from a given DOI.
        :param DOI doi: The DOI associated to the excepted URI.
        :return: The URI associated to the given DOI if exists else None.
        """
        doi = self._storage.find_one(prefix=doi.get_prefix(), provider=doi.get_suffix_provider(), value=doi.get_suffix_element())
        if doi is None:
            return None
        return doi.get_uri()

    def doi_exists(self, doi):
        """
        Check if a DOI exist.
        :param DOI doi: The DOI associated to the excepted URI.
        :return: True if the DOI exist else False.
        """
        doi = self._storage.find_one(prefix=doi.get_prefix(), provider=doi.get_suffix_provider(), value=doi.get_suffix_element())
        return doi is not None

    def get_all_doi_association(self, **args):
        """
        Get all DOI associations.
        :param args: filter arguments.
        :return: All DOI associations filtered by arguments
        """
        return self._storage.find(**args)

    def set_doi_association(self, doi, uri=None):
        """
        Add an association of a DOI and a URI.
        :param DOI doi: The DOI to add.
        :param str uri: The URI to add.
        """
        if self.get_uri_by_doi(doi) is not None:
            raise Exception('Cannot override an existing DOI association')
        doi.set_uri(uri)
        self._storage.save(doi)

    def remove_association_by_uri(self, uri):
        """
        Remove the association of a DOI and a URI.
        :param str uri: The URI identifying the excepted association.
        """
        self._storage.delete(uri=uri)

    def remove_association_by_doi(self, doi):
        """
        Remove the association of a DOI and a URI.
        :param DOI doi: The DOI identifying the excepted association.
        """
        self._storage.delete(prefix=doi.get_prefix(), provider=doi.get_suffix_provider(), value=doi.get_suffix_element())

    def remove_all_doi(self, **args):
        """
        Remove the association of a DOI and a URI.
        :param args: arguments to filtering the DOIs to delete (example: prefix='test', provider='com').
        """
        self._storage.delete_all(**args)

    def get_citation(self, doi_str, language):
        """
        Get a formatted citation from a DOI.
        :param str doi_str: The DOI to find.
        :param str language: Language of the requested citation.
        :raises: Exception: If the Citation can not be obtained.
        :return: The formatted citation got by a DOI.
        """
        headers = {
            'Accept': 'text/x-bibliography'
        }
        params = {
            'doi': doi_str,
            'style': self._citation_style,
            'lang': language
        }

        request = requests.get(self._citation_resolver, headers=headers, params=params, verify=False)

        if request.status_code == 200:
            return request.content
        elif request.status_code == 204:
            raise Exception('The request was OK but there was no metadata available.')
        elif request.status_code == 404:
            raise Exception('The DOI requested doesn\'t exist.')
        else:
            raise Exception('The DOI citation failed to be got: {0}'.format(request.content))

    def download_citation(self, doi_str, style, language):
        """
        Get a downloadable citation from a DOI.
        :param str doi_str: The DOI to find.
        :param str style: Style of the requested citation.
        :param str language: Language of the requested citation.
        :raises: Exception: If the Citation can not be obtained.
        :return: A dict containing the result content as "content", the content type as "type" and the filename as "filename"
        """
        _format = self._citation_formats[style]['format']

        headers = {
            'Accept': _format
        }
        params = {
            'lang': language
        }

        response = requests.get(self._citation_file_resolver + doi_str, headers=headers, params=params, verify=False, stream=True)
        filename = doi_str + "." + self._citation_formats[style]['extension']

        if response.status_code != 200:
            raise Exception('The DOI citation failed to be loaded: {0}'.format(response.reason))

        if _format != 'text/html' and response.text.lower().replace(' ', '').replace('\n', '').startswith('<!doctypehtml>'):
            raise Exception('The DOI citation failed to be loaded: response format is not the excepted one. ({0})'.format(_format))

        return {
            'content': response.content,
            'type': self._citation_formats[style]['format'],
            'filename': filename
        }
