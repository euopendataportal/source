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

import unittest
import requests
import ujson as json

from threading import Thread

class Test_UI_Util(unittest.TestCase):


    DATA_DICT = {'http://data.europa.eu/88u/dataset/h7zt7sbbIPHzY0Yz7pIcwQ': ['http://data.europa.eu/88u/document/b91f1fa3-cee0-41b9-a8ad-8d91f51a32b1',
                                                                            'http://data.europa.eu/88u/document/4e5c8bf6-cabf-499e-a241-0f1a97ac35c3',
                                                                            'http://data.europa.eu/88u/document/39c8c961-9c7b-4db6-9833-5f5298724578'],
                 'http://data.europa.eu/88u/dataset/DAP7Y7IUFjzSgvAGIYxw': ['http://data.europa.eu/88u/document/30ff822a-b953-4384-8ef8-791c12705a56',
                                                                            'http://data.europa.eu/88u/document/4c69119e-aea5-4819-9fb1-02f4a27222a4',
                                                                            'http://data.europa.eu/88u/document/ecb7e24d-f1e5-4d6c-aa93-93a12feb1571'],
                 'http://data.europa.eu/88u/dataset/wZu23iFi9uH1wFYNKDCp1g': ['http://data.europa.eu/88u/distribution/140d3a74-1c4b-413f-9fe9-ec45e35968e9',
                                                                            'http://data.europa.eu/88u/distribution/cb4f077c-67db-4a22-9478-7e5eca6d5b18'],
                 'http://data.europa.eu/88u/dataset/n27Lzmv6k7fiOkXkvi0FA': ['http://data.europa.eu/88u/distribution/78e59891-e7a7-485f-92f2-ead1188ce1ad']}

    def test_download_count_action(self):

        for key, value in self.DATA_DICT.iteritems():
            Thread(target=self._loop_function, args=(key,value)).start()


    def _loop_function(self, key, value):
        for res in value:
            count = 20
            while count > 0:
                r = requests.post("http://192.168.56.101:5000/api/action/count_download", data=json.dumps({'ds_uri': key, 'rs_uri': res}), headers={'Content-Type':'application/json'})

                print(r.status_code, r.reason)
                count -= 1