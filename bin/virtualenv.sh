#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
result=0
virtualenv_location="${VIRTUALENV_LOCATION:-$HOME/.venv/lighthouse}"

# Only create a virtualenv if we aren't in one
if [[ -z "$VIRTUAL_ENV" ]]; then
  # Create a virtual env
  virtualenv $virtualenv_location
  (( result += $? ))

  # Activate the virtual env
  . $virtualenv_location/bin/activate
  (( result += $? ))

  # If we've created a new virtualenv we should install dependencies
  ./bin/pip-install.sh
  (( result += $?))
fi

return $result
