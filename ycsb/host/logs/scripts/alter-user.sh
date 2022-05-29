#!/bin/bash

export PREFIX=$1
export HOST=$2
export LOG_STATEMENT=$(echo $(cat log-statement))
export LOG_DURATION=$(echo $(cat log-duration))
export LOG_MIN_MESSAGES=$(echo $(cat log-min-messages))
export PERMISSIONS=$(echo $(cat permissions))

ssh -t \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $PREFIX@$HOST "$LOG_STATEMENT; $LOG_MIN_MESSAGES; $LOG_DURATION; $PERMISSIONS"


