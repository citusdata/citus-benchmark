#!/bin/bash

set -euo pipefail

export AZURE_USER=$(whoami)

ip=$(az deployment group show --resource-group "$RESOURCE" --name "$RESOURCE" --query properties.outputs.driverPublicIp.value --output tsv)

scp \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    ${AZURE_USER}@${ip}:citus-benchmark/ycsb/*.csv . 2>/dev/null
