#!/bin/bash

RUNS_FILE=$1
# Get the full path of the file before changing directory
RUNS_FILE=$(realpath "$RUNS_FILE")

cd "$(dirname "$0")" || exit 1

set -ue

declare -a name_array=()

clean_exit() {
    # save the current exit code. That way we can use it after we cleaned up
    # the child processes.
    exit_code=$?
    cleanup_and_exit() {
        set -ux
        # cleanup all resource groups
        for name in "${name_array[@]}"; do
            ./cleanup.sh "$name" &
        done
        wait

        # Finally exit ourselves with the saved exit code
        exit $exit_code
    }
    trap cleanup_and_exit TERM
    # kill all processes in the current process group, this is including
    # this process itself. That's why we set another trap right before that
    # allows us to clean up.
    kill 0
}

trap "exit" INT TERM
trap 'clean_exit' EXIT

set -x
while read -r line; do
    # skip empty lines
    if [ -z "$line" ]; then
        continue
    fi

    IFS=',' read -r -a split_line <<< "$line"

    for i in $(seq "${split_line[0]}"); do
        random_string=$(< /dev/urandom tr -dc 'a-z0-9' | fold -w 8 | head -n 1)
        name=$USER-hammerdb-$random_string-$i
        name_array+=("$name")

        # If one of these fails, continue with the rest
        set +e
        set -x
        ./run-benchmark.sh "$name" "${split_line[@]:1}" &
        set +x
        set -e
    done
done < "$RUNS_FILE"
wait
exit
