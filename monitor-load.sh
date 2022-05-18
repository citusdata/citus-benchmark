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
export INSERTCOUNTM=${10}
export MONITORPW=${11}
export MAXTIME=${12}
export INSERTSTART=${13}
export CITUS_HOST=${14}

cd ycsb-0.17.0

bin/ycsb load jdbc \
    -P workloads/$WORKLOAD \
    -p db.driver=org.postgresql.Driver \
    -p recordcount=$RECORDS \
    -p threadcount=$THREADS \
    -p insertstart=$INSERTSTART \
    -p insertcount=$INSERTCOUNTM \
    -cp ./postgresql-42.2.14.jar \
    -p db.user=monitor \
    -p db.passwd=$MONITORPW \
    -p maxexecutiontime=$MAXTIME \
    -p db.url="jdbc:postgresql://$CITUS_HOST/citus?loadBalanceHosts=true" | tee ${HOMEDIR}/${OUTDIR}/load_${WORKLOAD}_${THREAD}_${RECORDS}_${ITERATION}_${WORKERS}_${RESOURCE}.mlog
