#!/bin/bash

source ckan_script_config.sh

# ARG1 = the rdf file containing the new corporate bodies.
if [[ $# -lt 1 ]] ; then
   echo "1 arguments are mandatory"
   echo "arg1 the rdf file containing the new corporate bodies"
   exit
   fi

CKAN_PUB=${CKAN_FOLDER}/conf/ckan_publishers.json
HIERARCHY=${CKAN_FOLDER}/conf/ckan_publishers_hierarchy.json

echo "************************************"
echo "*** Creating publisher json file ***"
echo "************************************"

roqet -D $1 -i sparql ${CKAN_FOLDER}/conf/nal_query.rq -r json > ${CKAN_PUB}

sed -i -e "s/\(^.*\"label.*\),/\1 } , /" ${CKAN_PUB}
sed -i -e "s/\"xml:lang\"/\"language\"/" ${CKAN_PUB}
sed -i -e "s/\(^.*language.*\):\s*\"/\1: { \"type\": \"literal\" , \"value\" : \"/" ${CKAN_PUB}


echo "**********************************************"
echo "*** Creating publisher hierarchy json file ***"
echo "**********************************************"

roqet -D $1 -i sparql ${CKAN_FOLDER}l/conf/nal_query_hierarchy.rq -r json > ${HIERARCHY}

rm -f ${CKAN_PUB}

