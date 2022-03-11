# Azure benchmarks

This directory contains useful helper scripts and ARM templates to run
HammerDB and CH-benCHmark against Azure infrastructure.

## Prerequisites

1. [Install the azure
   cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
2. Login to Azure with the CLI:
```bash
az login
```
3. Set a default Azure subscription and location:
```bash
az account set --subscription <subscription-id>
az config set defaults.location=eastus # feel free to choose another one
```
4. Install the Bicep CLI:
```bash
az bicep install
```
5. Make sure that the file `~/.ssh/id_rsa.pub` contains your SSH public key.

## Running benchmarks against Azure Database for PostgreSQL Hyperscale (Citus)

To run a benchmark against Citus on the managed service, use the following
command. The first argument is the name of the resource group that you want to
use.
```bash
./run-benchmark.sh "$USER-hammerdb-hyperscale" hyperscale
```

One of the last lines output of the benchmark will contain line of output in
CSV format.
```bash
jelte-hammerdb-hyperscale,18.283,46385
```

This line of CSV contains three columns, which contain the following three
values:
1. The name you gave to the benchmark
2. The number of minutes it took to build the dataset for the benchmark
3. The NOPM (new orders per minute) that was achieved during the benchmark

After this CSV line is shown, the resources will be cleaned up automatically.

To look at the benchmark while it's running:
```bash
./connect.sh "$USER-hammerdb-hyperscale"
```

To manually cleanup if the benchmark failed for some reason:
```bash
./cleanup.sh "$USER-hammerdb-hyperscale"
```

## Running benchmarks against Postgres installed on regular VMs

To run a benchmark against a Postgres server on a normal VM with default
settings, use the following command. The first argument is the name of the
resource group that you want to use.
```bash
./run-benchmark.sh "$USER-hammerdb-iaas" iaas-postgres
```

The important bit is the second argument being `iaas-postgres`. All the other
things are the same as described in the section above, e.g. the CSV line output,
`connect.sh` and `cleanup.sh`.

## Running benchmarks against an already existing Citus cluster

To run a benchmark against an already existing Citus cluster you can use the
following command. The first argument is the name of the resource group that you
want to use.
```bash
./run-benchmark.sh "$USER-hammerdb-hyperscale-pre-created" hyperscale-pre-created pgHost=postgres.myhostname.com pgAdminPassword=myPostgresUserPassword
```

The important bit is the second argument being `hyperscale-pre-created`, and the
provided hostname and password of the cluster that you want to use for the
benchmark. All the other things are the same as described in the section above,
e.g. the CSV line output, `connect.sh` and `cleanup.sh`.

## Running with custom settings

You can run the benchmark with non default settings very easily, by passing
parameters to the `./run-benchmark.sh` command:
```bash
./run-benchmark.sh "$USER-hammerdb-hyperscale" hyperscale warehouses=2000 runVirtualUsers=500 workers=16
```

To see all the possible parameters look at the top of the `hyperscale.bicep` or
`iaas-postgres.bicep` file (depending on the test that you are running).

## Running benchmarks in bulk

Often you want to compare multiple runs, and probably run the same benchmark a
few times to get some statistically relevant results. This can be done easily by
running the `bulk-run.sh` script. It takes a file describing the configurations
you want to run as input:

```bash
./bulk-run.sh runs.sample | tee -a results.csv
```

If you want to run different configurations of the benchmark, simply create a
custom runs file (or edit runs.sample). The "runs" file contains multiple lines,
each lines contains comma separated values. The first value in the line
determines how often each benchmark should be run (useful for getting
statistically relevant results). All other values are simply the arguments that
need to be passed to `run-benchmark.sh`. Notably the line does not contain the
resource group name. The reason is that this name is generated randomly for each
run, to avoid conflicts.
