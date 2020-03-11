#!/bin/bash

DIRECTORY=$(dirname $(readlink -f $0))


error_file_not_existing()
{
    echo "The directory \"$1\" does not exists"
    echo "installation aborted ..."
    exit 1
}

if [[ $# -gt 0 ]] ; then
    DIRECTORY="$1"
    if [ ! -d ${DIRECTORY} ]; then
        error_file_not_existing ${DIRECTORY}
    fi
fi

echo "INFO: create a clean new python virtualenv for ckan";
virtualenv --no-site-packages ${DIRECTORY}
mkdir ${DIRECTORY}/logs
mkdir ${DIRECTORY}/data

. ${DIRECTORY}/bin/activate
cd ${DIRECTORY}

echo "prepare the python environment with latest possible pip, setuptools, pip-accel"
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python2.7 get-pip.py
pip install setuptools==36.8.0
pip install pip-accel

cd ${DIRECTORY}
pip-accel install -r ${DIRECTORY}/ckanext-ecportal/requirements-prod.txt

for d in ${DIRECTORY}/*; do
    if [ -d "$d" ]; then
      # $d is a directory
      if [ -f "$d/setup.py" ]; then
        cd ${d}
        python setup.py develop
      fi
    fi
done
cd ${DIRECTORY}
virtualenv --relocatable ${DIRECTORY}

exit 0
