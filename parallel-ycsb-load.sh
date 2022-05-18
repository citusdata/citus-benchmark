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

export INSERTCOUNTC=$9
export INSERTCOUNTM=${10}
export MONITORPW=${11}
export MAXTIME=${12}
export THREADSM=$WORKERS
export INSERTSTART=${13}

export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`

(./ycsb-load-maxtime.sh $WORKLOAD $PORT $PGDATABASE $RECORDS $THREADS $ITERATION $WORKERS $RESOURCE $MONITORPW $MAXTIME $INSERTCOUNTC $CITUS_HOST) &

main_pid = $!

(./monitor-load.sh $WORKLOAD $PORT $PGDATABASE $RECORDS $WORKERS $ITERATION $WORKERS $RESOURCE $INSERTCOUNTM $MONITORPW $MAXTIME $INSERTSTART $CITUS_HOST) &

monitor_pid = $!

wait $main_pid
wait $monitor_pid
