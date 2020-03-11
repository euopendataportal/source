#!/bin/bash
# ckan_rdf_export triggers the CKAN plugin to generate the RDF dumps of
# the CKAN database

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

# the target directory
if [[ $# -gt 1 ]] ; then
   echo "Too many arguments"
   echo "arg1 the target directory (optional)"
   exit
   fi
if [[ $# -eq 1 ]] ; then
    TARGET_DIR=$1
else
    TARGET_DIR=${CKAN_FOLDER}/ckan2ts/work/rdf
fi

# ensure the target dir exists
mkdir -p ${TARGET_DIR}

if [[ ! -e ${CKAN_INI} ]] ; then
    echo "Incorrect location of the CKAN ini file"
    exit
    fi

paster --plugin=ckan rdf-export -c ${CKAN_INI} ${TARGET_DIR}



