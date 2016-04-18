#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

# Ensure we are in a virtualenv
. ./bin/virtualenv.sh
(( result+=$? ))

# Run the tests
./manage.py test
(( result+=$? ))

# Run the test that has to be run in isolation because of a django bug
TEST_API_USAGE=1 ./manage.py test apps.links.tests.test_usage_api.LinkUsageAPITest.test_update_usage_creates_api_usage
(( result+=$? ))

exit $result
