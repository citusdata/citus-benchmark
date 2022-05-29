# Collects postgresql logs from /dat/14/data/pg_log/ produced by user ‘monitor’ on every worker/coordinator
# Stores all collected files in RDS and S3 so that they persist
# If succeeded, delete locally generated files and folders (optional)

import os
from helper import *
import yaml
from logs import Logging
import sys

homedir = os.getcwd()
bucket = sys.argv[1]

# read config file
with open('config.yml', 'r') as f:
    try:
        config = yaml.safe_load(f)
        ycsb = config['ycsb']
        cluster = config['cluster']
    except yaml.YAMLError as exc:
        print(exc)

# Create a logging instance
logs = Logging(resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'], shard_count = ycsb['shard_count'])

# Collect cpu usage from worker nodes
logs.collect_iostat()

# # Get csv's from driver # # Get raw ycsb-data from driver for every resource group and push to blob
logs.get_csv_and_ycbs_logs()

# # Get raw postgresql data from worker nodes
logs.get_postgresql()

# # Runs script that pushes gathered data to Blob storage and a PostgreSQL DB
# # Push to postgresql
os.chdir(homedir + "/storage")
path = homedir + f"/logs/scripts/{cluster['resource']}"

run(["python3", 'push_to_db.py', path, "PARALLEL"], shell = False)

# # Push to blob
run(["./push-to-blob.sh", f"{path}/YCSB/raw/", bucket, f"{cluster['resource']}/raw/"], shell = False)
run(["./push-to-blob.sh", f"{path}/pglogs/", bucket, f"{cluster['resource']}/pglogs"], shell = False)
run(["./push-to-blob.sh", f"{path}/general/", bucket, f"{cluster['resource']}/general"], shell = False)

# DELETE RESOURCE GROUP FOLDER
run(["rm", "-r", path], shell = False)
print("FOLDER REMOVED")


print("DONE WITH BENCHMARKS")



