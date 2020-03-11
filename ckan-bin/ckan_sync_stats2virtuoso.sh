#!/bin/bash

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

paster --plugin=ckanext-ecportal sync_download_views download_count -c ${CKAN_INI}

paster --plugin=ckanext-ecportal sync_download_views views -c ${CKAN_INI}

