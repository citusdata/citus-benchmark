#!/bin/bash

cd $HOMEDIR/ycsb-0.17.0

export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`

bin/ycsb run jdbc \
    -P workloads/$WORKLOAD \
    -p db.driver=org.postgresql.Driver \
    -p recordcount=$RECORDS\
    -p insertstart=$INSERTSTART \
    -p insertcount=$INSERTCOUNT \
    -p operationcount=$OPERATIONS \
    -p threadcount=$THREADS \
    -cp ./postgresql-42.2.14.jar \
    -p db.user=$PGUSER \
    -p db.passwd=$PGPASSWORD \
    -p maxexecutiontime=$MAXTIME \
    -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=false" | tee ${HOMEDIR}/run_${WORKLOAD}_${THREAD}_${RECORDS}_${OPERATIONS}_${ITERATION}_${WORKERS}_${RESOURCE}_${DRIVERS}_${PART}.log
