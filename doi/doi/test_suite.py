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

from facade.tests import doi_facade_test
from generator.tests import test_generator
from reporting.service.tests import report_service_test
from storage.tests import test_doi_storage
from submission.tests import doi_submission_service_test


loader = unittest.TestLoader()
suite = unittest.TestSuite()


suite.addTests(loader.loadTestsFromModule(doi_facade_test))

suite.addTests(loader.loadTestsFromModule(test_generator))

suite.addTests(loader.loadTestsFromModule(report_service_test))

suite.addTests(loader.loadTestsFromModule(test_doi_storage))

suite.addTests(loader.loadTestsFromModule(doi_submission_service_test))


runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
