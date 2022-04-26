#!/usr/bin/env bash

export BENCHMARK_NAME=${1:-output}
export RECORDS=$2
export OPERATIONS=$3
export SHARD_COUNT=$4

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
SELECT create_distributed_table('usertable', 'ycsb_key', colocate_with := 'none', shard_count := "$SHARD_COUNT");
CREATE OR REPLACE FUNCTION dummy(key varchar)
RETURNS void AS \$\$
BEGIN
END;
\$\$ LANGUAGE plpgsql;
SELECT create_distributed_function('dummy(varchar(255))', '\$1', colocate_with :='usertable');

EOF

for thread_count in 800
do

	export thread_count
	echo "THREAD_COUNT: $thread_count, RECORD_COUNT: $RECORDS, OPERATIONS: $OPERATIONS"

	export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`
    psql -c "truncate usertable"

	# load workloada
	bin/ycsb load jdbc -P workloads/workloada -p db.driver=org.postgresql.Driver -p recordcount=$RECORDS -p threadcount=$thread_count -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee $HOMEDIR/$BENCHMARK_NAME/load_${thread_count}_${RECORDS}_${OPERATIONS}.log
	
	# run workloadc
	bin/ycsb run jdbc -P workloads/workloadc -p db.driver=org.postgresql.Driver -p operationcount=$OPERATIONS -p recordcount=$RECORDS -p threadcount=$thread_count -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee $HOMEDIR/$BENCHMARK_NAME/run_${thread_count}_${RECORDS}_${OPERATIONS}.log

done

echo "Executed succesfully"

cd "$HOMEDIR"

echo "Generating CSV..."
./get-csv-ycsb.sh $OUTPUT_FOLDER
echo "Done"
