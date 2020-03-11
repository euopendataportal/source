#!/bin/bash

CKAN_RESULTS=`curl http://localhost/data/api/action/package_list -d {}`

PACKAGES=`echo ${CKAN_RESULTS}| sed -e "s/.*\"result\":..//" | sed -e "s/].*//"| sed -e "s/\"//g" |sed -e "s/,//g" `

echo ${PACKAGES}

for p in ${PACKAGES} ; do
    echo $p
#    wget http://localhost/data/dataset/$p.rdf
done
