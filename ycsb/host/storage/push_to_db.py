import os
import psycopg2 as pg
import csv
import yaml
import sys

def list_csv_files(path, suffix = ".csv"):

    """ List all csv files from a specific path and returns list """

    return [filename for filename in os.listdir(path) if filename.endswith(suffix)]


def batch_insert(path, files, query):

    """ inserts multiple csv files into postgresql database """
    print(files)
    # Create cursor
    cursor = conn.cursor()

    for iteration in files:
        # Parse CSV file
        with open(path + "/" + iteration, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for record in reader:
                cursor.execute(query, record)
                conn.commit()

    if (conn):
        cursor.close()
        conn.close()
        print("Records succesfully inserted\nConnection closed.")


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

# get path
resource = os.getenv("RESOURCE")
path = sys.argv[1] + "/YCSB/results"

# insert
sql_insert = """INSERT INTO YCSB(rg, workers, iteration, workloadtype, workloadname, threads, records, operations, throughput, runtime)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

batch_insert(path, list_csv_files(path), sql_insert)


