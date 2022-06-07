#!/bin/bash
cd $HOMEDIR/ycsb-0.17.0

bin/ycsb run jdbc \
     -P workloads/$WORKLOAD \
    -p db.driver=org.postgresql.Driver \
    -p recordcount=$RECORDS \
    -p threadcount=$WORKERS \
    -p insertstart=$INSERTSTART \
    -p insertcount=$INSERTCOUNT_MONITOR \
    -p operationcount=$INSERTCOUNT_MONITOR \
    -cp ./postgresql-42.2.14.jar \
    -p db.user=monitor \
    -p db.passwd=$MONITORPW \
    -p maxexecutiontime=$MAXTIME \
    -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee ${HOMEDIR}/run_${WORKLOAD}_${THREAD}_${INSERTCOUNT_MONITOR}_${RECORDS}_${ITERATION}_${WORKERS}_${RESOURCE}.mlog
