import os
import psycopg2 as pg
import csv
import secrets
import yaml
import sys

length = 10
generated_key = secrets.token_urlsafe(length)

# Read configfile
with open('RDS.yml') as file:
    try:
        RDS = yaml.safe_load(file)[0]['RDS']
    except yaml.YAMLError as exc:
        print(exc)

# connect to RDS postgresql database
try:
    conn = pg.connect(f"dbname='{RDS['database']}' user='{RDS['user']}' host='{RDS['endpoint']}' password='{RDS['password']}'")
    print("Connecting succeeded")
except:
    print("Unable to connect to the database")
    sys.exit(1)

# iterate through all files
file = r'example.csv'

sql_insert = """INSERT INTO ycsb_results(id, workers, iteration, workloadtype, workloadname, threads, records, operations, throughput, runtime)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

# Create cursor
cursor = conn.cursor()

# Parse CSV file
with open(file, 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for record in reader:
        generated_key = secrets.token_urlsafe(length)
        cursor.execute(sql_insert, record)
        conn.commit()

if (conn):
    cursor.close()
    conn.close()
    print("Records succesfully inserted\nConnection closed.")

