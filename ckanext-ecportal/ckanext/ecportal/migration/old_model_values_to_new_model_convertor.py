# -*- coding: utf-8 -*-
#    Copyright (C) <${YEAR}>  <Publications Office of the European Union>
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
from ckanext.ecportal.migration.value_mapping_for_old_model import *
from ckanext.ecportal.migration.datasets_migration_manager import ControlledVocabulary
from ckanext.ecportal.migration.value_mapping_for_old_model import MAPPING
import traceback

log = logging.getLogger(__file__)



class OldModelValuesToNewModelConvertor(object):

    def __init__(self,old_model_dataset_dict):
        '''
        :param dict old_model_dataset_dict:
        '''
        self.__old_values_dict = old_model_dataset_dict # type: dict
        self.__transformed_values_dict = {} # type: dict

        # self.controlled_vocabulary = ControlledVocabulary()

    def __mdr_based_conversion_one_value(self, old_model_value, property_controlled_vocabulary):
        '''

        :param old_model_value:
        :param property_controlled_vocabulary:
        :rtype: str
        '''

        def string_similarity(string_value1, string_value2):
            '''

            :param str string_value1:
            :param str string_value2:
            :rtype: Boolean
            '''
            try:
                similarity = False
                if string_value1 == string_value2:
                    similarity = True
                # TODO other similarities maight be implemented
                compared_string1 = string_value1
                if '/' in string_value1:
                    compared_string1 = string_value1.split('/')[-1]
                if compared_string1 and '/' in string_value2:
                    if compared_string1.upper() == string_value2.split('/')[-1].upper():
                        similarity = True
                return similarity
            except BaseException as e:
                return False

        # check the similarity with the mdr uris
        transformed_value = None
        for mdr_uri in property_controlled_vocabulary:
            if string_similarity(old_model_value, mdr_uri):
                transformed_value = mdr_uri
                break
        return transformed_value

    def __dictionary_based_conversion_one_value(self, old_value, dict_mapping):
        '''
        The mapping uses a dictionary in which the old_value is the key of the dict.
        If it not possible to use the old_value as a key, we try to find a recommended key based on the approach used
        in migration -> mapping_key in old_value.

        :param self:
        :param str old_values:
        :param dict_mapping:
        :rtype:list
        '''
        def get_key_of_mapping_dict(old_value, dict_mapping):
            recommended_key = old_value
            if old_value not in dict_mapping:
                recommended_key = next((key for key in dict_mapping if key.lower() in old_value.lower()), old_value)
            return recommended_key

        try:

            recommended_key = get_key_of_mapping_dict(old_value,dict_mapping)
            transformed_values = dict_mapping.get(recommended_key, None)
            return transformed_values
        except BaseException as e:
            log.error("Dictionary based converison failed for {0}".format(old_value))
            log.error(traceback.print_exc(e))
            return None

    def __old_value_transformation_one_value(self,old_model_value, property_controlled_vocabulary, property_mapping_dictionary, property_name =None):
        '''
        Provides the converison of old value using three posible transformation approachs: mdr, dictionary and fallback
        return a
        :param str old_model_value:
        :param dict property_controlled_vocabulary:
        :param dict property_mapping_dictionary:
        :rtype: list
        '''

        try:
            #     start by the mdr mapping
            transformed_value = None
            if property_controlled_vocabulary is not None:
                transformed_value = self.__mdr_based_conversion_one_value(old_model_value,property_controlled_vocabulary)
            # try with dictionary based approach
            if transformed_value is None:
                if property_mapping_dictionary is not None:
                    transformed_value = self.__dictionary_based_conversion_one_value(old_model_value,property_mapping_dictionary)
            if transformed_value is None:
                transformed_value = self.__fallback(old_model_value, property_name)

            if not isinstance(transformed_value,list):
                transformed_value = [transformed_value]

            return transformed_value

        except BaseException as e:
            log.error("Transformation of old values failed for {0}".format(old_model_value))
            log.error(traceback.print_exc(e))
            return None

    def old_value_transformation_one_value_of_property (self, old_model_value, property_name):
        """

        :param property_name:
        :return:
        """
        property_controlled_vocabulary = MAPPING.get(property_name, {}).get(CONTROLLED_VOC, None)
        property_mapping_dictionary = MAPPING.get(property_name, {}).get(VALUES_MAPPING, None)
        transformed_value = self.__old_value_transformation_one_value(old_model_value, property_controlled_vocabulary, property_mapping_dictionary)

    def __old_values_transformation_list(self, old_model_values, property_controlled_vocabulary, property_mapping_dictionary,property_name = None):
        '''
        Provides the converion of old value using three posible transformation approachs: mdr, dictionary and fallback
        Returns a list of transformed values
        :param old_model_values:
        :param property_controlled_vocabulary:
        :param property_mapping_dictionary:
        :rtype: list
        '''
        try:
            transformed_values = []
            old_values = old_model_values
            for old_model_value in old_values:
                transformed_value = self.__old_value_transformation_one_value(old_model_value,property_controlled_vocabulary,property_mapping_dictionary, property_name)
                if transformed_value is not None:
                    transformed_values.extend(transformed_value)
            transformed_values = list(set(transformed_values))
            return transformed_values
        except BaseException as e:
            log.error("Transformation of old values failed.{0}".format(old_model_values))
            log.error(traceback.print_exc(e))
            return None

    def __transformation_old_values_of_property(self, property_name, list_values=None):
        '''

        :param dict old_values_dict:
        :param str property_name:
        :rtype:list
        '''
        list_old_values = list_values
        if list_old_values is None:
            list_old_values = self.__old_values_dict.get(property_name, None)
        if list_old_values is None:
            return None
        is_old_value_type_list = True
        if not isinstance(list_old_values,list):
            list_old_values = [list_old_values]
            is_old_value_type_list = False
        property_controlled_vocabulary = MAPPING.get(property_name,{}).get(CONTROLLED_VOC,None)
        property_mapping_dictionary = MAPPING.get(property_name,{}).get(VALUES_MAPPING,None)

        list_transformed_values = self.__old_values_transformation_list(list_old_values,property_controlled_vocabulary,property_mapping_dictionary, property_name)

        if list_transformed_values is not None:
            if not is_old_value_type_list:
                if len(list_transformed_values) == 1:
                    list_transformed_values = list_transformed_values[0]

        return list_transformed_values


    def full_transformation_old_values_of_property(self,property_name, list_values=None):
        """

        :param property_name:
        :return:
        """
        transformed_values = []
        if property_name =="groups":
            transformed_values = self.__eurovoc_to_theme()
        else:
            transformed_values = self.__transformation_old_values_of_property(property_name, list_values)

        return transformed_values



    def __fallback(self, old_value, property_name = None):
        # TODO ADD default value otherwise return the same value
        fallback_value = old_value
        if property_name is not None:
            defaul_value = MAPPING.get(property_name,{}).get(DEFAULT_VALUE,None)

            if defaul_value is not None:
                fallback_value = defaul_value

        return fallback_value

    def __eurovoc_to_theme(self):
        '''
        Create the them values in the case of eurovoc wuth the special structure
        :return:
        '''
        property_name = "groups"
        property_controlled_vocabulary = MAPPING.get(property_name, {}).get(CONTROLLED_VOC, None)
        property_mapping_dictionary = MAPPING.get(property_name, {}).get(VALUES_MAPPING, None)
        groups = self.__old_values_dict.get(property_name,[])
        transformed_groups = []
        eurovoce_domain_set = [eurovoc['title'] for eurovoc in groups if eurovoc.get('title', '')]
        transformed_themes = self.__old_values_transformation_list(eurovoce_domain_set,property_controlled_vocabulary,property_mapping_dictionary,property_name)  # type: list
        # add default value of eurovoc domain
        if not transformed_themes:
            transformed_themes.append(MAPPING.get('groups').get(DEFAULT_VALUE))

        # build the groups with transformed values and keep the other groups 'name'
        for theme in transformed_themes:
            transformed_groups.append({"title":theme})
        for group in groups:
            if group.get("name"):
                transformed_groups.append(group)

        return transformed_groups

    def full_transformation_of_dict(self):
        """
        Transform the whole dict
        :return: dict
        """

        try:
            list_properties_dataset=["groups", "status", "type_of_dataset", "accrual_periodicity"]
            list_properties_resource=["resource_type", "format"]

            self.__transformed_values_dict.update(self.__old_values_dict)
            self.__transformed_values_dict["groups"] = self.__transformed_values_dict.get("groups", [])  # to forece having at lezast the element groups in order to add default value
            for prop in list_properties_dataset:
                if self.__transformed_values_dict.has_key(prop):
                    self.__transformed_values_dict[prop] = self.full_transformation_old_values_of_property(prop)

            list_resources = self.__transformed_values_dict.get("resources", [])
            for resource in list_resources:  # type: dict
                for prop in list_properties_resource:
                    if resource.has_key(prop):
                        list_values = resource.get(prop)
                        resource[prop] = self.full_transformation_old_values_of_property(prop, list_values)
                    else:
                        # add default values by creating the missed properties
                        resource[prop] = MAPPING.get(prop).get(DEFAULT_VALUE)

            return self.__transformed_values_dict

        except BaseException as e:
            log.error("Transformation of old model failed. {0}".format(self.__old_values_dict))
            log.error(traceback.print_exc(e))
            return None
