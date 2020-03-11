#!/bin/bash
source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

# Purge all datasets marked as deleted for the one publisher
if [[ $# -ne 1 ]] ; then
   echo "Exactly 1 argument is mandatory: the publisher name (e.g.: estat)"
   exit
   fi

paster --plugin=ckanext-ecportal pub purge-datasets $1 -c ${CKAN_INI}