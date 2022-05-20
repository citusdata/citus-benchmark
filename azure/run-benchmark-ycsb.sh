#!/bin/bash

set -euxo pipefail
cd "$(dirname "$0")"

export RESOURCE_GROUP=$1

./create-drivervm.sh "$@"
echo "Creation of Driver VM succeeded"
# ./wait-for-results-ycsb.sh "$RESOURCE_GROUP" 2> /dev/null
# ./cleanup.sh "$RESOURCE_GROUP"

