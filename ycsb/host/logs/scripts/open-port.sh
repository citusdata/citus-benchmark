#!/bin/bash

export RESOURCE=$1
export PORT=$2

tmux new -s open-port -d; tmux send-keys -t open-port './port.sh '$RESOURCE' '$PORT'' Enter

