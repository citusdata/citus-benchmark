#!/bin/bash

export HOMEDIR=$(pwd)
sudo apt install -y default-jre python postgresql-client-common postgresql-client-14

sudo apt install python-is-python3 -y
sudo apt-get install python3-pip -y
pip3 install fire
pip3 install pandas
pip3 install matplotlib
