isodate=$(date +"%Y-%m-%dT%H:%M:%S")

export IS_CH_ONLY="false"
export IS_CH_AND_TPCC="false"
export IS_CH="false"
export IS_TPCC="true"
export IS_CITUS="true"
export BENCHNAME=${isodate}
export HAMMERDB_VERSION="4.12"
export SHARD_COUNT=48

export PGPORT="5432"
export PGUSER="cloudsa"
export PGDATABASE="postgres"
export PGHOST="unset"
export PGPASSWORD="unset"
