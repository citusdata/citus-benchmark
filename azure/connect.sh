#!/bin/bash
ssh "$(az deployment group show --resource-group "$1" --name "$1" --query properties.outputs.driverPublicIp.value --output tsv)"
