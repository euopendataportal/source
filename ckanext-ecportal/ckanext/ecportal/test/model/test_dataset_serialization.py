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

import cPickle as pickle
import unittest

from datadiff.tools import assert_equal
from pylons import config

import ckanext.ecportal.lib.cache.redis_cache as redis_cache
from ckanext.ecportal.configuration.configuration_constants import CKAN_ECODP_URI_PREFIX, VIRTUOSO_HOST_NAME
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.test.virtuoso.common_constants import VIRTUOSO_HOST_NAME_AUTHENTICATED

uri_prefix_test = "http://data.europa.eu/88u/dataset/"
class TestDatasetSerialisation(unittest.TestCase):
    def setUp(self):
        self._original_config = config.copy()
        config[CKAN_ECODP_URI_PREFIX] = 'http://data.europa.eu/88u'
        config[VIRTUOSO_HOST_NAME] = 'http://192.168.56.102:8890/sparql'
        config[VIRTUOSO_HOST_NAME_AUTHENTICATED] = 'http://192.168.56.102:8890/sparql-auth'

    def test_ts_and_cache_equality(self):
        name_or_id = uri_prefix_test + "dgt-translation-memory-V1-2"
        ts_dataset = None  # type: DatasetDcatApOp
        cache_dataset = None  # type: DatasetDcatApOp
        ts_dataset = DatasetDcatApOp(name_or_id)
        ts_dataset.get_description_from_ts()
        dataset_string = redis_cache.get_from_cache(name_or_id, pool=redis_cache.DATASET_POOL)
        if dataset_string:
            cache_dataset = pickle.loads(dataset_string)
        assert_equal(ts_dataset.schema.__dict__, cache_dataset.schema.__dict__)
