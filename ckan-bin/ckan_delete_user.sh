#!/bin/bash

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh


# create a new user for arg1
if [[ $# -lt 1 ]] ; then
   echo "1 arguments are mandatory"
   echo "arg1 the username"
   exit
   fi

# Run the paster command, referencing the .ini file
paster --plugin=ckan user remove $1 -c ${CKAN_INI}
