#!/bin/bash

# Usage:
# ./build-and-run.sh [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name]

source parse-arguments.sh

./build.sh
./run.sh
