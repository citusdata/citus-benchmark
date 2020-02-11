# hammerdb

This repository contains utility scripts/files that are used to run hammerdb benchmarks.

Hammerdb is an open source standard benchmarking tool. https://github.com/TPC-Council/HammerDB

TPC-C benchmark contains transaction queries.
TPC-H benchmark contains analytical queries.
CH-benCHmark is a mixed workload, it sends analytical queries along with transactional queries. https://research.tableau.com/sites/default/files/a8-cole.pdf

`build-and-run.sh` is the driver script. Example usage:

```bash
./build-and-run.sh <coordinator_ip> <is_tpcc> <is_ch> <username>
```

* if `is_tpcc` is `true`, then the transaction queries will be run.
* if `is_ch` is `true`, then the analytical queries will be run.

So if you want to run both tpcc and analytical queries concurrently, you should set both of them to true.
**You can set your psql connection string in this file**.

`build.tcl` is used to build hammerdb tables and `run.tcl` is used to run the test.
You can change hammerdb configurations from those files.

*pg_count_ware/pg_num_vu* should be at least 4. https://www.hammerdb.com/blog/uncategorized/how-many-warehouses-for-the-hammerdb-tpc-c-test/

In order to make the build step faster, we have forked the hammerdb and add `distribute tables` at the beginning of the build.
You should replace `pgoltp.tcl` with https://github.com/SaitTalhaNisanci/HammerDB/blob/citus/src/postgresql/pgoltp.tcl

Checklist for running benchmark:

* Make sure that node count is a divisor of shard count, otherwise some nodes will have more shards and the load will not be distribuded evenly.
* Make sure that max_connections is high enough based on #vuuser. max_connections should be at least 150 more than #vuuser.
* Make sure that you do a checkpoint before starting the test, the `build-and-run.sh` already does this. Otherwise the timing of checkpoint can affect the results for short tests.
