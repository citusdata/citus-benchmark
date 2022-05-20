#!/bin/bash

#!/bin/bash

export WORKLOAD=$1
export PORT=$2
export PGDATABASE=$3
export RECORDS=$4
export THREADS=$5
export ITERATION=$6
export WORKERS=$7
export RESOURCE=$8

export RECORDSM=$9
export OPERATIONSM=${10}
export MONITORPW=${11}
export MAXTIME=${12}
export THREADSM=$WORKERS

export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`

(.ycsb-load.sh) &

main_pid = $!

(monitor-load.sh) &

monitor_pid = $!

wait $main_pid
wait $monitor_pid
