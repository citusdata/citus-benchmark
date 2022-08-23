from concurrent.futures import process
import os
import subprocess
import sys
import pandas as pd

path = sys.argv[1]
# fn = sys.argv[1]

def eprint(*args, **kwargs):

    """
    eprint prints to stderr
    """

    print(*args, file=sys.stderr, **kwargs)


def run(command, *args, shell=True, **kwargs):

    """
    run runs the given command and prints it to stderr
    """

    eprint(f"+ {command} ")
    result = subprocess.run(command, *args, check=True, shell=shell, **kwargs)

    return


def reduce_output(filename):

    """ only gathers required output from gathered iostat files """

    outputname = filename.split('.')[0] + "-reduced"

    run(['./reduce.sh', filename, outputname], shell = False)


def process_values_from_iostat(filename):

    """
    processes the results from iostat
    returns a pandas Dataframe
    """

    filename = filename.split('.')[0] + "-reduced.out"

    user = []
    nice = []
    system = []
    iowait = []
    steal = []
    idle = []
    cpu = []
    timestep = []

    with open(filename , "r") as file:


        lines = file.read().split(' ')

        counter = 0
        ts = 0

        try:

            for value in lines:


                    counter += 1

                    if counter == 1:
                        user.append(float(value))
                        continue

                    if counter == 2:
                        nice.append(float(value))
                        continue

                    if counter == 3:
                        system.append(float(value))
                        continue

                    if counter == 4:
                        iowait.append(float(value))
                        continue

                    if counter == 5:
                        steal.append(float(value))
                        continue

                    idle.append(float(value))
                    cpu.append(100-float(value))
                    timestep.append(ts)

                    ts += 1
                    counter = 0

        except Exception as e:

            print(f"Exception occured: {e}")
            return pd.DataFrame()

    # create pandas pd
    df = pd.DataFrame(list(zip(timestep, user, nice, system, iowait, steal, idle, cpu)),
               columns =['timestep', 'user', 'nice', 'system', 'iowait', 'steal', 'idle', 'cpu'])\

    print(df)

    return df


def batch_process_iostat_output(path, output_csv = True, suffix = '.out'):

    """ batch processes all files ending with suffix in 1 folder """

    for file in [filename for filename in os.listdir(path) if filename.endswith(suffix)]:

        reduce_output(file)
        result = process_values_from_iostat(file)

        if result.empty:
            continue

        if output_csv:
            output_suffix = ".csv"

        output_name = file.split('.')[0] + output_suffix

        # convert pandas dataframe to csv-format
        result.to_csv(output_name)


def process_iostat_output(filename):

    """ processes 1 file """

    reduce_output(filename)
    process_values_from_iostat(filename)

    print("Processing Succeeded")


if __name__=="__main__":

    # batch processes a folder containing iostat output
    batch_process_iostat_output(path)









