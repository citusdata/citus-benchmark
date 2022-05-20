# prepare FILE:
# Builds config file with inputs from internal repo
# Reads config file (e.g. for DB credentials)
# Generates a file with metadata about citus cluster (driver_hardware, coord_hardware, coord_vcpu_num, coord_storage, worker_hardware, worker_vcpu_num, worker_storage, workers) and stores metadata.csv in output/{resource_group}
# Alters user permissions for second user ‘monitor’ (used for logging)


import os
from helper import *
import yaml
from logs import Logging

homedir = os.getcwd()

# read config file
with open('config.yml', 'r') as f:
    try:
        config = yaml.safe_load(f)
        ycsb = config['ycsb']
        cluster = config['cluster']
    except yaml.YAMLError as exc:
        print(exc)

# Store metadata about the resource group (hardware used etc)
# try:
#     run(['python3', 'metadata.py'], shell = False)
# except:
#     pass
#     print("Metadata already stored")

# Create a logging instance
logs = Logging(resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'], shard_count = ycsb['shard_count'])

# create output directories w/ resource name
logs.create_output_directories()

# worker adresses
logs.print_workers()

# create schema for YCSB benchmarks (usertable)
logs.prepare_postgresql_table()

# # Alter user permissions for user monitor
logs.set_permissions()

# Subsequently second command is executed on internal repo



