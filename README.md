# HammerDB TPROC-C and CH benchmarking tool for Citus and PostgreSQL

This repository contains two main sections:
1. Scripts and files to run [HammerDB][hammerdb] and the [CH-benCHmark][ch] on Citus
   and regular PostgreSQL. These are located in the root directory and the
   `README` that you're reading now explains how to use them.
2. Scripts and files to run those same benchmarks on Azure in a completely
   automated fashion. With these scrips you can start multiple Citus benchmarks
   on Azure with just a single command. These scripts and the README that
   explains how to use them can be found in the [`azure`
   directory](https://github.com/citusdata/citus-benchmark)

# Preparation

To run the benchmarks, you need to have psql installed.

If you are using CentOS 8 on the driver node, you can use the following steps:

```bash
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm epel-release
sudo yum update -y nss curl libcurl
sudo yum install -y screen postgresql13
sudo yum groupinstall -y "Development tools"
git clone https://github.com/citusdata/citus-benchmark.git
cd citus-benchmark
```

If you are using Ubuntu / Debian on the driver node:

```bash
sudo apt -y install vim bash-completion wget
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update -y
sudo apt install -y postgresql-client-13
git clone https://github.com/citusdata/citus-benchmark.git
cd citus-benchmark
```

# Running HammerDB TPROC-C with CH-benCHmark support

`build-and-run.sh` is the driver script and can be run using:

```bash
./build-and-run.sh [--hammerdb-version[=]<version>] [--ch|--ch-queries-only] [--no-citus] [--name[=]name] [--shard-count[=]<shard_count>]
```

For details on the flags run:
```
./build-and-run.sh --help
```

The script relies on libpq environment variables for connecting to the database.

Example usage that runs only HammerDB TPROC-C without CH-benCHmark queries:
```bash
export PGHOST=203.0.113.4
export PGUSER=citus
export PGDATABASE=citus
export PGPASSWORD=
./build-and-run.sh
```

## Running CH-bencCHmark queries

When running `build-and-run.sh` with the default flags, only HammerDB TPROC-C
will be ran. If you want to run the CH-benCHmark analytical queries you can
specify the `--ch` flag to run the benchmark with both TPROC-C and CH-benCHmark
queries at the same time. Or if you only want to run the CH analytical queries
without TPROC-C you can specify the `--ch-queries-only` flag.

## Changing HammerDB configurations

`build.tcl` is used to build hammerdb tables and `run.tcl` is used to run the test.
You can change hammerdb configurations from those files.

*pg_count_ware/pg_num_vu* should be at least 4. https://www.hammerdb.com/blog/uncategorized/how-many-warehouses-for-the-hammerdb-tpc-c-test/

## Running against standard Postgres (without Citus)

You can also use this repo to run these benchmarks against standard Postgres if
you want. If you pass the `--no-citus` flag to `build-and-run.sh` it will not
distribute any of the tables.

# Checklist for running the benchmark
- [ ] Make sure that worker node count is a divisor of the value of
  `--shard-count`, otherwise some nodes will have more shards and the load will
  not be distributed evenly.
- [ ] Make sure that `max_connections` is high enough based on `vuset vu` in
  `run.tcl`. `max_connections` should be at least 150 more than the value given
  to `vuset vu`.

# Implementation details
`ch_benchmark.py` is a utility script to send the extra 22 queries(analytical
queries). By default one thread is used for sending the analytical queries. The
start index for each thread is randomly chosen with a fixed seed so that it will
be same across different platforms.

[hammerdb]: https://github.com/TPC-Council/HammerDB
[ch]: https://db.in.tum.de/research/projects/CHbenCHmark/
