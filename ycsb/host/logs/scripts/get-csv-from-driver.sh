#!/bin/bash

RESOURCE_GROUP=$1
OUTPUT_FOLDER=$2

ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.driverPublicIp.value --output tsv)

scp -r $ip:citus-benchmark/ycsb/driver/*.csv $OUTPUT_FOLDER
