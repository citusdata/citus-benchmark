import math
import os
import sys
import subprocess

pglog = sys.argv[1]
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

output_internal='internal-1.txt'
output_external='external-1.txt'

os.chdir("scripts")
run(["./internal.sh", pglog, output_internal], shell = False)
run(["./external.sh", pglog, output_external], shell = False)
os.chdir(homedir)


total = 0

for results in [output_internal, output_external]:

    nonumber = 0
    total = 0
    with open(results) as f:

        lines = f.readlines()

        for line in lines:
            try:
                total += float(line)
            except:
                nonumber += 1

    totallines = len(lines) - nonumber
    avg = total/(totallines/3)

    # print(total)
    # print(totallines)
    # print(totallines/3)

    print(f"AVG {results} query is")
    print(avg)
    # l.append(avg)

    tps = 1/avg * 1000
    print(f"TPS for {results} queries is: {tps}")

