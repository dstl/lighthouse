#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

if [[ -z "$LIGHTHOUSE_HOST" ]]; then
	echo "You must specify a LIGHTHOUSE_HOST environment variable before"
	echo "running the acceptance tests."
	exit 1
fi

# Ensure we are in a virtualenv
. ./bin/virtualenv.sh
(( result+=$? ))

# Run the tests
./manage.py acceptance
(( result+=$? ))

exit $result
