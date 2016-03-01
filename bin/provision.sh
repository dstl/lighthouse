#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

. $dot/virtualenv.sh
(( result+=$? ))

./manage.py migrate
(( result+=$? ))

exit $result
