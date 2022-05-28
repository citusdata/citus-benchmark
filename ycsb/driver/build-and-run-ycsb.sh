echo Starting Benchmarks
echo "python3 benchmark.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW citus_workload"

python3 benchmark.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW citus_workload
