#!/bin/bash

dir=$1

cd $dir

tmux new-session -d -t main -s init-bench \; send-keys 'python3 server.py' Enter
