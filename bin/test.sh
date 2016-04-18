#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

# Ensure we are in a virtualenv
. ./bin/virtualenv.sh
(( result+=$? ))

# the test runner should pick a port at random, so there is less chance of
# multiple test runs at once (common in CI) clashing over the port
# TODO - remove this after django upgrade (default behaviour in >1.9)
export DJANGO_LIVE_TEST_SERVER_ADDRESS='localhost:8081-8179'

# Run the tests
./manage.py test
(( result+=$? ))

# Run the test that has to be run in isolation because of a django bug
TEST_API_USAGE=1 ./manage.py test apps.links.tests.test_usage_api.LinkUsageAPITest.test_update_usage_creates_api_usage
(( result+=$? ))

exit $result
