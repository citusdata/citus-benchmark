#!/bin/bash

name=$1
out=$2

cat $name | grep anchor | cut -d ' ' -f 24 > $out
