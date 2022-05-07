#!/bin/bash

export HOMEDIR=$PWD
export OUTPUT_FOLDER=largeexp
export PGDATABASE=citus
export RECORDS=$1
export OPERATIONS=$2
export SHARD_COUNT=$3
export THREAD_COUNT=$4
export ITERATIONS=$5

mkdir -p $OUTPUT_FOLDER

python3 run-benchmark.py --outdir=$OUTPUT_FOLDER --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS citus_workload 