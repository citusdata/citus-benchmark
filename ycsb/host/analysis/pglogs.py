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

    # eprint(f"+ {command}")
    # result = subprocess.run(command, *args, check=True, shell=shell, **kwargs)
    return subprocess.run(command, *args, check=True, shell=shell, **kwargs)


def skip_k_first_queries(lines, k, shard = False):

    """ returns the resulting lines from a file by skipping the k first queries """

    # execution time of 1 query is a summation of 3 rows (parse, bind, execute)
    # therefore multiply k with 3

    if not shard:
        k = k * 3

    index = 0

    for i, line in enumerate(lines):

        if k:

            try:
                float(line)
                k -= 1
                continue

            except:
                continue

        index = i
        break

    return lines[index:]


def read_file(filename, k = 0, shard = False):

    """ reads a file and returns file contents and length of file """


    with open(filename) as f:

        lines = f.readlines()

        if k > 0:
            lines = skip_k_first_queries(lines, k, shard)

        return lines, len(lines)


def sum_and_count_anchor_shard(filename, k = 0):

    """ sums all anchor (i.e. query on child worker + latency) execution times """

    count, _sum = 0, 0

    for line in read_file(filename, k)[0]:

        try:
            _sum += float(line)
            count += 1

        except Exception as e:

            print(f'Exception: {e}')
            continue

    if not _sum:
        return 0, 0

    return _sum, count


def calculate_anchor_shard_average(filename):

    """ calculates avg of anchor shard execution """

    _sum, count = sum_and_count_anchor_shard(filename)

    if not count:
        return 0

    return _sum / count


def sum_and_count_execution_time(filename, k):

    """ sums all execution times """

    nonumber = 0
    total = 0
    lines, length = read_file(filename, k)

    for line in lines:

        try:
            total += float(line)

        except:
            nonumber += 1

    count = length - nonumber

    try:
        print(f"{filename}: total cumulative {total}, total lines: {count}")

    except Exception as e:

        print(f"Exception: {e}")
        return 0, 0

    return total, count


def get_valid_numbers(lines):

    """ only extract valid float numbers from pglogs """

    result = []

    for line in lines:

        try:
            result.append(float(line))

        except:
            continue

    return result


def sum_3_values(result):

    """ sums parse, bind and execute per query and returns a list """

    compute = []

    # sum every 3 results (parse, bind, execute)
    for i in range(0, len(result), 3):

        try:
            compute.append(sum(result[i:i+3]))

        except Exception as e:

            compute.append(sum(result[i:]))

    return compute


def collect_execution_times(filename, k = 30, shard = False):

    """ returns list with all execution times """

    # read file
    lines, length = read_file(filename, k, shard)

    # only extract valid entries from file
    result = get_valid_numbers(lines)

    # if anchor shard, no summing is necessary
    # thus directly return result
    if shard:
        return [val / 1000 for val in result]

    # sum parse, bind, execute per query and return list
    return sum_3_values(result)


def calculate_avg_executiontime(filename):

    """ calculates avg execution time """

    total, totallines = sum_and_count_execution_time(filename)

    if not totallines:
        return 0

    try:
        print(f"{filename}: total cumulative {total}, total lines: {totallines}")
        avg = total/(totallines/3)

    except Exception as e:

        print(f"Exception: {e}")
        return 0

    return avg


def print_output(anchor_mean, anchor_stdev, external_mean, external_stdev, internal_mean, internal_stdev, latency_mean, parent_mean):

    """ prints output of batch processing pglogs """

    print("")
    print("TOTAL AVERAGES (mean, stdev)")
    print("----------------------------------------------------------------------------------------------")
    print(f"Anchor Shard: {anchor_mean}, {anchor_stdev}")
    print(f"Parent (coordinator/external): {external_mean}, {external_stdev}")
    print(f"Child (internal): {internal_mean}, {internal_stdev}")
    print(f"Anchor - Child (latency): {latency_mean}")
    print(f"Compute on coordinator (parent) node: {parent_mean}")



def remove_txt(cleanup):

    """
    removes ALL .txt files in current folder
    !!! MAY unwantedly remove relevant txt files !!!
    """

    if cleanup:

        run(['./remove.sh', '.txt', os.getcwd()], shell = False)


def calculate_mean_per_worker(node, internal, external, anchor, output_internal, output_external, output_shard):

    """ calculates mean values for internal, external and anchor per worker """

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

    return internal, external, anchor


def batch_process_pglogs(path, suffix = '.log', cleanup = True, mean = False):

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

        if mean:
            internal, external, anchor = calculate_mean_per_worker(node, internal, external, anchor, output_internal, output_external, output_shard)

        else:
            internal.extend(collect_execution_times(output_internal, k = 100))
            external.extend(collect_execution_times(output_external, k = 100))
            anchor.extend(collect_execution_times(output_shard, k = 100, shard = True))

    anchor_mean, anchor_stdev = stats.mean(anchor), stats.stdev(anchor)
    external_mean, external_stdev = stats.mean(external), stats.stdev(external)
    internal_mean, internal_stdev = stats.mean(internal), stats.stdev(internal)
    latency_mean = anchor_mean - internal_mean
    parent_mean = external_mean - anchor_mean

    print_output(anchor_mean, anchor_stdev, external_mean, external_stdev, internal_mean, internal_stdev, latency_mean, parent_mean)
    remove_txt(cleanup)

    print()
    print("TOTAL LENGTHS")
    print("----------------------------------------------------------------------------------------------")
    print(f"Total lengths: parent: {len(external)}, child: {len(internal)}, shard: {len(anchor)}")


if __name__=="__main__":

    path = sys.argv[1]
    batch_process_pglogs(path, suffix = '.log')
