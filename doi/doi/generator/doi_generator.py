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
from doi.mapper.mapping_value_service import MappingValue


class DOIGenerator:

    def __init__(self, controller, doi_prefix):
        self._controller = controller
        self._prefix = doi_prefix

    def _generate_new_doi(self, prefix, provider, suffix):
        """
        Generate a DOI from a prefix and a provider.
        :param str prefix: The prefix of the DOI.
        :param str provider: The provider of the DOI.
        :param str suffix: The second suffix of the DOI.
        :return: The obtained DOI.
        """
        if suffix is None:
            return self._controller.next_doi(prefix, provider)
        else:
            doi = DOI(prefix, provider, suffix)
            if self._controller.doi_exists(doi):
                raise Exception('Cannot override an existing DOI association')

            self._controller.set_doi_association(doi)
            return doi

    def _get_doi(self, prefix, provider, uri, suffix):
        """
        Get a DOI from a prefix, a provider and a URI, generate it if needed.
        :param str prefix: The prefix of the DOI.
        :param str provider: The provider of the DOI.
        :param str uri: The URI of the data to identify.
        :param str suffix: The second suffix of the DOI.
        :return: The obtained DOI.
        """
        doi = self._controller.get_doi_by_uri(uri)
        if doi is None:
            doi = self._generate_new_doi(prefix, provider, suffix)
            self._controller.set_doi_association(doi, uri)
        return doi

    def generate(self, provider, uri=None, suffix=None):
        """
        Give a DOI from a provider and optionally from a URI. This DOI is generated if needed. This DOI must not exist.
        :param str provider: The Data Provider associated.
        :param str uri: The URI of the data that will be associated to the DOI.
        :param str suffix: The second suffix of the DOI.
        :raises Exception: If the DOI can not be obtained.
        :return: The generated DOI.
        """
        provider_numerical = MappingValue.mapping_from_odp_publisher_id_to_doi_publisher_numerical_id(provider)
        provider = provider_numerical
        doi = self._generate_new_doi(self._prefix, provider, suffix) if uri is None else self._get_doi(
            self._prefix, provider, uri, suffix)

        return doi
