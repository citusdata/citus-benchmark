#!/bin/bash

RESOURCE_GROUP=$1
SIGN=$2
SLEEP=$3

while ! test -f $SIGN; do

if [[ -d "citus-benchmark" ]]
then
    cd citus-benchmark/ycsb/driver
fi
    sleep $SLEEP
	./get-sign.sh $RESOURCE_GROUP $SIGN
done

echo "Benchmark ready to start"
rm $SIGN

