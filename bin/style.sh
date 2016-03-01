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

pip install flake8
(( result+=$? ))

flake8 . --count --statistics --exclude="$VIRTUAL_ENV"
(( result+=$? ))

exit $result
