#!/bin/bash

export WORKLOAD=$1
export PORT=$2
export DATABASE=$3
export RECORDS=$4
export THREADS=$5
export OPERATIONS=$6

cd ycsb-0.17.0

bin/ycsb run jdbc -P workloads/$WORKLOAD -p db.driver=org.postgresql.Driver -p recordcount=$RECORDS -p operationcount=$OPERATIONS -p threadcount=$THREADS -cp ./postgresql-42.2.14.jar -p db.url="jdbc:postgresql://localhost:$PORT/$DATABASE/?prepareThreshold=0" | tee ${HOMEDIR}/${OUTDIR}/run_${WORKLOAD}_${THREAD}_${RECORDS}_${OPERATIONS}.log
