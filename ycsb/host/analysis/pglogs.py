import statistics as stats
import os
import sys
import subprocess

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


def read_file(filename):

    """ reads a file and returns file contents and length of file """

    with open(filename) as f:

        lines = f.readlines()
        length = len(lines)

        return lines, length


def calculate_anchor_shard_average(filename):

    """ calculates avg of anchor shard execution """

    count, _sum = 0, 0
    # print(filename)

    for line in read_file(filename)[0]:

        try:
            _sum += float(line)
            count += 1

        except Exception as e:

            print(f'Exception: {e}')
            continue
    # print()
    # print(f"anchor shard sum: {_sum} and count {count}")
    # print()

    if not _sum:
        return 0

    return _sum / count


def calculate_avg_executiontime(filename):

    """ calculates avg execution time """

    nonumber = 0
    total = 0
    lines, length = read_file(filename)

    for line in lines:

        try:
            total += float(line)

        except:
            nonumber += 1

    totallines = length - nonumber

    try:
        print(f"{filename}: total cumulative {total}, total lines: {totallines}")
        avg = total/(totallines/3)

    except Exception as e:

        print(f"Exception: {e}")
        return 0

    tps = 1/avg * 1000
    # print(f"Estimated tps is {tps}")

    return avg

def print_output(anchor_mean, anchor_stdev, external_mean, external_stdev, internal_mean, internal_stdev, latency_mean):

    """ prints output of batch processing pglogs """

    print("")
    print("TOTAL AVERAGES (mean, stdev)")
    print("----------------------------------------------------------------------------------------------")
    print(f"Anchor Shard: {anchor_mean}, {anchor_stdev}")
    print(f"Parent (coordinator/external): {external_mean}, {external_stdev}")
    print(f"Child (internal): {internal_mean}, {internal_stdev}")
    print(f"Anchor - Child (latency): {latency_mean}")



def remove_txt(cleanup):

    """
    removes ALL .txt files in current folder
    !!! MAY unwantedly remove relevant txt files !!!
    """

    if cleanup:

        run(['./remove.sh'], shell = False)


def batch_process_pglogs(path, suffix = '.log', cleanup = True):

    """ batch processes all files ending with suffix in one folder """

    anchor = []
    internal = []
    external = []

    for file in [filename for filename in os.listdir(path) if filename.endswith(suffix)]:

        filepath = path + "/" + file
        node = file.split('-')[1]

        output_internal = f'{node}-internal.txt'
        output_external = f'{node}-external.txt'
        output_shard = f'{node}-shard.txt'

        run(["./internal.sh", filepath, output_internal], shell = False)
        run(["./external.sh", filepath, output_external], shell = False)
        run(["./shard.sh", filepath, output_shard], shell = False)

        anchor_ms = calculate_anchor_shard_average(output_shard) / 1000
        print(f"anchor shard avg is {anchor_ms} milliseconds")

        external_ms = calculate_avg_executiontime(output_external)

        if not external_ms:
            print(f'No parent/coordinator queries on worker {node}')

        else:
            print(f"Avg parent query execution time is {external_ms}")
            external.append(external_ms)
            anchor.append(anchor_ms)

        internal_ms = calculate_avg_executiontime(output_internal)
        print(f"Avg child query execution time is {external_ms}")
        internal.append(internal_ms)

    anchor_mean, anchor_stdev = stats.mean(anchor), stats.stdev(anchor)
    external_mean, external_stdev = stats.mean(external), stats.stdev(external)
    internal_mean, internal_stdev = stats.mean(internal), stats.stdev(internal)
    latency_mean = anchor_mean - internal_mean

    print_output(anchor_mean, anchor_stdev, external_mean, external_stdev, internal_mean, internal_stdev, latency_mean)
    remove_txt(cleanup)

if __name__=="__main__":

    path = sys.argv[1]
    batch_process_pglogs(path, suffix = '.log')
