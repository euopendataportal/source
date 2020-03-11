#!/usr/bin/env bash

source backup_restore.conf
if [[ -z "$POSTGRES_USER" ]] || [[ -z "$POSTGRES_HOST" ]] || [[ -z "$POSTGRES_PWD" ]]  ; then
    echo "configuration variables not properly set"
    echo "Please export the following variables"
    echo "POSTGRES_HOST Postgresql Hostname"
    echo "POSTGRES_USER Postgresql Username"
    echo "POSTGRES_PWD Postgresql Password"
    exit
fi



echo "Checking connection with postgresql, deleting all users";
PGPASSWORD=${POSTGRES_PWD} psql -U${POSTGRES_USER} -h ${POSTGRES_HOST} -c "update \"user\" set state = 'deleted' where name != 'api' AND name != 'ecportal';"