#!/bin/bash

# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# echo commands
set -x

hostname=$1
file_name=$2
is_tpcc=$3
is_ch=$4
username=$5

password=""
port=5432

CH_THREAD_COUNT=1
RAMPUP_TIME=3
DEFAULT_CH_RUNTIME_IN_SECS=7200

export PGHOST=${hostname}
export PGPORT=${port}
export PGPASSWORD=${password}
export PGUSER=${username}
export PGDATABASE=${username}

mkdir -p results/

# drop tables if they exist since we might be running hammerdb multiple times with different configs
psql -v "ON_ERROR_STOP=1" -f sql/drop-tables.sql

# create ch-benchmark tables in cluster
psql -v "ON_ERROR_STOP=1" -f sql/ch-benchmark-tables.sql

# distribute ch-benchmark tables
psql -f sql/ch-benchmark-distribute.sql

# build hammerdb related tables
(cd $HOME/HammerDB-3.3 && ./hammerdbcli auto build.tcl | tee -a ./results/build_${file_name}.log)

# distribute tpcc tables in cluster
psql -f sql/tpcc-distribute.sql

# distribute functions in cluster 
psql -f sql/tpcc-distribute-funcs.sql

psql -f sql/vacuum-ch.sql
psql -f sql/vacuum-tpcc.sql

psql -f sql/do-checkpoint.sql

if [ $is_ch = true ] ; then
    ./ch_benchmark.py ${CH_THREAD_COUNT} ${hostname} ${RAMPUP_TIME} >> results/ch_benchmarks.log &
    ch_pid=$!
    echo ${ch_pid}
fi

if [ $is_tpcc = true ] ; then
    # run hammerdb tpcc benchmark
    (cd $HOME/HammerDB-3.3 && ./hammerdbcli auto run.tcl | tee -a ./results/run_${file_name}.log)
    # filter and save the NOPM( new orders per minute) to a new file
    grep -oP '[0-9]+(?= NOPM)' ./results/run_${file_name}.log >> ./results/${file_name}_NOPM.log
else
    sleep $DEFAULT_CH_RUNTIME_IN_SECS
fi

if [ $is_ch = true ] ; then
    kill ${ch_pid}
    sleep 30
fi

psql "${connection_string}" -f sql/tables-total-size.sql >> ./results/table_total_size.out
