#!/bin/bash

set -euo pipefail

export RESOURCE_GROUP=$1
export AZURE_USER=$(whoami)
export FILENAME=$2

ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.driverPublicIp.value --output tsv)

scp \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $AZURE_USER@$ip:citus-benchmark/ycsb/azure/$FILENAME . 2>/dev/null

