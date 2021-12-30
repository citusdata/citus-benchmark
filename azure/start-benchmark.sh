#!/bin/bash


set -euo pipefail
cd "$(dirname "$0")"

RESOURCE_GROUP=$1
shift
DEPLOYMENT=$1
shift

PUBKEY_PATH=~/.ssh/id_rsa.pub
PUBKEY=$(cat $PUBKEY_PATH)

PGPASSWORD=$(openssl rand -base64 24)

az group create --name "$RESOURCE_GROUP" --only-show-errors > /dev/null

az deployment group create \
    --only-show-errors \
    --resource-group "$RESOURCE_GROUP" \
    --name "$RESOURCE_GROUP" \
    --template-file "$DEPLOYMENT.bicep" \
    --parameters "vmAdminUsername=$USER" \
    --parameters "vmAdminPublicKey=$PUBKEY" \
    --parameters "pgAdminPassword=$PGPASSWORD" \
    --parameters "namePrefix=$RESOURCE_GROUP" \
    "$@" > /dev/null
