#!/bin/bash

RESOURCE_GROUP=$1
OUTPUT_FOLDER=$2

ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.driverPublicIp.value --output tsv)
secondip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.seconddriverPublicIp.value --output tsv)

scp -r \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $ip:citus-benchmark/ycsb/driver/*log $OUTPUT_FOLDER  2>/dev/null

scp -r \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $secondip:citus-benchmark/ycsb/driver/*log $OUTPUT_FOLDER  2>/dev/null

