#!/bin/bash

tmux new -s server -d; tmux send-keys -t server 'python3 server.py' Enter