#!/bin/bash

# Usage:
# ./build-and-run.sh [HammerDB version] {file_name} {is_tpcc} {is_tpch}
# Example:
# ./build-and-run.sh 4.3 myfirstbenchmark true false

# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# echo commands
set -x

if [ $# -eq 4 ] ; then
    version=$1
    shift
else version="4.3"
fi
file_name=$1
is_tpcc=${2:-true}
is_ch=${3:-false}

export PGHOST=${PGHOST:-localhost}
export PGPORT=${PGPORT:-5432}
export PGUSER=${PGUSER:-postgres}
export PGDATABASE=${PGDATABASE:-$PGUSER}
export PGPASSWORD=${PGPASSWORD}

./build.sh "$version" "$file_name" "$is_tpcc" "$is_ch"
./run.sh "$version" "$file_name" "$is_tpcc" "$is_ch"
