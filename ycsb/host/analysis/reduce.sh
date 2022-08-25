#!/bin/bash

filename=$1
outputname=$2

echo $(cat ${filename} | grep avg-cpu -A 1 | grep 0) > ${outputname}.out

