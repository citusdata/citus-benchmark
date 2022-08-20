#!/bin/bash

RESOURCE=$1
PORT=$2

az vm open-port --resource-group ${RESOURCE} --name ${RESOURCE}-driver --port $PORT
tmux kill-session -t open-port
