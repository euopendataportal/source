#!/bin/bash

source ckan_script_config.sh

if [[ $# -lt 1 ]] ; then
   echo "1 arguments are mandatory"
   echo "arg1 the CKAN api key"
   exit 1
fi

source ${CKAN_FOLDER}/bin/activate

echo "*****************************"
echo "*** Update CKAN publisher ***"
echo "*****************************"

if [[ ! -f ${CORPORATE_BODIES}  ]]; then
    echo "File $CORPORATE_BODIES not found!"
    exit 1
fi

paster --plugin=ckanext-ecportal ecportal update-publishers ${CORPORATE_BODIES} -c ${CKAN_INI}

echo "End"

