#!/usr/bin/env bash
# fail if trying to reference a variable that is not set.
set -u
# exit immediately if a command fails
set -e
# fail if a command that is piped fails
set -o pipefail

helpstring="usage: [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name]"

IS_CH_ONLY=${IS_CH_ONLY:-false}
IS_CH_AND_TPCC=${IS_CH_AND_TPCC:-false}
IS_TPCC=${IS_TPCC:-true}
IS_CH=${IS_CH:-false}
IS_CITUS=${IS_CITUS:-true}

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
                    HAMMERDB_VERSION="${!OPTIND}"; OPTIND=$(( OPTIND + 1 ))
                    BENCHNAME="$OPTARG"
                    ;;
                hammerdb-version=*)
                    HAMMERDB_VERSION=${OPTARG#*=}
                    ;;
                name)
                    if [ -z ${!OPTIND+x} ]; then
                        echo "error: --name requires argument" >&2
                        exit 2
                    fi
                    BENCHNAME="${!OPTIND}"; OPTIND=$(( OPTIND + 1 ))
                    ;;
                name=*)
                    BENCHNAME=${OPTARG#*=}
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
    echo "error: You can only provide one of --ch and --h-only, not both" >&2
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

isodate=$(date +"%Y-%m-%dT%H:%M:%S")
BENCHNAME=${BENCHNAME:-${isodate}}
HAMMERDB_VERSION=${HAMMERDB_VERSION:-4.3-custom}

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

# echo commands after we parsed the arguments
set -x
