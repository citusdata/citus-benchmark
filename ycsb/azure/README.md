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
python3 run.py --resource=yourname --records=1000 --operations=1000 --threads=50,100 --iterations=2 --workers=2 start_benchmark
```

#### Batch Run

##### Change hardware configurations:

Modify `hardware.config` file
