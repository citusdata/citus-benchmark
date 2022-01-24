#!/bin/bash
set -euxo pipefail
pgbech -i -I dt
psql -P pager=off -v "ON_ERROR_STOP=1" -f sql/pgbench-reference.sql
pgbech -i -I gvp
