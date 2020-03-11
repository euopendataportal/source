#!/bin/bash

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

paster --plugin=ckanext-ecportal search-index rebuild -c ${CKAN_INI} --force
