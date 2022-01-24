#!/bin/bash
set -euxo pipefail
pgbench -i -I dtp
psql -P pager=off -v "ON_ERROR_STOP=1" -f sql/pgbench-reference.sql
pgbench -i -I gv
