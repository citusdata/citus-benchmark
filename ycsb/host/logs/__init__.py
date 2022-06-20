import os
import fire
from helper import run, eprint
import datetime

class Logging(object):


    def get_worker_adresses(self):

        """ get adresses from workers in a citus cluster """

        os.chdir(f"{self.HOMEDIR}/logs/scripts")
        return os.popen(f"./worker-adresses.sh {self.HOST} {self.PORT} {self.PASSWORD} {self.USER} {self.DATABASE}").read().split('\n')[0].split(',')


    def get_worker_name(self):

        """ get worker name (e.g. 0, 1 etc) """

        names = []

        for worker in self.get_worker_adresses():
            names.append(worker[1:].split('.')[0])

        return names


    def get_weekday(self):

        """ returns abbreviation of current weekday needed for PostgreSQL log """

        day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat','Sun']

        return day_name[datetime.datetime.today().weekday()]


    def __init__(self, resource, prefix, host, password = "postgres", port = 5432, user = "citus", database = "citus",
    iterations = 1, shard_count = 4, iteration = 0):

        self.HOMEDIR = os.getcwd()
        self.PASSWORD = password
        self.HOST = host
        self.PORT = str(port)
        self.USER = user
        self.DATABASE = database
        self.PREFIX = prefix
        self.RESOURCE = resource
        self.WORKERS = self.get_worker_adresses()
        self.ITERATIONS = iterations
        self.SHARD_COUNT = shard_count
        self.CURRENT_ITERATION = iteration


        # Set environment variables
        os.environ['PGPASSWORD'] = self.PASSWORD
        os.environ['PGHOST'] = self.HOST
        os.environ['PGPORT'] = str(self.PORT)
        os.environ['PGUSER'] = self.USER
        os.environ['PGDATABASE'] = self.DATABASE
        os.environ['PREFIX'] = self.PREFIX
        os.environ['RESOURCE'] = self.RESOURCE
        os.environ['WORKERS'] = str(self.WORKERS)
        os.environ['ITERATIONS'] = str(self.ITERATIONS)
        os.environ['SHARD_COUNT'] = str(self.SHARD_COUNT)


    def prepare_postgresql_table(self):

            """
            Executes bash script that enters psql, truncates usertable if exists and creates
            a new empty usertable
            """

            os.chdir(f"{self.HOMEDIR}/logs/scripts")
            run(["./prepare-table-driver.sh", str(self.SHARD_COUNT), str(self.HOST), str(self.DATABASE), str(self.USER), str(self.PASSWORD)], shell = False)
            os.chdir(f"{self.HOMEDIR}/logs")
            print("Schema and distributed tables prepared")


    def create_output_directories(self):

        """ create output directories if not there yet """

        run(['mkdir', '-p', self.RESOURCE], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/YCSB/results"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/YCSB/raw"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/pglogs"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/general"], shell = False)


    def get_csv_and_ycbs_logs(self, outdir = "results"):

        """ connects with VM and gets generated csv's """

        os.chdir(f'{self.HOMEDIR}/logs/scripts')
        run(["./get-csv-from-driver.sh", self.RESOURCE, f"{self.RESOURCE}/YCSB/results"], shell = False)
        run(["./get-ycsb-logs-from-driver.sh", self.RESOURCE, f"{self.RESOURCE}/YCSB/raw"], shell = False)
        os.chdir(f"{self.HOMEDIR}")


    def print_workers(self):

        """ prints all host of workers """

        for worker in self.get_worker_adresses():
            print(worker)


    def connect_to_worker(self, worker, script):

        """ Connects to a worker via ssh, and runs a script """

        run(["ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}", script], shell = False)


    def run_on_all_workers(self, script):

        """ runs script in all workers from citus cluster """

        for i, worker in enumerate(self.WORKERS):
            self.connect_to_worker(worker, script)


    def set_permissions(self):

        """
        Sets the following permissions for user 'monitor':
        alter user monitor set log_duration = on
        alter user monitor set log_min_messages = 'debug1'
        alter user monitor set log_statement to 'all'
        """

        os.chdir(f'{self.HOMEDIR}/logs/scripts')

        # change permissions on coordinator node
        run(["./alter-user.sh", self.PREFIX, self.HOST, ">", "/dev/null"], shell = False)

        # Also manually change on all workers
        for worker in self.WORKERS:
            run(["./alter-user-on-worker.sh", self.PREFIX, worker, ">", "/dev/null"], shell = False)

        os.chdir(f"{self.HOMEDIR}/logs")


    def workers_and_ids(self):

        """ Print worker id and corresponding worker adresses """

        return list(zip(self.get_worker_name(), self.WORKERS))


    def get_postgresql(self):

        """ collects postgresql logs in /dat/14/data/pg_logs """

        os.chdir(f'{self.HOMEDIR}/logs/scripts')

        for worker_num, worker_host in self.workers_and_ids():
            run(["./get-pglog.sh", self.PREFIX, worker_host, worker_num, str(self.CURRENT_ITERATION)], shell = False)

        os.chdir(f"{self.HOMEDIR}/logs")


    def truncate_pg_log(self):

        """
        truncates pg_log in /dat/14/data/pg_logs
        no run_on_all_workers is used due to sudo
        """

        os.chdir(f'{self.HOMEDIR}/logs/scripts')

        for worker_host in self.WORKERS:
            run(["./truncate-pg_log.sh", self.PREFIX, worker_host, f"postgresql-{self.get_weekday()}.log"], shell = False)

        os.chdir(f"{self.HOMEDIR}/logs")


    def start_iostat(self):

        """ starts the tmux process to automatically measure cpu usage during benchmarks """

        # Runs script on workers (IOSTAT) that collects CPU usage for every second
        self.run_on_all_workers("tmux new -s cpu-usage -d; tmux send-keys -t cpu-usage 'nohup iostat -xmt 1 &' Enter")


    def collect_iostat(self):

        """ Collect iostat files from every worker and stores in resource_group/workername/general """

        for i, worker in enumerate(self.WORKERS):

            run(["scp", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}:nohup.out", f"{self.HOMEDIR}/logs/scripts/{self.RESOURCE}/general/worker-{i}-{self.CURRENT_ITERATION}.out"], shell = False)


    def delete_iostat(self):

        """ Collect iostat files from every worker and stores in resource_group/workername/general """

        self.run_on_all_workers("tmux kill-session -t cpu-usage; rm nohup.out")


    def prepare_monitor_run(self):

        """ prepares for a monitor run """

        self.truncate_pg_log()
        self.start_iostat()


    def stop_monitoring(self):

        """
        Stop Monitoring:
        - collect nohup.out on every worker
        - stop execution of iostat
        - get postgresql logs
        """

        self.collect_iostat()
        self.delete_iostat()
        self.get_postgresql()




if __name__ == '__main__':

  fire.Fire(Logging)
