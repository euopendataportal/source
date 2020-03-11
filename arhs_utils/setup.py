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

from setuptools import setup
import sys, os

version = '1.0.0'

entry_points= {
        # Add plugins here and execute 'python setup.py develop'
        # to make them appear in .egg-info/entry_points.txt

    }

setup(
    name='ecodp-utils',
    version=version,
    description="CKAN EU Open Data Portal Extension",
    long_description='''
    ''',
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Publications Office',
    author_email='OP.Project-ODP@arhs-cube.Com',
    url='http://data.europa.eu/euodp',
    license='AGPL',
    packages=['arhs_utils', 'arhs_utils.arhs_email', 'arhs_utils.xslt'],
    #namespace_packages=['doi_facade', 'exceptions', 'generator', 'repository', 'submission'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points = entry_points
)
