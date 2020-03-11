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

from setuptools import setup, find_packages

version = '0.1'

setup(
    name='ckanext-sitemap',
    version=version,
    description="Sitemap extension for CKAN",
    long_description="""\
	""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Aleksi Suomalainen',
    author_email='aleksi.suomalainen@nomovok.com',
    url='https://github.com/locusf/ckanext-sitemap',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.sitemap'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    setup_requires=[
        'nose'
    ],
    entry_points= {
        'paste.paster_command': [
            'sitemap = ckanext.sitemap.commands:InitSitemapFiles'
        ],
        'ckan.plugins': [
            'sitemap = ckanext.sitemap.plugin:SitemapPlugin'
        ]
    }
)
