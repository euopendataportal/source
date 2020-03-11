#!/bin/bash

# This script backups the activity tables and clears them.
source ckan_script_config.sh
source backup_restore.conf

if [[ -z $RDF2CKAN_UPLOADS_FILES_DIR ]] || [[ -z "$APPLICATION_FILES_DIR" ]] || [[ -z "$TARGET_BACKUP_DIR" ]] || [[ -z "$CKAN_USER" ]] || [[ -z "$CKAN_PWD" ]] || [[ -z "$POSTGRES_USER" ]] || [[ -z "$POSTGRES_HOST" ]]  ; then
    echo "configuration variables not proberly set"
    exit
    fi

DATE=`date +%Y-%m-%d-%H-%M-%S`

mkdir -p ${CKAN_TMP}

# default value; should not be changed
DATABASE=ecodp

echo "Start clearing activity table"

# Dump the activity tables for prosperity
pg_dump  -a -t activity -t activity_detail -h ${POSTGRES_HOST} -U ${POSTGRES_USER} ${DATABASE}> ${CKAN_TMP}/activity_backup_${DATE}.sql
gzip ${CKAN_TMP}/activity_backup_${DATE}.sql

# Clean their contents
psql -d ${DATABASE} -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -c 'truncate activity, activity_detail;'

echo "Finished clearing activity table"
