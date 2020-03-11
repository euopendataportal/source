#!/bin/bash
source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

paster --plugin=ckanext-ecportal tracking update -c ${CKAN_INI}
paster --plugin=ckanext-ecportal search-index rebuild -r -c ${CKAN_INI}
