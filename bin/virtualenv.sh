#!/bin/bash
# (c) Crown Owned Copyright, 2016. Dstl.
result=0
virtualenv_location="${VIRTUALENV_LOCATION:-$HOME/.venv/lighthouse}"

# Create a virtual env
virtualenv $virtualenv_location
(( result += $? ))

# Activate the virtual env
. $virtualenv_location/bin/activate
(( result += $? ))

# Install the requirements
pip install -r requirements.txt
(( result += $? ))

return $result
