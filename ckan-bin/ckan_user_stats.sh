#!/bin/bash
# Arg1 = absolute path to file where the stats are output to in CSV format
# Arg2 = date in the form [YYYY-MM-DD] from which point the stats are dumped
# Arg3 = optional date in the form [YYYY-MM-DD] to which point the stats are dumped. if not, actual date will be applied

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/paster.sh

if [[ $# -lt 2 ]] ; then
   echo "2 arguments are mandatory"
   echo "Arg1 = file where the stats are output to in CSV format"
   echo "Arg2 = date in the form [YYYY-MM-DD] from which point the stats are dumped"
   echo "Arg3 = optional date in the form [YYYY-MM-DD] to which point the stats are dumped. if not, actual date will be applied"
   exit
fi

if [[ $# -eq 3 ]]; then
	paster --plugin=ckanext-ecportal tracking export "$1" -c ${CKAN_INI} "$2" "$3"
else
	paster --plugin=ckanext-ecportal tracking export "$1" -c ${CKAN_INI} "$2"
fi
