import os
import subprocess
import sys

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

    return result

def create_output_directories(self):

    """ create output directories if not there yet """

    run(['mkdir', '-p', 'output'], shell = False)
    run(['mkdir', '-p', 'output' + "/YCSB/" + self.RESOURCE + "/results"], shell = False)
    run(['mkdir', '-p', 'output' + "/pglogging"], shell = False)
    run(['mkdir', '-p', 'output' + "/general"], shell = False)