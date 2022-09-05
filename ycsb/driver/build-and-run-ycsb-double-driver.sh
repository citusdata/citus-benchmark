echo Starting Benchmarks

if [ ${PART} -eq 0 ]; then
	tmux new -s server -d; tmux send-keys -t server  'python3 server-double.py' Enter
	python3 monitor-double.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW --driver_id=$PART monitor_workloada
else
	python3 monitor-double-client.py --host=$PGHOST --parallel=$PARALLEL --records=$RECORDS --operations=$OPERATIONS --shard_count=$SHARD_COUNT --threads=$THREAD_COUNT --iterations=$ITERATIONS --workers=$WORKERS --resource=$RESOURCE_GROUP --monitorpw=$MONITORPW --driver_id=$PART monitor_workloada
fi

# tmux kill-session -t server
# tmux kill-session -t init-bench
