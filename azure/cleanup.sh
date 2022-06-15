#!/bin/bash
set -euxo pipefail
cd "$(dirname "$0")"

RESOURCE_GROUP=$1
az group delete -y --name "$RESOURCE_GROUP" --no-wait > /dev/null
