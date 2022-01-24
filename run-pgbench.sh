#!/bin/bash

set -euo pipefail

concurrency=$1
seconds=${2:-60}

export PGHOST=${PGHOST:-localhost}
export PGPORT=${PGPORT:-5432}
export PGUSER=${PGUSER:-postgres}
export PGDATABASE=${PGDATABASE:-$PGUSER}
if [ -z "${PGPASSWORD+x}" ]; then
    echo "error: The PGPASSWORD environment variable must be set" >&2
    exit 2
fi
export PGPASSWORD=${PGPASSWORD}

cd "$(dirname "$0")" || exit 1

clean_exit() {
    exit_code=$?
    # kill all child processes.
    kill $(jobs -pr)
    exit $exit_code
}

trap "exit" INT TERM
trap 'clean_exit' EXIT

for _ in $(seq "$concurrency"); do
  pgbench --select-only -j 1 -c 35 -T "$seconds" --no-vacuum &
done
wait
