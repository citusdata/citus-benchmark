#!/bin/bash
RESOURCE_GROUP=$1

ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.driverPublicIp.value --output tsv)
ssh "$ip"
