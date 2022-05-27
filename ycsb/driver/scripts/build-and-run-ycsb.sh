#!/bin/bash
export PGHOST=$1
export PGUSER=$2
export PGPASSWORD=$3
export PGPORT=$4
export PGDATABASE=citus
export RECORDS=$5
export OPERATIONS=$6
export SHARD_COUNT=$7
export THREAD_COUNT=$8
export ITERATIONS=$9
export WORKERS=${10}
export RESOURCE_GROUP=${11}
export MONITORPW=${12}
export PARALLEL=True

cd $HOMEDIR

python3 benchmark.py --host=PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW citus_workload
