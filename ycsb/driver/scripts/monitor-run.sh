#!/bin/bash
cd ycsb-0.17.0

bin/ycsb run jdbc -P \
    workloads/$WORKLOAD \
    -p db.driver=org.postgresql.Driver \
    -p insertstart=$RECORDS \
    -p insertcount=$RECORDS \
    -p operationcount=$OPERATIONS \
    -p threadcount=$WORKERS \
    -cp ./postgresql-42.2.14.jar \
    -p db.user=$MONITOR \
    -p db.passwd=$PASSWORD \
    -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee ${HOMEDIR}/run_${WORKLOAD}_${MONITOR}_${ITERATION}_${WORKERS}_${RESOURCE}.log
