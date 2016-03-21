#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

# Ensure we are in a virtualenv
. ./bin/virtualenv.sh
(( result+=$? ))

./manage.py migrate
(( result+=$? ))

./manage.py rebuild_index --noinput
(( result+=$? ))

./manage.py compress --force
(( result+=$? ))

./manage.py collectstatic --noinput
(( result+=$? ))

exit $result
