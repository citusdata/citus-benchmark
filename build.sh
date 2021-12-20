#!/bin/bash

# Usage:
# ./build.sh [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name] [--shard-count[=]<shard_count>]

source parse-arguments.sh
mkdir -p results/

# drop tables if they exist since we might be running hammerdb multiple times with different configs
psql -v "ON_ERROR_STOP=1" -f sql/drop-tables.sql

# set Citus configurations
psql -c "ALTER ROLE current_user SET citus.shard_count TO $SHARD_COUNT" 2>/dev/null || true
psql -c "ALTER ROLE current_user SET citus.enable_repartition_joins to on" 2>/dev/null || true

sed -i.sedbak -e "s/pg_cituscompat .*/pg_cituscompat $IS_CITUS/" build.tcl
rm build.tcl.sedbak

# build hammerdb related tables
test -d "HammerDB-$HAMMERDB_VERSION" || ./generate-hammerdb.sh "$HAMMERDB_VERSION"
(cd "HammerDB-$HAMMERDB_VERSION" && time ./hammerdbcli auto ../build.tcl | tee "../results/hammerdb_build_${BENCHNAME}.log")

# Needs to be done after building TPC tables, otherwise HammerDB complains that
# tables already exist in the database.
if [ "$IS_CH" = true ] ; then
    # create ch-benchmark tables in cluster
    psql -v "ON_ERROR_STOP=1" -f sql/ch-benchmark-tables.sql

    if [ "$IS_CITUS" = true ]; then
        # distribute ch-benchmark tables
        psql -f sql/ch-benchmark-distribute.sql
    fi
fi

