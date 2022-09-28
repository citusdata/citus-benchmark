# Run YCSB benchmarks on Citus in Azure Managed Service

### Requirements:

For the benchmarks to run, both `python2`and `python3` are required. In addition, we make use of the Python package `python fire`.

If you are using Ubuntu / Debian on the driver node, you can run `./install.sh`:

```
sudo apt -y install vim bash-completion wget
sudo apt update -y
sudo apt-get install python3-pip -y
pip3 install fire
```

### Run YCSB against Citus on Azure

The scripts load the amount of records specified behind the records flag and runs any of the YCSB standard workloads by performing the specified amount of operations. A CSV with some statistics from the benchmark is automatically generated afterwards on the driver VM and transferred to your local machine.

For details on the flags run:

```
python3 ycsb.py --help
```

Example usage:

```
python3 ycsb.py --resource=yourname --records=10000 --operations=10000 --threads=100,200,300 --iterations=2 --workers=2 --workload="run_all_workloads" start_benchmark
```

##### Parameters explained

> `resource` is the name of the resource group that will be created for running the benchmarks <br>
> `records` the amount of records to be inserted by YCSB <br>
> `operations` is the amount of operations performed by YCSB <br>
> `threads` is a list (seperated by a comma) of the different threadcouns used during the YCSB benchmarks <br>
> `shard_count` default is 2 * workers. You can set your own shard count with this parameter. <br>
> `iterations` is the amount of iterations for the benchmarks <br>
> `workers` represents the amount of workers in the Citus cluster <br>
> `autodelete` default value is false. If set to true, cluster will be automatically deleted when benchmarks are finished. <br>
> `workloads` are the YCSB workloads one can test. We have the following options: <br>
>
> > - workloada
> > - workloadb
> > - workloadc
> > - workloadd
> > - workloade
> > - workloadf
> > - run_all_workloads
>
