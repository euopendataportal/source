#!/bin/bash

# This script backups the whole ckan site and tars the result in a timestamped file
# The resulted backup is copied on a target directory.
function checkErrorCode {
    STATUS=$?
    if [[ ${STATUS} -ne 0 ]]; then
            echo "One of the above the messages caused a problem."
            echo "Backup is aborted"
            exit 2;
    fi
}

source ckan_script_config.sh
source backup_restore.conf

if [[ -z "$APPLICATION_FILES_DIR" ]] || [[ -z "$TARGET_BACKUP_DIR" ]] || [[ -z "$CKAN_USER" ]] || [[ -z "$CKAN_PWD" ]] || [[ -z "$POSTGRES_USER" ]] || [[ -z "$POSTGRES_HOST" ]]  ; then
    echo "configuration variables not properly set"
    exit
    fi
checkErrorCode

DATE=`date +%Y-%m-%d-%H-%M-%S`

# PLACED IN  CONF :
DUMP_DIR=${CKAN_TMP}/ckan_backup
DUMP_FILE=ecodp_ckan_${DATE}
RDF2CKAN_FILE=ecodp_rdf2ckan_${DATE}
DUMP_DB=ecodp_ckan_db_${DATE}
DUMP_ECODP=ecodp_ckan_all_${DATE}

echo "start backup"

# make a place to dump temporay all data
echo "Removing old dump directory"
rm -rf ${DUMP_DIR}
checkErrorCode
echo "Creating new dump directory"
mkdir -p ${DUMP_DIR}
checkErrorCode
mkdir -p ${DUMP_DIR}/files
checkErrorCode
mkdir -p ${DUMP_DIR}/db
checkErrorCode

echo "Checking connection with postgresql, asking for a simple count from table of groups";
psql -U${POSTGRES_USER} -h ${POSTGRES_HOST} -c "select count(1) FROM public.group;"
checkErrorCode
# 1st backup the postgres database
echo "Dumping database"
pg_dump -h ${POSTGRES_HOST} -U ${POSTGRES_USER} --file ${DUMP_DIR}/db/${DUMP_DB}.sql --format custom ecodp
echo "Compacting database"
gzip ${DUMP_DIR}/db/${DUMP_DB}.sql
checkErrorCode
# 2e backup the file resources
if [[ -e ${APPLICATION_FILES_DIR} ]] ; then
echo "Making tarball file out of the dump"
tar -czf ${DUMP_DIR}/files/${DUMP_FILE}.tgz --absolute-names ${APPLICATION_FILES_DIR}
checkErrorCode
else
echo "no web interface files available."
fi
if [[ -e ${RDF2CKAN_UPLOADS_FILES_DIR} ]] ; then
echo "Making tarball out of the rdf2ckan files"
tar -czf ${DUMP_DIR}/files/${RDF2CKAN_FILE}.tgz --absolute-names ${RDF2CKAN_UPLOADS_FILES_DIR}
checkErrorCode
else
echo "no rdf2ckan upload files available."
fi

# make the global backup
pushd .
echo "In temporary directory working..."
cd ${CKAN_TMP}
checkErrorCode
echo "Preparing the tarball of backup"
tar -czf ${DUMP_ECODP}.tgz ckan_backup
checkErrorCode
mkdir -p ${TARGET_BACKUP_DIR}
checkErrorCode
echo "Moving dump to the backup final destination directory"
mv ${DUMP_ECODP}.tgz ${TARGET_BACKUP_DIR}
checkErrorCode
popd
echo "Removing old dump dir"
rm -rf ${DUMP_DIR}
checkErrorCode
echo "backup finished"
