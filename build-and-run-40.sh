#!/bin/bash

# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# echo commands
set -x

file_name=$1
is_tpcc=$2
is_ch=$3

CH_THREAD_COUNT=1
RAMPUP_TIME=3
DEFAULT_CH_RUNTIME_IN_SECS=7200

export PGHOST=${PGHOST:-localhost}
export PGUSER=${PGUSER:-postgres}
export PGDATABASE=${PGDATABASE:-$PGUSER}
export PGPASSWORD=${PGPASSWORD}

current_dir=$PWD

sed -i -e "s/diset connection pg_host .*/diset connection pg_host $PGHOST/" build.tcl run.tcl
sed -i -e "s/diset tpcc pg_dbase .*/diset tpcc pg_dbase $PGDATABASE/" build.tcl run.tcl
sed -i -e "s/diset tpcc pg_defaultdbase .*/diset tpcc pg_defaultdbase $PGDATABASE/" build.tcl run.tcl
sed -i -e "s/diset tpcc pg_user .*/diset tpcc pg_user $PGUSER/" build.tcl run.tcl
sed -i -e "s/diset tpcc pg_superuser .*/diset tpcc pg_superuser $PGUSER/" build.tcl run.tcl
sed -i -e "s/diset tpcc pg_pass .*/diset tpcc pg_pass $PGPASSWORD/" build.tcl run.tcl
sed -i -e "s/diset tpcc pg_superuserpass .*/diset tpcc pg_superuserpass $PGPASSWORD/" build.tcl run.tcl

mkdir -p results/

# drop tables if they exist since we might be running hammerdb multiple times with different configs
psql -v "ON_ERROR_STOP=1" -f sql/drop-tables.sql

# create ch-benchmark tables in cluster
psql -v "ON_ERROR_STOP=1" -f sql/ch-benchmark-tables.sql

# distribute ch-benchmark tables
psql -f sql/ch-benchmark-distribute.sql

# set shard count
psql -c "ALTER ROLE current_user SET citus.shard_count TO 40" 2>/dev/null || true

# build hammerdb related tables
(cd HammerDB-4.0 && time ./hammerdbcli auto $current_dir/build.tcl | tee "$current_dir/results/hammerdb_build_${file_name}.log")

# distribute tpcc tables in cluster
psql -f sql/tpcc-distribute.sql

# distribute functions in cluster 
psql -f sql/tpcc-distribute-funcs.sql

psql -f sql/vacuum-ch.sql
psql -f sql/vacuum-tpcc.sql

if [ $is_ch = true ] ; then
    ./ch_benchmark.py ${CH_THREAD_COUNT} ${PGHOST} ${RAMPUP_TIME} ${file_name} >> results/ch_benchmarks_${file_name}.log &
    ch_pid=$!
    echo ${ch_pid}
fi

if [ $is_tpcc = true ] ; then
    # run hammerdb tpcc benchmark
    (cd HammerDB-4.0 &&  time ./hammerdbcli auto $current_dir/run.tcl | tee "$current_dir/results/hammerdb_run_${file_name}.log" )
    # filter and save the NOPM( new orders per minute) to a new file
    grep -oP '[0-9]+(?= NOPM)' "./results/hammerdb_run_${file_name}.log" >> "./results/hammerdb_nopm_${file_name}.log"
else
    sleep $DEFAULT_CH_RUNTIME_IN_SECS
fi

if [ $is_ch = true ] ; then
    kill ${ch_pid}
    sleep 30
fi
