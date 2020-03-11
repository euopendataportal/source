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
import sys, os

version = '2.2.2.1'

entry_points= {
        # Add plugins here and execute 'python setup.py develop'
        # to make them appear in .egg-info/entry_points.txt
        'ckan.plugins' : [
            'ecportal = ckanext.ecportal.plugin:ECPortalPlugin',
            'ecportal_controller_dataset = ckanext.ecportal.controllers.dataset:ECPortalDatasetController',
            'ecportal_controller_resource = ckanext.ecportal.controllers.dataset:ECPortalResourcePlugin',
            'ecportal_forms = ckanext.ecportal.forms:ECPortalDatasetForm',
             'ecportal_publisher_form = ckanext.ecportal.forms:ECPortalPublisherForm',
            'ecportal_multilingual_dataset = ckanext.ecportal.multilingual.plugin:ECPortalMultilingualDataset',
             'ecportal_multilingual_tag = ckanext.ecportal.multilingual.plugin:ECPortalMultilingualTag',
            'ecportal_multilingual_group = ckanext.ecportal.multilingual.plugin:ECPortalMultilingualGroup',
            'ecportal_facets = ckanext.ecportal.facets:ECPortalFacets',
            'ecportal_homepage = ckanext.ecportal.homepage:ECPortalHomepagePlugin',
            'rdft = ckanext.ecportal.plugin:RDFTPlugin',
            'ecportal_logout = ckanext.ecportal.controllers.logout_plugin:ECODPLogoutPlugin',
            'ecportal_group = ckanext.ecportal.controllers.group_plugin:ECODPGroupPlugin',
            'ecportal_datapusher = ckanext.ecportal.controllers.ecodp_datapusher_plugin:ECODPDatapusherPlugin',
            'ecportal_datastore = ckanext.ecportal.controllers.ecodp_datastore_plugin:ECODPDatastorePlugin',
            'ecportal_clear_cache_middleware = ckanext.ecportal.configuration.cache_clear_middleware:ECPortalCacheClearMiddelware'
        ],
        'paste.paster_command': [
            'pub = ckanext.ecportal.lib.cli:ManagePublisher',
            'ecportal=ckanext.ecportal.commands:ECPortalCommand',
            'tracking=ckanext.ecportal.lib.cli:Tracking',
            'search-index=ckanext.ecportal.lib.cli:SearchIndexCommand',
            'sync_download_views=ckanext.ecportal.lib.cli:SyncViewAndDownloadCount',
            'migrate_to_virtuoso=ckanext.ecportal.lib.cli:MirgateDcatToVirtuoso',
            'update_estat_datasets=ckanext.ecportal.lib.cli:UpdateEstatDatasets',
            'mapping_table=ckanext.ecportal.lib.cli:MappingTable',
            'update_statistics_duplicated_datatset=ckanext.ecportal.lib.cli:UpdateStatisticsDuplicated',
            'prefill_voc_cache=ckanext.ecportal.lib.cli:PrefilRedisCacheWithControlledVocabulary',
            'fix_all_incorrect_issued_date=ckanext.ecportal.lib.cli:Fix_all_incorrect_issued_date'
        ],
    }

setup(
    name='ckanext-ecportal',
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
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.ecportal'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points = entry_points
)
