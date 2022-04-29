#!/bin/bash

export HOMEDIR=$PWD
export OUTPUT_FOLDER=output
export PGDATABASE=citus
export RECORDS=$1
export OPERATIONS=$2
export SHARD_COUNT=$3

mkdir -p $OUTPUT_FOLDER

./install-and-run-ycsb.sh $OUTPUT_FOLDER $RECORDS $OPERATIONS $SHARD_COUNT

# python3 run-benchmark.py --outdir=$OUTPUT_FOLDER --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT 