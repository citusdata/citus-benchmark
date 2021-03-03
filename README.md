# HammerDB TPROC-C and CH benchmarking tool for Citus and PostgreSQL

This repository contains utility scripts/files to run [HammerDB](https://github.com/TPC-Council/HammerDB) and the [CH-benCHmark](https://db.in.tum.de/research/projects/CHbenCHmark/) on Citus and regular PostgreSQL.

# Preparation

To run the benchmarks, you need to have psql installed.

If you are using CentOS 8 on the driver node, you can use the following steps:

```bash
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm epel-release
sudo yum update -y nss curl libcurl
sudo yum install -y screen postgresql13
sudo yum groupinstall -y "Development tools"
git clone https://github.com/citusdata/ch-benchmark.git
cd ch-benchmark
```

If you are using Ubuntu / Debian on the driver node:

```bash
sudo apt -y install vim bash-completion wget
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update -y
sudo apt install -y postgresql-client-13
git clone https://github.com/citusdata/ch-benchmark.git
cd ch-benchmark
```

# Running HammerDB TPROC-C with CH-benCHmark support

Generate a patched HammerDB version with:
```bash
./generate-hammerdb.sh 4.0
```

`build-and-run.sh` is the driver script and can be run using:

```bash
./build-and-run.sh <version 3.3 or 4.0> <prefix> <is_tpcc> <is_ch>
```

* prefix indicates the prefix used in result files
* if `is_tpcc` is `true`, then the transaction queries will be run.
* if `is_ch` is `true`, then the analytical queries will be run.

The script relies on libpq environment variables for connecting to the database.

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

`ch_benchmark.py` is a utility script to send the extra 22 queries(analytical queries). By default one thread is used for sending the analytical queries. The start index for each thread is randomly chosen with a fixed seed so that it will be same across different platforms.

Checklist for running benchmark:

* Make sure that node count is a divisor of shard count, otherwise some nodes will have more shards and the load will not be distribuded evenly.
* Make sure that max_connections is high enough based on #vuuser. max_connections should be at least 150 more than #vuuser.
* Make sure that you do a checkpoint before starting the test, the `build-and-run.sh` already does this. Otherwise the timing of checkpoint can affect the results for short tests.
