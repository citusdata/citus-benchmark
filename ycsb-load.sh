#!/bin/bash

export WORKLOAD=$1
export PORT=$2
export PGDATABASE=$3
export RECORDS=$4
export THREADS=$5

cd ycsb-0.17.0

bin/ycsb load jdbc -P workloads/$WORKLOAD -p db.driver=org.postgresql.Driver -p recordcount=$RECORDS -p threadcount=$THREADS -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee ${HOMEDIR}/${OUTDIR}/load_${WORKLOAD}_${THREAD}_${RECORDS}.log
