#!/bin/bash


cd $HOMEDIR/ycsb-0.17.0

bin/ycsb load jdbc \
    -P workloads/$WORKLOAD \
    -p db.driver=org.postgresql.Driver \
    -p recordcount=$RECORDS \
    -p threadcount=$THREADS \
    -p insertstart=$INSERTSTART  \
    -p insertcount=$INSERTCOUNT_CITUS \
    -p maxexecutiontime=$MAXTIME \
    -cp ./postgresql-42.2.14.jar \
    -p db.user=$PGUSER \
    -p db.passwd=$PGPASSWORD \
    -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee ${HOMEDIR}/load_${WORKLOAD}_${THREAD}_${RECORDS}_${ITERATION}_${WORKERS}_${RESOURCE}.log
