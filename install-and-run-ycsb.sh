#!/usr/bin/env bash

export OUTPUT_FOLDER=${1:-output}
export RECORDS=$2
export OPERATIONS=$3
export SHARD_COUNT=$4

# install ycsb and postgresql jdbc driver
./install-ycsb.sh

# prepare table in psql
./prepare table.sh $SHARD_COUNT

for thread_count in 50
do

	export thread_count
	echo "THREAD_COUNT: $thread_count, RECORD_COUNT: $RECORDS, OPERATIONS: $OPERATIONS"

	export CITUS_HOST=`psql -tAX -c "select string_agg(substring(nodename from 9),',') from pg_dist_node where groupid > 0 or (select count(*) from pg_dist_node) = 1"`
    psql -c "truncate usertable"

	# load workloada
	bin/ycsb load jdbc -P workloads/workloada -p db.driver=org.postgresql.Driver -p recordcount=$RECORDS -p threadcount=$thread_count -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee $HOMEDIR/$OUTPUT_FOLDER/load_${thread_count}_${RECORDS}_${OPERATIONS}.log
	
	# run workloadc
	bin/ycsb run jdbc -P workloads/workloadc -p db.driver=org.postgresql.Driver -p operationcount=$OPERATIONS -p recordcount=$RECORDS -p threadcount=$thread_count -cp ./postgresql-42.2.14.jar -p db.user=$PGUSER -p db.passwd=$PGPASSWORD -p db.url="jdbc:postgresql://$CITUS_HOST/$PGDATABASE?loadBalanceHosts=true" | tee $HOMEDIR/$OUTPUT_FOLDER/run_${thread_count}_${RECORDS}_${OPERATIONS}.log

done

echo "Executed succesfully"

cd "$HOMEDIR"

echo "Generating CSV..."
./get-csv-ycsb.sh $OUTPUT_FOLDER
echo "Done"
