#!/bin/bash

export PGHOST=$1
export PGPORT=$2
export PGPASSWORD=$3
export PGUSER=$4
export PGDATABASE=$5

echo $(psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1")
