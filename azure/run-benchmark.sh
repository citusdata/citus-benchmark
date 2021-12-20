#!/bin/bash

RESOURCE_GROUP=$1
shift
DEPLOYMENT=$1
shift

PUBKEY_PATH=~/.ssh/id_rsa.pub
PUBKEY=$(cat $PUBKEY_PATH)

PGPASSWORD=$(openssl rand -base64 24)

az group create --name "$RESOURCE_GROUP"

az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$RESOURCE_GROUP" \
    --template-file "$DEPLOYMENT.bicep" \
    --parameters "vmAdminUsername=$USER" \
    --parameters "vmAdminPublicKey=$PUBKEY" \
    --parameters "pgAdminPassword=$PGPASSWORD" \
    --parameters "namePrefix=$RESOURCE_GROUP" \
    "$@"
