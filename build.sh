#!/bin/bash

# Usage:
# ./build.sh [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name] [--shard-count[=]<shard_count>]

source parse-arguments.sh
mkdir -p results/

# drop tables if they exist since we might be running hammerdb multiple times with different configs
psql -P pager=off -v "ON_ERROR_STOP=1" -f sql/drop-tables.sql

# set Citus configurations
psql -P pager=off -c "ALTER ROLE current_user SET citus.shard_count TO $SHARD_COUNT" 2>/dev/null || true
psql -P pager=off -c "ALTER ROLE current_user SET citus.enable_repartition_joins to on" 2>/dev/null || true

sed -i.sedbak -e "s/pg_cituscompat .*/pg_cituscompat $IS_CITUS/" build.tcl
rm build.tcl.sedbak

# build hammerdb related tables
./download-hammerdb.sh "$HAMMERDB_VERSION"
start_time=$(date +%s)
(cd "HammerDB-$HAMMERDB_VERSION" && time ./hammerdbcli auto ../build.tcl | tee "../results/hammerdb_build_${BENCHNAME}.log")
end_time=$(date +%s)

# Do three-decimal fixed arithmetic using only bash to calculate the number of
# minutes the build took. (floating point arithmetic does not exist in bash)
# Inspired by: https://stackoverflow.com/a/35402635/2570866
thousands_of_minutes_spent=$(printf "%04d" $(( (end_time - start_time) * 1000 / 60)))
minutes_spent="${thousands_of_minutes_spent:0:-3}.${thousands_of_minutes_spent: -3}"
echo "$minutes_spent" | tee "results/hammerdb_minutesbuild_${BENCHNAME}.log"

# Needs to be done after building TPC tables, otherwise HammerDB complains that
# tables already exist in the database.
if [ "$IS_CH" = true ] ; then
    # create ch-benchmark tables in cluster
    psql -P pager=off -v "ON_ERROR_STOP=1" -f sql/ch-benchmark-tables.sql

    if [ "$IS_CITUS" = true ]; then
        # distribute ch-benchmark tables
        psql -P pager=off -f sql/ch-benchmark-distribute.sql
    fi
fi

