#!/bin/bash
set -euo pipefail

RESOURCE_GROUP=$1

ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.driverPublicIp.value --output tsv)
ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" "$ip" "ch-benchmark/create-csv-result-lines.sh"
