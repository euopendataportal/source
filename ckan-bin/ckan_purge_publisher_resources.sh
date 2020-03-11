#!/bin/bash

source ckan_script_config.sh

# clear the publisher content
if [[ $# -lt 2 ]] ; then
   echo "2 arguments are mandatory"
   echo "arg1 the CKAN publisher id"
   echo "arg2 the CKAN api key"
   exit
   fi

JSON="{\"group\":\"$1\"}"

curl ${DOMAIN}/data/api/action/purge_revision_history -H "Authorization: $2" -d "$JSON"


