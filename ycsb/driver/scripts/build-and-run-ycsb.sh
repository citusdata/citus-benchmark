#!/bin/bash

cd $HOMEDIR

python3 benchmark.py --parallel=True --outdir=$OUTPUT_FOLDER --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW citus_workload
