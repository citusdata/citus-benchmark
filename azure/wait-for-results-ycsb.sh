#!/bin/bash

set -euo pipefail
cd "$(dirname "$0")"

RESOURCE_GROUP=$1

while ! ./get-results-ycsb.sh "$RESOURCE_GROUP"; do
    sleep 10
done
