#!/bin/bash
set -euxo pipefail
az group delete -y --name "$1"
