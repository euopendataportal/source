from setuptools import setup, find_packages
import sys, os

version = '1.0.0'

entry_points= {
        # Add plugins here and execute 'python setup.py develop'
        # to make them appear in .egg-info/entry_points.txt

    }

setup(
    name='mdr-framework',
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
    packages=['odp_common', 'odp_common.mdr', 'test'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points = entry_points
)
