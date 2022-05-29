import os
from helper import *
import yaml
from logs import Logging
import time
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

time.sleep(120)
os.chdir(homedir + '/logs/scripts/')

# If 'run.finished' then get all generated csv's from driver vm and store in db's
run(["./try-sign.sh", cluster['resource'], 'run.finished', '60'], shell = False)

os.chdir(homedir)

# Data collection
run(['python3', 'collect_data_individual.py', bucket], shell = False)



