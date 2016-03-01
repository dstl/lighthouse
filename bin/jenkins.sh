#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

# Lighthouse DB should be unique to each job, to prevent conflicts
export LIGHTHOUSE_DB="$JOB_NAME$BUILD_NUMBER"

# Setup a virtualenv
. ./bin/virtualenv.sh
(( result+=$? ))

# Run the tests
./bin/test.sh
(( result+=$? ))

# Lint the code
./bin/style.sh
(( result+=$? ))

exit $result
