#!/bin/bash
export PREFIX=$1
export HOST=$2
export WORKER_NUM=$3


ssh -t \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $PREFIX@$HOST "sudo su -c 'cat /dat/14/data/pg_log/*.log'" > $RESOURCE/pglogs/PGLOG-${WORKER_NUM}.log


