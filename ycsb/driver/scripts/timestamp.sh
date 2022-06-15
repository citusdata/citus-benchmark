#!/bin/bash

filename=$1
directory=$2

cd $directory

date | cut -d ' ' -f 4 > $filename
