#!/bin/bash

source ckan_script_config.sh
source ${CKAN_FOLDER}/ckan-bin/backup_restore.conf
# This script restores the whole ckan site from a tar created with
#  arg1 = the backup_ckan script
function checkErrorCode {
    STATUS=$?
    if [[ ${STATUS} -ne 0 ]]; then
            echo "One of the above the messages caused a problem."
            echo "The restore aborted"
            exit 2;
    fi
}

if [[ -z "$RDF2CKAN_UPLOADS_FILES_DIR" ]] || [[ -z "$APPLICATION_FILES_DIR" ]] || [[ -z "$TARGET_BACKUP_DIR" ]] || [[ -z "$CKAN_USER" ]] || [[ -z "$CKAN_PWD" ]] || [[ -z "$POSTGRES_USER" ]] || [[ -z "$POSTGRES_HOST" ]]  ; then
    echo "configuration variables not properly set"
    exit
    fi

TAR=$1
if [[ -z "${TAR}" ]] ; then
    echo "arguments are missing"
    exit
    fi
checkErrorCode

DATE=`date +%Y-%m-%d-%H-%M-%S`

DUMP_DIR=${CKAN_TMP}/ckan_backup
DUMP_FILE=ecodp_ckan_${DATE}
DUMP_DB=ecodp_ckan_db_${DATE}
DUMP_ECODP=ecodp_ckan_all_${DATE}

echo "Checking connection with postgresql, asking for a simple count from table of groups";
psql -U${POSTGRES_USER} -h ${POSTGRES_HOST} -c "select count(1) FROM public.group;"
checkErrorCode

echo "start restore"
echo "unpacking ..."

# create an empty environment
echo "Removing old directory dump"
rm -rf ${DUMP_DIR}
mkdir -p ${DUMP_DIR}

# empty the sql database

# unpack the tar
echo "Untarring..."
tar -zxf ${TAR} -C ${CKAN_TMP}
checkErrorCode
# unpack the files

echo "restore the files"

rm -rf ${APPLICATION_FILES_DIR}
for f in $( ls ${DUMP_DIR}/files ) ; do
	tar -zxf ${DUMP_DIR}/files/${f} --absolute-names
	checkErrorCode
done

# upload the database
echo "Unzipping...."
for f in $( ls ${DUMP_DIR}/db ) ; do
	gunzip ${DUMP_DIR}/db/${f}
	checkErrorCode
done

echo "restore the database"

for f in $( ls ${DUMP_DIR}/db ) ; do
	pg_restore -U${POSTGRES_USER} -decodp --clean ${DUMP_DIR}/db/$f -h${POSTGRES_HOST} --verbose
done
checkErrorCode
echo "restore completed"

# rebuild the index
echo "Starting to rebuild the index ... This can take a while"

${CKAN_FOLDER}/ckan-bin/ckan_reindex.sh
checkErrorCode
echo "restore finished"
