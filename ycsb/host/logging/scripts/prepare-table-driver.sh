#!/bin/bash

export SHARD_COUNT=$1
export PGHOST=$2
export PGDATABASE=$3
export PGUSER=$4
export PGPASSWORD=$5

psql -h $PGHOST -U $PGUSER -d $PGDATABASE <<EOF
DROP TABLE if EXISTS usertable;

CREATE TABLE usertable (
        YCSB_KEY VARCHAR(255) PRIMARY KEY,
        FIELD0 TEXT, FIELD1 TEXT,
        FIELD2 TEXT, FIELD3 TEXT,
        FIELD4 TEXT, FIELD5 TEXT,
        FIELD6 TEXT, FIELD7 TEXT,
        FIELD8 TEXT, FIELD9 TEXT
);
SELECT create_distributed_table('usertable', 'ycsb_key', colocate_with := 'none', shard_count := '$SHARD_COUNT');
CREATE OR REPLACE FUNCTION dummy(key varchar)
RETURNS void AS \$\$
BEGIN
END;
\$\$ LANGUAGE plpgsql;
SELECT create_distributed_function('dummy(varchar(255))', '\$1', colocate_with :='usertable');

EOF
