#!/bin/bash

export PREFIX=$1
export HOST=$2
export LOG_STATEMENT=$(echo $(cat log-statement))
export LOG_DURATION=$(echo $(cat log-duration))
export LOG_MIN_MESSAGES=$(echo $(cat log-min-messages))
export LOG_STATEMENT_TWO=$(echo $(cat log-statement-2))
export LOG_DURATION_TWO=$(echo $(cat log-duration-2))
export LOG_MIN_MESSAGES_TWO=$(echo $(cat log-min-messages-2))
export PERMISSIONS=$(echo $(cat permissions))

ssh -t \
    -o "UserKnownHostsFile=/dev/null" \
    -o "StrictHostKeyChecking=no" \
    $PREFIX@$HOST "$LOG_STATEMENT; $LOG_MIN_MESSAGES; $LOG_DURATION; $PERMISSIONS"


    # $PREFIX@$HOST "$LOG_STATEMENT; $LOG_STATEMENT_TWO; $LOG_DURATION; $LOG_DURATION_TWO; $LOG_MIN_MESSAGES; $LOG_MIN_MESSAGES_TWO; $PERMISSIONS"


