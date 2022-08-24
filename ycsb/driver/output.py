import os
import fire
import csv
import random, string

homedir = os.getcwd()


def search_file(filename, substring):

    """ Searches for a substring in the output file and returns the value corresponding to the substring """

    with open(filename, "r") as file:

        for line in file:

            if substring not in line:
                continue

            return float(line.split(' ')[-1].split('\n')[0])

    return 0


def get_records(filename):

    """ gets amount of records inserted in database from YCSB output logs """

    return search_file(filename, '[INSERT], Operations')


def get_operations(filename):

    """ gets amount of read operations performed from YCSB output logs """

    return search_file(filename, '[READ], Operations')


def get_throughput(filename):

     """ gets throughput from YCSB output logs """

     return search_file(filename, '[OVERALL], Throughput')


def get_runtime(filename):

     """ gets total runtime from YCSB output logs """

     return search_file(filename, '[OVERALL], RunTime(ms)') / 1000


def random_string(length):

    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def return_csv(csvname="output.csv"):

    """
    generates a csv with format:
    id, workers, iteration, workloadtype, workloadname, threads, records, operations, throughput, runtime
    """

    results = [["id", "workers", "iteration", "workloadtype", "workloadname", "threads", "records", "operations", "throughput", "runtime (s)"]]

    for output_file in os.listdir('.'):

        # Ignore non-log files
        if not output_file.endswith(".log"):
            continue

        # Split name of file; determine threadcount and workload type (load or run)
        values = output_file.split('_')

        if values[0] == "load":

            # resource_group, workers, iteration, workloadtype, workloadname, threads, records, operations, throughput, runtime
            row = [values[-1].split('.')[0], values[-2], values[-3], values[0], values[1], values[2], values[3], 0, get_throughput(output_file), get_runtime(output_file)]
            results.append(row)
            continue

        # resource_group, workers, iteration, workloadtype, workloadname, threads, records, operations, throughput, runtime
        row = [values[-1].split('.')[0], values[-2], values[-3], values[0], values[1], values[2], values[3], values[4], get_throughput(output_file), get_runtime(output_file)]
        results.append(row)

    # write results to csv file
    f = open(homedir + "/" + csvname, 'w')
    writer = csv.writer(f)

    for row in results:
        writer.writerow(row)

    f.close()

    def concat_csv(self):
        return

if __name__ == '__main__':

  fire.Fire(return_csv)