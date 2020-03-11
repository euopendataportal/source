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

from doi.submission.doi_submission_service import DOISubmissionService


class DOISubmissionServiceTest(unittest.TestCase):

    # TODO complete

    def test_register_with_wrong_agency(self):
        _submission_service = DOISubmissionService('wrong_agency', 'user', 'password')
        submission_result = _submission_service.register_doi('wrong metadata')
        self.assertEquals(500, submission_result.status)


if __name__ == '__main__':
    unittest.main()

