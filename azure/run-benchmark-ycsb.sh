#!/bin/bash

set -euxo pipefail
cd "$(dirname "$0")"

export RESOURCE_GROUP=$1

./start-benchmark-ycsb.sh "$@"
./wait-for-results-ycsb.sh "$RESOURCE_GROUP" 2> /dev/null
# ./cleanup.sh "$RESOURCE_GROUP"
