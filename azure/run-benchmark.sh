#!/bin/bash

set -euxo pipefail
cd "$(dirname "$0")"

RESOURCE_GROUP=$1

./start-benchmark.sh "$@"
./wait-for-results.sh "$RESOURCE_GROUP" 2> /dev/null
./cleanup.sh "$RESOURCE_GROUP"
