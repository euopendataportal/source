#!/bin/bash

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

paster --plugin=ckan db upgrade -c ${CKAN_INI}


