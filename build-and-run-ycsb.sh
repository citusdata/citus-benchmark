#!/bin/bash

# Usage:
# ./build-and-run.sh [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name] [--shard-count[=]<shard_count>]

export HOMEDIR=$PWD
export BENCHMARK_NAME=output
export PGDATABASE=citus

mkdir -p $BENCHMARK_NAME

./install-and-run-ycsb.sh $BENCHMARK_NAME
