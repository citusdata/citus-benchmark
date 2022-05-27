#!/bin/bash
export PGHOST=$0
export PGUSER=$1
export PGPASSWORD=$2
export PGPORT=$3
export PGDATABASE=citus
export RECORDS=$4
export OPERATIONS=$5
export SHARD_COUNT=$6
export THREAD_COUNT=$7
export ITERATIONS=$8
export WORKERS=$9
export RESOURCE_GROUP=${10}
export MONITORPW=${11}
export PARALLEL=True

cd $HOMEDIR

python3 benchmark.py --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW citus_workload
