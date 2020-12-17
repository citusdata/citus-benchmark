#!/bin/bash

# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# echo commands
set -x

if [ $# -eq 4 ] ; then
    version=$1
    shift
else version="4.0"
fi
file_name=$1
is_tpcc=$2
is_ch=$3

export PGHOST=${PGHOST:-localhost}
export PGUSER=${PGUSER:-postgres}
export PGDATABASE=${PGDATABASE:-$PGUSER}
export PGPASSWORD=${PGPASSWORD}

mkdir -p results/

# drop tables if they exist since we might be running hammerdb multiple times with different configs
psql -v "ON_ERROR_STOP=1" -f sql/drop-tables.sql

# create ch-benchmark tables in cluster
psql -v "ON_ERROR_STOP=1" -f sql/ch-benchmark-tables.sql

# distribute ch-benchmark tables
psql -f sql/ch-benchmark-distribute.sql

# set shard count
psql -c "ALTER ROLE current_user SET citus.shard_count TO 40" 2>/dev/null || true
psql -c "ALTER ROLE current_user SET citus.enable_repartition_joins to on" 2>/dev/null || true

# build hammerdb related tables
test -d "HammerDB-$version" || ./generate-hammerdb.sh "$version"
(cd HammerDB-$version && time ./hammerdbcli auto ../build.tcl | tee "../results/hammerdb_build_${file_name}.log")

exec ./run.sh "$version" "$@"
