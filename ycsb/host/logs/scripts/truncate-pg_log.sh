#!/bin/bash
export PREFIX=$1
export HOST=$2
export LOGNAME=$(echo $(./echo-truncate.sh ${3}))

ssh -t \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $PREFIX@$HOST "sudo su -c ${LOGNAME}"


