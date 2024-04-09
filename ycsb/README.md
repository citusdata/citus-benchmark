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

The YCSB scripts will automatically take care of the provisioning of the Citus clusters and makes sure the the specified workloads are executed. The workloads consist of a specified amount of records behind the `--records` flag and the amount of operations specified after the `--operations` flag. A `.csv` with some interesting results of the benchmark is automatically generated afterward each benchmark. This csv file is generated on the driver VM and transferred to your local machine when the benchmark run is finished.

For details on the flags run:

```
python3 ycsb.py --help
```

Example usage:

```
python3 ycsb.py --resource=yourname --records=10000 --operations=10000 --threads=100,200,300 --iterations=2 --workers=2 --workload="run_all_workloads" start_benchmark
```

After the above command is run, it takes some minutes to provision and configure the Citus cluster and driver VM. If the driver VM is configured, you can connect with your driver VM:

```
cd ../azure
./connect.sh yourname
```

For manually transferring the generated output from the Driver VM to your local machine:

```
cd ../azure
./get-file.sh
```

**Note:** If `autodelete` is set to false (default), make sure to manually delete your resource group after the benchmark runs:

```
cd ../azure
./cleanup.sh yourname
```

### Parameters explained

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


