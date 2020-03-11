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

import logging, codecs
from ckanext.ecportal.test.virtuoso.test_with_virtuoso_configuration import TestWithVirtuosoConfiguration
logging.basicConfig(level=logging.DEBUG)
from ckanext.ecportal.virtuoso.utils_triplestore_crud_core import VirtuosoCRUDCore
from ckanext.ecportal.migration.old_model_values_to_new_model_convertor import *
import json
vsc = VirtuosoCRUDCore()

# build the data for the test

test_folder_path = "/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/ckanext/ecportal/test/data/"
class TestOldModelValuesToNewModelConvertor(TestWithVirtuosoConfiguration):

    def setUp(self):
        # vsc = VirtuosoCRUDCore()

        pass


    def test_full_transformation_old_values_of_property(self):
        # dictionary based mapping with 1 to many




        dict = {

            "groups": [
                    {'title': 'http://eurovoc.europa.eu/100150'},
                    {'title': 'http://eurovoc.europa.eu/100158'},
                    {'title': 'http://eurovoc.europa.eu/100149'},
                    {'title': 'http://eurovoc.europa.eu/100151'},
                    {'title': 'http://eurovoc.europa.eu/100157'},
                    {'title': 'http://eurovoc.europa.eu/100152'},
                    {'title': 'http://eurovoc.europa.eu/100161'},
                    {'title': 'http://eurovoc.europa.eu/100144'},
                    {'title': 'http://eurovoc.europa.eu/100155'},
                    {'title': 'http://eurovoc.europa.eu/100142'},
                    {'title': 'http://eurovoc.europa.eu/100153'},
                    {'title': 'http://eurovoc.europa.eu/100159'},
                    {'title': 'http://eurovoc.europa.eu/100154'},
                    {'title': 'http://eurovoc.europa.eu/100162'},
                    {'title': 'http://eurovoc.europa.eu/100160'},
                    {'title': 'http://eurovoc.europa.eu/100145'},
                    {'title': 'http://eurovoc.europa.eu/100156'},
                    {'title': 'http://eurovoc.europa.eu/100143'},
                    {'title': 'http://eurovoc.europa.eu/100148'},
                    {'title': 'http://eurovoc.europa.eu/100146'},
                    {'title': 'http://eurovoc.europa.eu/100147'}
                    ],
        }


        transformer = OldModelValuesToNewModelConvertor(dict)
        transformed_values_eurovoc = transformer.full_transformation_old_values_of_property("groups")

        self.assertEqual(len(transformed_values_eurovoc),13,"Eurovoc domain transformation failed  are not translated. Dictionary based")


        dict = {
        "groups":[
            {'title': 'http://publications.europa.eu/resource/authority/data-theme/ENVI'},
            {'title': 'http://publications.europa.eu/resource/authority/data-theme/AGRI'},
            {'title':'NONO'}
            ]
        }
        transformer = OldModelValuesToNewModelConvertor(dict)
        transforme_new_value = transformer.full_transformation_old_values_of_property("groups")

        exist_agri = {"title":"http://publications.europa.eu/resource/authority/data-theme/AGRI"} in transforme_new_value
        exist_gove = {"title":"http://publications.europa.eu/resource/authority/data-theme/GOVE"} in transforme_new_value

        exist_new_eurovoc = exist_agri and exist_gove
        self.assertTrue(exist_new_eurovoc, "Transformattion new values failed")


        # MDR based mapping
        dict_format = {'format':"zIp"}
        transformer = OldModelValuesToNewModelConvertor(dict_format)
        transformed_values_file_format = transformer.full_transformation_old_values_of_property("format")
        self.assertEqual(transformed_values_file_format,"http://publications.europa.eu/resource/authority/file-type/ZIP", "Transformation of value failed, Mdr based ")

        # Dictionary based mapping 1 to 1
        dict_format = {'format':"application/rss+xml"}
        transformer = OldModelValuesToNewModelConvertor(dict_format)
        transformed_values_file_format = transformer.full_transformation_old_values_of_property("format")
        self.assertEqual(transformed_values_file_format,
                         "http://publications.europa.eu/resource/authority/file-type/RSS",
                         "Transformation of value failed, Dictionary mapping 1to1 ")

        # test the recommended key for mapping
        dict_distribution_type = {'resource_type': "http://.blabla.feed_blabla"}
        transformer = OldModelValuesToNewModelConvertor(dict_distribution_type)
        transformed_values_distribution_type = transformer.full_transformation_old_values_of_property('resource_type')
        self.assertEqual(transformed_values_distribution_type,"http://publications.europa.eu/resource/authority/distribution-type/FEED_INFO", "The recommended key for dictionary mapping failed")






        # test with complet file
        dataset_ckan_dict = {}
        with open(test_folder_path + "old_model_dataset.json") as f:
            dataset_ckan_dict = json.load(f)
        transformer = OldModelValuesToNewModelConvertor(dataset_ckan_dict)
        transformed_dict  = transformer.full_transformation_of_dict()
        assert (transformed_dict)
        pass


    def test_default_values(self):
        # test the default value
        dict_default_values = {"groups": [{"title":"I am not eurovoc"}],
                               "resource_type": "I am not resource type",
                               "format": "I am not format"
                               }

        transformer = OldModelValuesToNewModelConvertor(dict_default_values)
        transformed_default_format = transformer.full_transformation_old_values_of_property("format")
        transformed_default_resType = transformer.full_transformation_old_values_of_property("resource_type")
        transformed_default_groups = transformer.full_transformation_old_values_of_property("groups")

        self.assertEqual(transformed_default_format,DEFAULT_VALUE_FORMAT,"Transformation from old model. Default value for format failed")
        self.assertEqual(transformed_default_resType,DEFAULT_VALUE_DISTRIBUTION_TYPE,"Transformation from old model. Default value for resource type failed")
        self.assertEqual(transformed_default_groups, [{"title":DEFAULT_VALUE_DATATHEME}])

        # not initialized properties

        pass

    def test_add_default_values(self):

        # test without groups
        dataset_ckan_dict = {}
        with open(test_folder_path + "old_model_dataset_default_values.json") as f:
            dataset_ckan_dict = json.load(f)
        transformer = OldModelValuesToNewModelConvertor(dataset_ckan_dict)
        transformed_dict = transformer.full_transformation_of_dict()
        groups = transformed_dict.get('groups',[])
        self.assertEqual (len(groups),1)


        dataset_ckan_dict["groups"]= [{"name":" I am a group in db"}]
        transformer = OldModelValuesToNewModelConvertor(dataset_ckan_dict)
        transformed_dict = transformer.full_transformation_of_dict()
        groups = transformed_dict.get('groups', [])
        self.assertEqual(len(groups),2)


        dataset_ckan_dict["groups"] = [{"name": " I am a group in db"},{"title":"I am not eurovoc"}]
        transformer = OldModelValuesToNewModelConvertor(dataset_ckan_dict)
        transformed_dict = transformer.full_transformation_of_dict()
        assert (transformed_dict)






