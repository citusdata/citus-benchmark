import yaml
import sys

Configs = {

        'cluster': {
            'port': sys.argv[1],
            'resource' : sys.argv[2],
            'host': sys.argv[3],
            'pgpassword': sys.argv[4],
            'user': 'citus',
            'database': 'citus',
            'table': 'usertable',
            'workers': sys.argv[5],
            'prefix': sys.argv[6]
        },

        'monitor': {
            'user': 'monitor',
            'pgpassword': sys.argv[7]
        },

        'ycsb': {
            'records': sys.argv[8],
            'operations': sys.argv[9],
            'shard_count': sys.argv[10],
            'thread_counts': sys.argv[11],
            'iterations': sys.argv[12]
            'workloads': 'workloada,workloadb,workloadc,workloadd,workloade,workloadf'
        },

        'hardware': {
            'coord_hw': sys.argv[13],
            'worker_hw': sys.argv[14],
            'coord_vcpu': sys.argv[15],
            'worker_vcpu': sys.argv[16],
            'coord_storage': sys.argv[17],
            'worker_storage': sys.argv[18]
        }

}

yaml_file = "config.yml"

with open(yaml_file, 'w') as f:
    data = yaml.dump(Configs, f)
    print(f"Build '{yaml_file}' succesfully completed")
