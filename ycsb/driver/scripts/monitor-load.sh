#!/bin/bash
cd $HOMEDIR/ycsb-0.17.0

bin/ycsb load jdbc \
    -P workloads/$WORKLOAD \
    -p db.driver=org.postgresql.Driver \
    -p recordcount=$RECORDS \
    -p threadcount=$THREADS \
    -p insertstart=$INSERTSTART \
    -p insertcount=$INSERTCOUNT_MONITOR \
    -cp ./postgresql-42.2.14.jar \
    -p db.user=monitor \
    -p db.passwd=$MONITORPW \
    -p maxexecutiontime=$MAXTIME \
    -p db.url="jdbc:postgresql://$CITUS_HOST/citus?loadBalanceHosts=true" | tee ${HOMEDIR}/load_${WORKLOAD}_${THREAD}_${RECORDS}_${ITERATION}_${WORKERS}_${RESOURCE}.mlog
