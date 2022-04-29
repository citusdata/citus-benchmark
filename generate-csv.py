from concurrent.futures import thread
import os
import subprocess
import fire
import sys
import csv
import random, string

homedir = os.getcwd()

def eprint(*args, **kwargs):

    """
    eprint prints to stderr
    """

    print(*args, file=sys.stderr, **kwargs)


def run(command, *args, shell=True, **kwargs):

    """
    run runs the given command and prints it to stderr.
    """

    eprint(f"+ {command}")
    result = subprocess.run(command, *args, check=True, shell=shell, **kwargs)
    return result


def change_directory(name="."):

    """
    changes directory
    """

    global homedir

    os.chdir(homedir + "/" + name)


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


def return_csv(outfolder = "output", csvname="output.csv"):

    """
    generates a csv with format:
    workloadtype, workloadname, threads, records, operations, throughput, runtime
    """


    os.chdir(outfolder)

    results = [["workloadtype", "workloadname", "threads", "records", "operations", "throughput", "runtime (s)"]]

    for output_file in os.listdir('.'):

        # Split name of file; determine threadcount and workload type (load or run)
        values = output_file.split('_')

        if values[0] == "load":

            # workloadtype, workloadname, threads, records, operations, throughput, runtime
            row = [values[0], values[1], values[2], values[-1].split('.')[0], 0, get_throughput(output_file), get_runtime(output_file)]
            results.append(row)
            continue

        row = [values[0], values[1], values[2], values[3], values[-1].split('.')[0], get_throughput(output_file), get_runtime(output_file)]
        results.append(row)

    f = open(homedir + "/" + csvname, 'w')
    writer = csv.writer(f)

    for row in results:

        writer.writerow(row)

    # close the file
    f.close()


if __name__ == '__main__':
    
  fire.Fire(return_csv)