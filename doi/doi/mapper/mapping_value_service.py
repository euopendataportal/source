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

from doi.exceptions.doi_mapper_exception import DOIMapperException
class MappingValue():
    """
    Manage the mapping between values used in the DOI service.
    The mapping is based on two ideas; a function based dynamic conversion, or dictionary based approach
    
    """

    def __init__(self):
        pass

    @classmethod
    def mapping_from_odp_publisher_id_to_doi_publisher_numerical_id(cls, publisher_odp_id_str):
        """
        Get the numerical doi id of the publisher from the odp publisher one.
        :param publisher_odp_id_str: 
        :return: 
        """

        if isinstance(publisher_odp_id_str,unicode) or isinstance(publisher_odp_id_str,str):
            return cls()._get_numerical_value_of_string(publisher_odp_id_str)
        else:
            raise DOIMapperException("publisher_odp_id is not a string")

    @classmethod
    def mapping_from_doi_publisher_numerical_id_to_odp_publisher_id(cls, publisher_doi_id_numerical):
        """
        Get the ODP publisher id  of th publisher using the corresponding DOI pulisher id 
        :param publisher_doi_id_numerical: 
        :return str: 
        """
        if isinstance(publisher_doi_id_numerical,unicode) or isinstance(publisher_doi_id_numerical,str):
            try:
                return cls()._get_inverse_of_ascii_numerical_value(publisher_doi_id_numerical)
            except DOIMapperException as e:
                raise DOIMapperException(e.message)
        else:
            raise DOIMapperException("publisher_doi_id_numerical is not string")


    def _get_numerical_value_of_string(self, string_value):
        """
        Implement an ascii conversion of a string. each char is converted to a corresponding 3 digits ascii code. 
        Ex: 'ODP' is converted to 079068080 
        :param str string_value:
        :return:
        """
        num_ascii_value = ""
        for c in string_value:
            str_ord = str(ord(c))
            if ord(c) > 99:
                num_ascii_value += str_ord
            if 9 < ord(c) < 100:
                num_ascii_value += "0" + str_ord
            if 0 <= ord(c) < 10:
                num_ascii_value += "00" + str_ord
        return num_ascii_value

    def _get_inverse_of_ascii_numerical_value(self, ascii_numerical_value):
        """
        Get the string value of the ascii code 
        :param str ascii_numerical_value:
        :return:
        """
        number_of_chars = len(ascii_numerical_value) / 3
        mod = len(ascii_numerical_value) % 3

        if mod != 0:
            raise DOIMapperException("The size of the ascii_numerical_value is not modulo 3")
        start = 0
        end = 3
        string_value_of_ascii = ""
        for i in range(0, number_of_chars):
            ascii_chars = ascii_numerical_value[start:end]
            char = chr(int(ascii_chars))
            string_value_of_ascii += char
            start += 3
            end += 3
        return string_value_of_ascii
