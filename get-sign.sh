#!/bin/bash

set -euo pipefail

export RESOURCE_GROUP=$1
export AZURE_USER=$(whoami)
export FILENAME=$2

ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.driverPublicIp.value --output tsv)

scp $AZURE_USER@$ip:$FILENAME . 2>/dev/null

