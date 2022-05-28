import psycopg2 as pg
import yaml
import sys

def get_results(query, maximum = 0):

    """ stores results of query in a list """

    # Create cursor
    cursor = conn.cursor()

    # Execute query
    cursor.execute(query)

    if maximum:
        results =  cursor.fetchmany(maximum)
    else:
        results = cursor.fetchall()

    if (conn):
        cursor.close()
        conn.close()
        print("Records succesfully queried\nConnection closed.")

    return results

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

# insert
sql_query = "SELECT AVG(throughput) FROM ycsb WHERE workers=5 and workloadtype='run';"
sql_query2 = "SELECT AVG(throughput) FROM ycsb;"
sql_query3 = "SELECT AVG(throughput) FROM ycsb;"

query_list = [sql_query, sql_query2]

res = get_results(sql_query)

for i in res:
    for val in i:
        print(str(val).split(" ")[0])


