#!/bin/bash

source ckan_script_config.sh
###########################################################################################################
###  Update the internal indicator on the openess of files according to Tim Berners Lee grid (ODP-539)  ###
###  [foreseen to be run by a cron job]                                                                  ###
###########################################################################################################

# Start the background worker if not already started yet
celeryd_processes=$(ps -f | grep "paster --plugin=ckan celeryd"  | wc -l)
echo "Porcesses containing 'paster --plugin=ckan celeryd' found: " $celeryd_processes

if (( $celeryd_processes <= 2 )); then
  echo "Start a new background worker processs"
  nohup ${CKAN_FOLDER}/bin/paster --plugin=ckan celeryd --config=${CKAN_INI} >> ${CKAN_FOLDER}/logs/celeryd.log 2>&1 &
fi


echo "Update the openess info"
${CKAN_FOLDER}/bin/paster --plugin=ckanext-qa qa update --config=${CKAN_INI}