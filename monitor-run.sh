#!/bin/bash

export WORKLOAD=$1
export PORT=$2
export PGDATABASE=$3
export RECORDS=$4
export THREADS=$5
export OPERATIONS=$6
export ITERATION=$7
export WORKERS=$8
export RESOURCE=$9
export MONITOR=monitor

cd ycsb-0.17.0

export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`

bin/ycsb run jdbc -P workloads/$WORKLOAD -p db.driver=org.postgresql.Driver -p insertstart=$RECORDS -p insertcount=$RECORDS -p operationcount=$OPERATIONS -p threadcount=$WORKERS -cp ./postgresql-42.2.14.jar -p db.user=$MONITOR -p db.passwd=$PASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee ${HOMEDIR}/${OUTDIR}/run_${WORKLOAD}_${MONITOR}_${ITERATION}_${WORKERS}_${RESOURCE}.log
