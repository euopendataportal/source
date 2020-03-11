#!/bin/bash

source ckan_script_config.sh
source ${CKAN_FOLDER}/bin/activate

# change the password of a user in arg1
if [[ $# -lt 1 ]] ; then
   echo "1 arguments are mandatory"
   echo "arg1 the username"
   exit
   fi

# Run the paster command, referencing the .ini file
paster --plugin=ckan user setpass $1 -c ${CKAN_INI}