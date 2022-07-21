#!/bin/bash

RESOURCE_GROUP=$1
SIGN=$2
SLEEP=$3

while ! test -f $SIGN; do
    sleep $SLEEP
	./get-file.sh $RESOURCE_GROUP $SIGN
done

./get-file.sh $RESOURCE_GROUP results.csv

rm $SIGN

