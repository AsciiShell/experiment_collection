import os
import subprocess

import sys


def call(*args, shell=False):
    proc = subprocess.run(args, shell=shell, check=False)
    if proc.returncode:
        print('Error: ', *args)


setup_dir = os.path.dirname(os.path.abspath(__file__))
setup_client = os.path.join(setup_dir, 'setup_client.py')
setup_server = os.path.join(setup_dir, 'setup_server.py')

if os.path.exists(setup_client):
    call_args = sys.argv.copy()
    call_args[0] = setup_client
    call('python3', *call_args)
if os.path.exists(setup_server):
    call_args = sys.argv.copy()
    call_args[0] = setup_server
    call('python3', *call_args)
