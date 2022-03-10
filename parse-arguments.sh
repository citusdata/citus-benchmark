#!/usr/bin/env bash
# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# fail if a command that is piped fails
set -o pipefail

helpstring="Usage: [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name] --shard-count=<shard_count>

Apart from these arguments this script relies on the following libpq
environment variables:
- PGPASSWORD (required)
- PGHOST (default: localhost)
- PGPORT (default: 5432)
- PGUSER (default: postgres)
- PGDATABASE (default: \$PGUSER)

Arguments:
  --hammerdb-version    What version of HammerDB to use to run the benchmark.
                        To be able to run use this script to run Citus
                        benchmarks it is required to use '4.4' here. All
                        other versions only work for standard Postgres
                        benchmarks.
                        (default: 4.4)
  --ch                  Run both HammerDB TPROC-C and CH-benCHmark queries at
                        the same time.
  --ch-queries-only     Run only CH-benCHmark queries (so don't run HammerDB
                        TPROC-C queries
  --no-citus            Build the dataset and run the benchmark for standard
                        Postgres instead of for Citus. This also requires
                        setting pg_cituscompat to false in run.tcl
  --name                The name you want to give to the benchmark run. This
                        determines the filenames in the results directory.
                        (default: timestamp of start of benchmark)
  --shard-count         The amount of shards each distributed table should
                        have. It's important to make sure that this is
                        divisible by the number of worker nodes that you have,
                        otherwise the load will not be evenly spread across
                        nodes.
                        (default: 48)
"

IS_CH_ONLY=${IS_CH_ONLY:-false}
IS_CH_AND_TPCC=${IS_CH_AND_TPCC:-false}
IS_TPCC=${IS_TPCC:-true}
IS_CH=${IS_CH:-false}
IS_CITUS=${IS_CITUS:-true}
HAMMERDB_VERSION=${HAMMERDB_VERSION:-4.4}
isodate=$(date +"%Y-%m-%dT%H:%M:%S")
BENCHNAME=${BENCHNAME:-${isodate}}
SHARD_COUNT=${SHARD_COUNT:-48}

# inspired by: https://stackoverflow.com/a/7680682/2570866
optspec=":h-:"
while getopts "$optspec" optchar; do
    case "${optchar}" in
        -)
            case "${OPTARG}" in
                hammerdb-version)
                    if [ -z ${!OPTIND+x} ]; then
                        echo "error: --hamerdb-version requires argument" >&2
                        exit 2
                    fi
                    HAMMERDB_VERSION="${!OPTIND}"
                    OPTIND=$(( OPTIND + 1 ))
                    ;;
                hammerdb-version=*)
                    HAMMERDB_VERSION=${OPTARG#*=}
                    ;;
                name)
                    if [ -z ${!OPTIND+x} ]; then
                        echo "error: --name requires argument" >&2
                        exit 2
                    fi
                    BENCHNAME="${!OPTIND}"
                    OPTIND=$(( OPTIND + 1 ))
                    ;;
                name=*)
                    BENCHNAME=${OPTARG#*=}
                    ;;
                shard-count)
                    if [ -z ${!OPTIND+x} ]; then
                        echo "error: --shard-count requires argument" >&2
                        exit 2
                    fi
                    SHARD_COUNT="${!OPTIND}"
                    OPTIND=$(( OPTIND + 1 ))
                    ;;
                shard-count=*)
                    SHARD_COUNT=${OPTARG#*=}
                    ;;
                no-citus)
                    IS_CITUS=false
                    ;;
                ch-queries-only)
                    IS_CH_ONLY=true
                    IS_CH=true
                    IS_TPCC=false
                    ;;
                ch)
                    IS_CH_AND_TPCC=true
                    IS_CH=true
                    IS_TPCC=true
                    ;;
                help)
                    echo "$helpstring" >&2
                    exit 0
                    ;;
                *)
                    echo "error: Unknown option --${OPTARG}" >&2
                    echo "$helpstring" >&2
                    exit 2
                    ;;
            esac;;
        h)
            echo "$helpstring" >&2
            exit 0
            ;;
        *)
            ;;
    esac
done

if [ $IS_CH_ONLY = true ] && [ $IS_CH_AND_TPCC = true ]; then
    echo "error: You can only provide one of --ch and --ch-queries-only, not both" >&2
    exit 2
fi

export PGHOST=${PGHOST:-localhost}
export PGPORT=${PGPORT:-5432}
export PGUSER=${PGUSER:-postgres}
export PGDATABASE=${PGDATABASE:-$PGUSER}
if [ -z "${PGPASSWORD+x}" ]; then
    echo "error: The PGPASSWORD environment variable must be set" >&2
    exit 2
fi
export PGPASSWORD=${PGPASSWORD}

# Only parse the variables once and then export them to any nested scripts,
# this way the BENCHNAME is the same for both the build and the run when
# sourcing parse-arguments.sh from build-and-run.sh.
export IS_CH_ONLY
export IS_CH_AND_TPCC
export IS_TPCC
export IS_CH
export IS_CITUS
export BENCHNAME
export HAMMERDB_VERSION
export SHARD_COUNT

# echo commands after we parsed the arguments
set -x
