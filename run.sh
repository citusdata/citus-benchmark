#!/bin/bash

# Usage:
# ./run.sh [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name] [--shard-count[=]<shard_count>]

# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# echo commands
set -x
# fail if a command that is piped fails
set -o pipefail

CH_THREAD_COUNT=${CH_THREAD_COUNT:-1}
RAMPUP_TIME=${RAMPUP_TIME:-3}
DEFAULT_CH_RUNTIME_IN_SECS=${DEFAULT_CH_RUNTIME_IN_SECS:-7200}

source parse-arguments.sh
mkdir -p results/

psql -f sql/vacuum-ch.sql
psql -f sql/vacuum-tpcc.sql
psql -f sql/do-checkpoint.sql

if [ "$IS_CH" = true ] ; then
    ./ch_benchmark.py "${CH_THREAD_COUNT}" "${PGHOST}" "${RAMPUP_TIME}" "${BENCHNAME}" >> results/"ch_benchmarks_${BENCHNAME}.log" &
    ch_pid=$!
    echo ${ch_pid}
fi

if [ "$IS_TPCC" = true ] ; then
    # run hammerdb tpcc benchmark
    ./download-hammerdb.sh "$HAMMERDB_VERSION"
    (cd "HammerDB-$HAMMERDB_VERSION" && time ./hammerdbcli auto ../run.tcl | tee "../results/hammerdb_run_${BENCHNAME}.log")
    # filter and save the NOPM (new orders per minute) to a new file
    grep -oP '[0-9]+(?= NOPM)' "./results/hammerdb_run_${BENCHNAME}.log" | tee -a "./results/hammerdb_nopm_${BENCHNAME}.log"
elif [ "$IS_CH" = true ] ; then
    sleep "$DEFAULT_CH_RUNTIME_IN_SECS"
fi

if [ "$IS_CH" = true ] ; then
    kill ${ch_pid}
    sleep 30
fi
