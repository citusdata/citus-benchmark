#!/bin/bash

export HOMEDIR=$PWD
export OUTPUT_FOLDER=output
export PGDATABASE=citus
export RECORDS=$1
export OPERATIONS=$2
export SHARD_COUNT=$3
export THREAD_COUNT=$4
export ITERATIONS=$5
export WORKERS=$6
export RESOURCE_GROUP=$7
export MONITORPW=$8

mkdir -p $OUTPUT_FOLDER

python3 benchmark.py --outdir=$OUTPUT_FOLDER --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW citus_workload
