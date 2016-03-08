#!/bin/bash
result=0
download_location="${DOWNLOAD_LOCATION:-/opt/dist/pypi}"
internet_access=${INTERNET_ACCESS:-true}

if $internet_access; then
  # Ensure our download location exists
  mkdir -p "$download_location"

  # Ensure we are in a virtualenv
  . ./bin/virtualenv.sh
  (( result+=$? ))

  # Download app requirements
  pip download -r requirements.txt --dest "$download_location"
  (( result += $? ))

  # Download test requirements
  pip download -r requirements_test.txt --dest "$download_location"
  (( result += $? ))
fi

exit $result
