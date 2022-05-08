#!/bin/bash

export WORKLOAD=$1
export PORT=$2
export PGDATABASE=$3
export RECORDS=$4
export THREADS=$5
export OPERATIONS=$6
export ITERATION=$7

cd ycsb-0.17.0

export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`

bin/ycsb run jdbc -P workloads/$WORKLOAD -p db.driver=org.postgresql.Driver -p recordcount=$RECORDS -p operationcount=$OPERATIONS -p threadcount=$THREADS -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee ${HOMEDIR}/${OUTDIR}/run_${WORKLOAD}_${THREAD}_${RECORDS}_${OPERATIONS}_${ITERATION}_${WORKERS}_${RESOURCE}.log
