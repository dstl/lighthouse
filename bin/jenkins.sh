dot="$(cd "$(dirname "$0")"; pwd)"
cd "$dot/../"
result=0

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
