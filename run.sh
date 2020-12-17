#!/bin/bash

# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# echo commands
set -x

CH_THREAD_COUNT=1
RAMPUP_TIME=3
DEFAULT_CH_RUNTIME_IN_SECS=7200

version=$1
file_name=$2
is_tpcc=$3
is_ch=$4

psql -f sql/vacuum-ch.sql
psql -f sql/vacuum-tpcc.sql

if [ $is_ch = true ] ; then
    ./ch_benchmark.py ${CH_THREAD_COUNT} ${PGHOST} ${RAMPUP_TIME} ${file_name} >> results/ch_benchmarks_${file_name}.log &
    ch_pid=$!
    echo ${ch_pid}
fi

if [ $is_tpcc = true ] ; then
    # run hammerdb tpcc benchmark
    (cd HammerDB-$version && time ./hammerdbcli auto ../run.tcl | tee "../results/hammerdb_run_${file_name}.log")
    # filter and save the NOPM (new orders per minute) to a new file
    grep -oP '[0-9]+(?= NOPM)' "./results/hammerdb_run_${file_name}.log" >> "./results/hammerdb_nopm_${file_name}.log"
elif [ $is_ch = true ] ; then
    sleep $DEFAULT_CH_RUNTIME_IN_SECS
fi

if [ $is_ch = true ] ; then
    kill ${ch_pid}
    sleep 30
fi
