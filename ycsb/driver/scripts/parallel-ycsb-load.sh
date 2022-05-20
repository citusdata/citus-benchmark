#!/bin/bash


export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`

(./ycsb-load-maxtime.sh) &

main_pid = $!

(./monitor-load.sh) &

monitor_pid = $!

wait $main_pid
wait $monitor_pid
