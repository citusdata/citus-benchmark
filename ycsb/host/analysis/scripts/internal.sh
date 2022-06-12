#!/bin/bash

name=$1
out=$2

cat $name | grep app=citus | grep duration: | cut -d ':' -f 6 | cut -d ' ' -f 2 > $out
