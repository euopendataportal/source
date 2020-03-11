#!/bin/bash

source ckan_script_config.sh

if [[ $# -lt 4 ]] ; then
   echo "4 arguments are mandatory"
   echo "arg1 the username"
   echo "arg2 the publishers acronym"
   echo "arg3 the sysadmin api key"
   echo "arg4 the frontend prefix in the form http://\$FRONTEND"
   exit
   fi

source ${CKAN_FOLDER}/ckan-bin/paster.sh


# arg1 is username
#      password will be prompted
# arg2 is publisher acronym, lower cased e.g. cnect
# arg3 is the sysadmin api key
# arg4 is the frontend hostname/ip-address prefix of the form http://$FRONTEND

# create a new user
# lowercasing the user name is not needed
# args1=`echo $1 | tr '[A-Z]' '[a-z]'`
args1=$1
args2=`echo $2 | tr '[A-Z]' '[a-z]'`
# Run the paster command, referencing the .ini file
paster --plugin=ckan user add ${args1} -c ${CKAN_INI}

# alternative 2: insert via a specific call
USERDESC=`paster --plugin=ckan user $args1 -c ${CKAN_INI}`
UserID=` echo ${USERDESC} | sed -e "s/ name.*//" | sed -e "s/^.*id=//" `

GroupUpdate2=`curl -X POST "$4/data/api/3/action/member_create" -d "{\"id\": \"$args2\", \"object\": \"$UserID\", \"object_type\": \"user\", \"capacity\": \"editor\"}" -H "Authorization: $3"`

echo ${GroupUpdate2}
echo "user created and added to the publisher"

