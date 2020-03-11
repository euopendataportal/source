#!/usr/bin/env bash
source ckan_script_config.sh

echo ""
echo "***************************************************************"
echo "***   Update number of downloads resources: $(date)   ***"
echo "***************************************************************"
echo "HOST: $(hostname)"
echo ""

ACTION="update_number_downloads"

# Check if the correct user is running the script
SCRIPT_EXECUTOR=$(whoami)
if [[ "$SCRIPT_EXECUTOR" != "ecodp" ]]; then
    echo "Please run as ecodp, not as $SCRIPT_EXECUTOR"
    exit
else
  echo "User check OK"
fi


echo "***************************************************************"
echo "The script will be called with these parameters"
echo "***************************************************************"
echo "***************************************************************"

. ${CKAN_FOLDER}/bin/activate
${CKAN_FOLDER}/bin/paster --plugin=ckanext-ecportal update_number_downloads -c ${CKAN_FOLDER}/conf/ecportal.ini