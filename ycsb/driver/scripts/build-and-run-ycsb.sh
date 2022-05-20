#!/bin/bash

cd $HOMEDIR

python3 benchmark.py --outdir=$OUTPUT_FOLDER --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW test_parallel_load
