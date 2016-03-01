#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

# Source a virtualenv if we aren't in one
if [[ -z "$VIRTUAL_ENV" ]]; then
  . ./bin/virtualenv.sh
  (( result+=$? ))
fi

# Install the test requirements
pip install -r requirements_test.txt
(( result+=$? ))

# Run the tests
./manage.py test
(( result+=$? ))

exit $result
