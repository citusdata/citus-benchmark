import psycopg2 as pg
import yaml
import sys

def get_results(cursor, query, maximum = 0):

    """ stores results of query in a list """

    # Execute query
    cursor.execute(query)

    if maximum:
        results =  cursor.fetchmany(maximum)
    else:
        results = cursor.fetchall()

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

workers = sys.argv[1]
vcpu_per_worker = sys.argv[2]

configuration = [workers, vcpu_per_worker]
sql_query = f"select threads, count(threads), avg(throughput), stddev(throughput) from ycsb where workloadtype='run' and rg in (select resource_group as rg from hardware where workers={configuration[0]} and worker_vcp_num={configuration[1]}) group by threads order by avg desc;"

query_list = [sql_query]

cursor = conn.cursor()

for q in query_list:
    print(q)

    print(get_results(cursor, q))

if (conn):
    cursor.close()
    conn.close()
    print("Records succesfully queried\nConnection closed.")



