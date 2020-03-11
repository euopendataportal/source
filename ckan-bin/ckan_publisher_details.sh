#!/bin/bash
# This script returns the details about the publisher stored in ckan

args_num=2
if [[ $# -lt ${args_num} ]] ; then
    echo "$args_num argument are mandatory"
    echo "arg1 the frontend ip/hostname"
    echo "arg2 the publishers acronym"
    exit
fi


curl -X POST "http://$1/data/api/3/action/organization_show" -d "{\"id\": \"$2\"}"
