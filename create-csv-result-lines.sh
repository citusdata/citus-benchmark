#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

compgen -G "results/hammerdb_run_*.log" > /dev/null || { >&2 echo No run has started yet ; exit 1 ; }
for run_file in results/hammerdb_run_*.log; do
    NAME=${run_file#results/hammerdb_run_}
    NAME=${NAME%.log}
    MINUTESBUILD_FILE="results/hammerdb_minutesbuild_$NAME.log"
    NOPM_FILE="results/hammerdb_nopm_$NAME.log"
    if [ -f "$MINUTESBUILD_FILE" ]; then
        MINUTESBUILD=$(< "$MINUTESBUILD_FILE" tr -d '\n')
    else
        MINUTESBUILD=
    fi
    if [ -f "$NOPM_FILE" ]; then
        NOPM=$(< "$NOPM_FILE" tr -d '\n')
    else
        >&2 echo "Run $NAME has not completed yet"
        exit 1
    fi
    echo "$NAME,$MINUTESBUILD,$NOPM"
done
