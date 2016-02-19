dot="$(cd "$(dirname "$0")"; pwd)"
result=0

. $dot/virtualenv.sh
(( result+=$? ))

exit $result
