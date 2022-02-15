#!/usr/bin/env python3
import subprocess
import sys

"""
eprint prints to stderr
"""
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

"""
run runs the given command and prints it to stderr.
"""
def run(command, *args, shell=True, **kwargs):
    eprint(f"+ {command}")
    result = subprocess.run(command, *args, check=True, shell=shell, **kwargs)
    return result

# easy execution of simple commands
run("echo 1")

# safe execution of a command with user input
some_user_input = 'hacked; cat /etc/passwd'
run(["echo", some_user_input], shell=False)
