#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

RESOURCE_GROUP=$1

ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.driverPublicIp.value --output tsv)
ssh -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    -o "ControlMaster=auto" \
    -o "ControlPath=.ssh-controlmasters/%r@%h:%p" \
    -o "ControlPersist=24h" \
    "$ip" \
    "citus-benchmark/create-csv-result-lines.sh"
