#!/bin/bash
# ARG1 = the username of the sys admin user.

# This script creates a valid EU ODP empty CKAN database.
source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

if [[ $# -lt 1 ]] ; then
   echo "1 arguments are mandatory"
   echo "arg1 the username of the sysadmin"
   exit
   fi

paster --plugin=ckan db clean -c ${CKAN_INI}
paster --plugin=ckan db init  -c ${CKAN_INI}
# erase the file storage for CKAN UI and RDF2CKAN
rm -rf ${CKAN_FOLDER}/var/file-storage/*
rm -rf ${CKAN_FOLDER}/var/uploads/*
paster --plugin=ckanext-ecportal ecportal update-all-vocabs -c ${CKAN_INI}
paster --plugin=ckanext-ecportal ecportal update-publishers -c ${CKAN_INI}
paster --plugin=ckanext-ecportal search-index rebuild -c ${CKAN_INI}
paster --plugin=ckanext-ecportal ecportal searchcloud-install-tables -c ${CKAN_INI}
paster --plugin=ckanext-ecportal ecportal import-csv-translations -c ${CKAN_INI}
paster --plugin=ckanext-ecportal ecportal import-csv-translations-licence -c ${CKAN_INI}
paster --plugin=ckanext-ecportal search-index rebuild -c ${CKAN_INI}

# create a new user

# Run the paster command, referencing the .ini file
paster --plugin=ckan sysadmin add $1 -c ${CKAN_INI}
paster --plugin=ckan user $1 -c ${CKAN_INI}

