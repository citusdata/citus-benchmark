#!/bin/bash

export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`

(./ycsb-run-maxtime.sh) &

main_pid=$!

(./monitor-run.sh) &

monitor_pid=$!

wait $main_pid
wait $monitor_pid
