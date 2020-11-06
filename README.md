# HammerDB OSS-TPC-C and CH benchmarking tool

This repository contains utility scripts/files that are used to run the [CH-benCHmark](https://db.in.tum.de/research/projects/CHbenCHmark/) on Citus and regular PostgreSQL.

HammerDB is a standard open source benchmarking tool available from https://github.com/TPC-Council/HammerDB . It supports OSS-TPC-C and OSS-TPC-H workloads. We use HammerDB for running the C part of the CH benchmark, but you can also use this tool to run the OSS-TPC-C-based workload by itself.

# Preparation

If you are using CentOS 8 on the driver node, you can use the following steps to prepare:

```bash
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo yum update -y nss curl libcurl
sudo yum install -y screen postgresql13
sudo yum groupinstall -y "Development tools"
git clone https://github.com/citusdata/ch-benchmark.git
cd ch-benchmark
```

# Running HammerDB OSS-TPC-C with CH-benCHmark support

`build-and-run.sh` is the driver script and can be run using:

```bash
./build-and-run.sh <prefix> <is_tpcc> <is_ch>
```

* prefix indicates the prefix used in result files
* if `is_tpcc` is `true`, then the transaction queries will be run.
* if `is_ch` is `true`, then the analytical queries will be run.

The script relies on libpq environment variables for connecting to the database.

Make sure Citus is configured with the following `citus.replication_model` setting before running the benchmark:
```sql
postgres=# show citus.replication_model ;
┌─────────────────────────┐
│ citus.replication_model │
├─────────────────────────┤
│ streaming               │
└─────────────────────────┘
(1 row)
```

Example usage:
```bash
export PGHOST=203.0.113.4
export PGUSER=citus
export PGDATABASE=citus
export PGPASSWORD=
./build-and-run.sh tpcc-run true false
```

So if you want to run both tpcc and analytical queries concurrently, you should set both of them to true.

`build.tcl` is used to build hammerdb tables and `run.tcl` is used to run the test.
You can change hammerdb configurations from those files.

*pg_count_ware/pg_num_vu* should be at least 4. https://www.hammerdb.com/blog/uncategorized/how-many-warehouses-for-the-hammerdb-tpc-c-test/

In order to make the build step faster, we have forked the hammerdb and add `distribute tables` at the beginning of the build.
You should replace `pgoltp.tcl` with https://github.com/SaitTalhaNisanci/HammerDB/blob/citus/src/postgresql/pgoltp.tcl

`ch_benchmark.py` is a utility script to send the extra 22 queries(analytical queries). By default one thread is used for sending the analytical queries. The start index for each thread is randomly chosen with a fixed seed so that it will be same across different platforms.

Checklist for running benchmark:

* Make sure that node count is a divisor of shard count, otherwise some nodes will have more shards and the load will not be distribuded evenly.
* Make sure that max_connections is high enough based on #vuuser. max_connections should be at least 150 more than #vuuser.
* Make sure that you do a checkpoint before starting the test, the `build-and-run.sh` already does this. Otherwise the timing of checkpoint can affect the results for short tests.
