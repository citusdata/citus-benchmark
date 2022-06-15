#!/bin/bash

cd $1

tmux new -s server -d; tmux send-keys -t server  'python3 server.py' Enter
