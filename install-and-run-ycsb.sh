#!/usr/bin/env bash

export BENCHMARK_NAME=${1:-fixed}

# sudo apt install -y default-jre python postgresql-client-common postgresql-client-12

wget https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz

tar xfvz ycsb-0.17.0.tar.gz

cd ycsb-0.17.0

wget https://jdbc.postgresql.org/download/postgresql-42.2.14.jar

psql <<EOF
DROP TABLE if EXISTS usertable;

CREATE TABLE usertable (
        YCSB_KEY VARCHAR(255) PRIMARY KEY,
        FIELD0 TEXT, FIELD1 TEXT,
        FIELD2 TEXT, FIELD3 TEXT,
        FIELD4 TEXT, FIELD5 TEXT,
        FIELD6 TEXT, FIELD7 TEXT,
        FIELD8 TEXT, FIELD9 TEXT
);
SELECT create_distributed_table('usertable', 'ycsb_key', colocate_with := 'none', shard_count := 60);
CREATE OR REPLACE FUNCTION dummy(key varchar)
RETURNS void AS \$\$
BEGIN
END;
\$\$ LANGUAGE plpgsql;
SELECT create_distributed_function('dummy(varchar(255))', '\$1', colocate_with :='usertable');

EOF

export record_count=2000000
export operation_count=20000000

for thread_count in 200 400 600 800 990
do
	
	export thread_count
	echo "THREAD_COUNT: $thread_count, RECORD_COUNT: $record_count, OPERATION_COUNT: $operation_count"

	export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0;"`
	psql -c "truncate usertable"
	bin/ycsb load jdbc -P workloads/workloada -p db.driver=org.postgresql.Driver -p recordcount=$record_count -p threadcount=$thread_count -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee $HOMEDIR/$BENCHMARK_NAME/load_${thread_count}_${record_count}_${operation_count}.log

	grep Throughput $HOMEDIR/$BENCHMARK_NAME/load_${thread_count}_${record_count}_${operation_count}.log | awk '{print $3}'

	bin/ycsb run jdbc -P workloads/workloadc -p db.driver=org.postgresql.Driver -p operationcount=$operation_count -p recordcount=$record_count -p threadcount=$thread_count -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee $HOMEDIR/$BENCHMARK_NAME/run_${thread_count}_${record_count}_${operation_count}.log

	grep Throughput $HOMEDIR/$BENCHMARK_NAME/run_${thread_count}_${record_count}_${operation_count}.log | awk '{print $3}'
done

echo "Executed succesfully"

cd "$HOMEDIR"

echo "Generating CSV..."
./get-csv-ycsb.sh $BENCHMARK_NAME
echo "Done"
