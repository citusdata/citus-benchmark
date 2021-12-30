# Azure benchmarks

This directory contains useful helper scripts and ARM templates to run
HammerDB and CH-benCHmark against Azure infrastructure.

## Prerequisites

Set a default Azure subscription and location:
```
az account set --subscription <subscription-id>
az config set defaults.location=eastus # feel free to choose another one
```

## Running benchmarks against Azure Database for PostgreSQL Hyperscale (Citus)

To run a benchmark against Citus on the managed service, use the following
command. The first argument is the name of the resource group that you want to
use.
```
./run-benchmark.sh "$USER-hammerdb-hyperscale" hyperscale
```

To look at the benchmark:
```
./connect.sh "$USER-hammerdb-hyperscale"
```

To clean up:
```
./cleanup.sh "$USER-hammerdb-hyperscale"
```

## Running benchmarks against Postgres installed on regular VMs

To run a benchmark against a Postgres server on a normal VM with default
settings, use the following command. The first argument is the name of the
resource group that you want to use.
```
./run-benchmark.sh "$USER-hammerdb-iaas" iaas-postgres
```

To look at the benchmark:
```
./connect.sh "$USER-hammerdb-iaas"
```

To clean up:
```
./cleanup.sh "$USER-hammerdb-iaas"
```


## Running with custom settings

You can run the benchmark with non default settings very easily, by passing
parameters to the `./run-benchmark.sh` command:
```bash
./run-benchmark.sh "$USER-hammerdb-hyperscale" hyperscale warehouses=2000 runVirtualUsers=500 workers=16
```

To see all the possible parameters look at the top of the `hyperscale.bicep` or
`iaas-postgres.bicep` file (depending on the test that you are running).
