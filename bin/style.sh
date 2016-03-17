#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

# Ensure we are in a virtualenv
. ./bin/virtualenv.sh
(( result+=$? ))

flake8 . --count --statistics --exclude="$VIRTUAL_ENV" --builtins=FileNotFoundError
(( result+=$? ))

exit $result
