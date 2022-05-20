#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

# check whether csv file exists in current directory
compgen -G "*.csv" > /dev/null || { >&2 echo No run has finished yet ; exit 1 ; }

for run_file in *.csv; do
    echo $(cat $run_file)
done
