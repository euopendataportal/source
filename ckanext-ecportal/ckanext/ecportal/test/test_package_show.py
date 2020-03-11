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

import ckan.logic as logic

from nose.tools import *


class Test_package_show(unittest.TestCase):
    @raises(logic.NotFound)
    def package_show_not_existin_id_test(self):
        context = {'user': 'localhost', 'for_view': False}
        data_dict = {'uri': 'http://data.europa.eu/999/dataset/no-never-existing-id-test'}

        logic.get_action('package_show')(context, data_dict)
        # ecportal_get.package_show(context, data_dict)

    @raises(logic.NotFound)
    def package_show_empty_id_test(self):
        context = {'user': 'localhost', 'for_view': False}
        data_dict = {'id': 'http://data.europa.eu/999/dataset/no-never-existing-id-test'}

        logic.get_action('package_show')(context, data_dict)

    def package_show_test(self):
        context = {'user': 'localhost', 'for_view': False}
        data_dict = {'uri': 'http://data.europa.eu/88u/dataset/dgt-translation-memory-V1-2'}

        pkg = logic.get_action('package_show')(context, data_dict)
        # ecportal_get.package_show(context, data_dict)

        self.assertNotEqual(pkg, None)


if __name__ == '__main__':
    unittest.main()
