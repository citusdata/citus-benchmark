import psycopg2 as pg
import yaml
import sys

homedir = sys.argv[1]

# Read configfile for database
with open('RDS.yml') as file:
    try:
        RDS = yaml.safe_load(file)[0]['RDS']
    except yaml.YAMLError as exc:
        print(exc)

# Read general configfile
with open(homedir + "/config.yml") as f:
    try:
        config = yaml.safe_load(f)
        cluster = config['cluster']
        hardware = config['hardware']

    except yaml.YAMLError as exc:
        print(exc)

# connect to RDS postgresql database
try:
    conn = pg.connect(f"dbname='{RDS['database']}' user='{RDS['user']}' host='{RDS['endpoint']}' password='{RDS['password']}'")
except:
    print("Unable to connect to the database")
    sys.exit(1)

# CONFIGFILE SCHEMA
# hardware:
#   coord_hw
#   coord_storage
#   coord_vcpu
#   worker_hw
#   worker_storage
#   worker_vcpu

def insert_metadata(query):

    """ inserts metadata about hardware and resource group into postgresql db """

    try:
        # Create cursor
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()

        if (conn):
            cursor.close()
            conn.close()
            print("SUCCES: Metadata sucessfully stored")
    except:
        print("FATAL: Failed to store metadata")
        pass

sql_insert = f"""INSERT INTO hardware(resource_group, driver_hw, coord_hw, worker_hw, coord_vcpu_num, worker_vcp_num, coord_storage, worker_storage, workers)
                VALUES('{cluster['resource']}', 'Standard_D64s_v3', '{hardware['coord_hw']}',  '{hardware['worker_hw']}',  {int(hardware['coord_vcpu'])},
                {int(hardware['worker_vcpu'])}, {int(hardware['coord_storage'])},  {int(hardware['worker_storage'])}, {int(cluster['workers'])})"""

insert_metadata(sql_insert)


