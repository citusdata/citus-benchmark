#!/bin/bash

dir=$1

cd $dir

tmux new -s server -d; tmux send-keys -t server 'python3 server.py' Enter
