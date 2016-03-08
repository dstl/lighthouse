#!/bin/bash
result=0
download_location="${DOWNLOAD_LOCATION:-/opt/dist/pypi}"

# Ensure we are in a virtualenv
. ./bin/virtualenv.sh
(( result+=$? ))

# Download the dependencies
./bin/pip-download.sh
(( result += $? ))

# Install the app requirements
pip install -r requirements.txt --find-links="$download_location" --no-index
(( result += $? ))

# Install test requirements
pip install -r requirements_test.txt --find-links="$download_location" --no-index
(( result += $? ))

exit $result
