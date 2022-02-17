#!/bin/bash

# Usage:
# ./build-and-run.sh [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name] [--shard-count[=]<shard_count>]


export HOMEDIR=$PWD
export BENCHMARK_NAME=output
export PGDATABASE=citus

# BENCHMARK_NAME=${1:-standard}
# CLUSTER_NAME=${CLUSTER_NAME:-lottecitus}
# PGPASSWORD=${PGPASSWORD:-thesis123$}

# export CLUSTER_NAME
# export PGPASSWORD
# export PGHOST=c.$CLUSTER_NAME.postgres.database.azure.com
# export PGDATABASE=citus
# export PGUSER=citus
# export HOMEDIR=$PWD
# export BENCHMARK_NAME=${BENCHMARK_NAME}-output

mkdir -p $BENCHMARK_NAME

sh -ex ./install-and-run-ycsb.sh $BENCHMARK_NAME
