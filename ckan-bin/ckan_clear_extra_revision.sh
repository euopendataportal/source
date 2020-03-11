#!/bin/bash

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

# the next line is only required if cleaning up a EU ODP release 08.00.0x database
# paster --plugin=ckanext-ecportal ecportal purge-task-data -c $CKAN_INI
paster --plugin=ckanext-ecportal ecportal purge-package-extra-revision -c ${CKAN_INI}
