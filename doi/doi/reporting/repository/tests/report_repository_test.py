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

from doi.repository.doi_repository import DOIRepository


class DOIRepositoryTest(unittest.TestCase):

    _TEST_DOI = "test/doi-1"

    _doi_repository = DOIRepository()

    def setUp(self):
        self._doi_repository.delete_all()

    def test_save(self):
        generated_doi = self._doi_repository.save(self._TEST_DOI)
        self.assertNotEquals(None, self._doi_repository.find(generated_doi))

    def test_find(self):
        generated_doi = self._doi_repository.save(self._TEST_DOI)
        self.assertNotEquals(None, self._doi_repository.find(generated_doi))
        self.assertEquals(None, self._doi_repository.find('some/unstored-DOI'))

    def test_find_last(self):
        generated_doi = self._doi_repository.save(self._TEST_DOI)
        self.assertNotEquals(generated_doi, self._doi_repository.find_last())

    def test_delete(self):
        generated_doi = self._doi_repository.save(self._TEST_DOI)
        self.assertNotEquals(None, self._doi_repository.find(generated_doi))
        self._doi_repository.delete(generated_doi)
        self.assertEquals(None, self._doi_repository.find(generated_doi))

    def tearDown(self):
        self._doi_repository.delete_all()


if __name__ == '__main__':
    unittest.main()
