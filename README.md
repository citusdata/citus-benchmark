# YCSB benchmarks for Citus

This repository contains utility scripts/files to run [YCSB][https://github.com/brianfrankcooper/YCSB?msclkid=6b10912cc7b911ec94793005301b742d] on Citus.

# Preparation

To run the benchmarks, you need to have psql installed.

If you are using Ubuntu / Debian on the driver node:

```bash
sudo apt -y install vim bash-completion wget
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update -y

git clone https://github.com/citusdata/citus-benchmark.git --branch ycsb-model
cd citus-benchmark

sudo apt install -y default-jre python postgresql-client-common postgresql-client-14
sudo apt-get install python3-pip -y
pip3 install fire
pip3 install pandas
pip3 install matplotlib
```

# Running YCSB

`run-benchmark.py` is the driver script and can be run using e.g.:

```
python3 run-benchmark.py [--outdir[=]<output_directory>] [--records[=]records] [--operations[=]operations] [--shard_count[=][shard_count] [--threads[=]thread_counts] citus_workload
```

This script loads with workloada the amount of records specified behind the records flag and runs workloadc (100% reads) by performing the specified amount of operations. A CSV with some statistics from the benchmark is automatically generated afterwards.


For details on the flags run:

```
./run-benchmark.py --help
```
