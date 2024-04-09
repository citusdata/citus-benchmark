#!/bin/bash

SIGN=$1
SLEEP=$2

while ! test -f $SIGN; do
    sleep $SLEEP
	./get-file.sh $SIGN
done

./get-file.sh ${RESOURCE}-results.csv

rm $SIGN
cat ${RESOURCE}-results.csv
