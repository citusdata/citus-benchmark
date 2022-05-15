#!/bin/bash

RESOURCE_GROUP=$1
SIGN=$2
SLEEP=$3

while ! test -f $SIGN; do
	./get-sign.sh $RESOURCE_GROUP $SIGN
	sleep $SLEEP
done

rm $SIGN

