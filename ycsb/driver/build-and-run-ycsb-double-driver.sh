echo Starting Benchmarks
echo "python3 monitor-double.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW --drivers=$DRIVERS --driver_id=$PART citus_workload"

tmux new -s server -d; tmux send-keys -t server  'python3 server.py' Enter
python3 monitor.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW monitor_workloada

# tmux kill-session -t server
# tmux kill-session -t init-bench
