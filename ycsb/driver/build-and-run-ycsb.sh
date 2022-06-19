echo Starting Benchmarks
echo "python3 benchmark.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW citus_workload"

tmux new -s server -d; tmux send-keys -t server  'python3 orchestrator.py' Enter
python3 benchmark.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW monitor_workloadc

# tmux kill-session -t server
tmux kill-session -t init-bench
