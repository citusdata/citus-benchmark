#!/bin/bash
export PREFIX=$1
export HOST=$2

ssh -t \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $PREFIX@$HOST "sudo cat /dat/14/data/pg_logs/*" > $resource/pglogs 2>/dev/null
