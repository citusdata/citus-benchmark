#!/bin/bash
RESOURCE_GROUP=$1
export VMNAME="${RESOURCE_GROUP}-driver-analysis"
echo $VMNAME

# ip=$(az deployment group show --resource-group "$RESOURCE_GROUP" --name "$RESOURCE_GROUP" --query properties.outputs.PublicIp.value --output tsv)
ip=$(az vm list-ip-addresses --name "$VMNAME" --resource-group "$RESOURCE_GROUP" --query "[].virtualMachine.network.publicIpAddresses[0].ipAddress" --output tsv)
echo "Trying to connect with VM for performance monitoring..."
ssh "$ip"
