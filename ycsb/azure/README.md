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
