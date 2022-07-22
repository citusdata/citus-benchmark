# Run YCSB benchmarks on Citus in Azure Managed Service

### Requirements:

For linux/ubuntu

```
sudo apt -y install vim bash-completion wget
sudo apt update -y
sudo apt-get install python3-pip -y
pip3 install fire
pip3 install pandas
pip3 install matplotlib
```

#### Run YCSB against Citus on Azure

Example usage:

```
python3 ycsb.py --resource=yourname --records=10000 --operations=10000 --threads=100,200,300 --iterations=2 --workers=2 --workloads="run_all_workloads" start_benchmark
```

##### Parameters explained

> `resource` is the name of the resource group that will be created for running the benchmarks
> `records` the amount of records to be inserted by YCSB
> `operations` is the amount of operations performed by YCSB
> `threads` is a list (seperated by a comma) of the different threadcouns used during the YCSB benchmarks
> `iterations` is the amount of iterations for the benchmarks
> `workers` represents the amount of workers in the Citus cluster
> `autodelete` default value is false. If set to true, cluster will be automatically deleted when benchmarks are finished.
> `workloads` are the YCSB workloads one can test. We have the following options:
> > - workloada
> > - workloadb
> > - workloadc
> > - workloadd
> > - workloade
> > - workloadf
> > - run_all_workloads
