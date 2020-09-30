import os
import platform
import re
import subprocess
import sys


def call(*args, shell=False):
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, check=False)
    if proc.returncode:
        print('Error: ', *args)
        print('STDOUT:', proc.stdout, file=sys.stdout)
        proc.check_returncode()
    return proc.stdout.decode('utf8').strip()


def get_bins():
    path = 'dist'
    binaries = os.listdir(path)
    bins = []
    for it in binaries:
        if it.endswith('.whl') or platform.system() == 'Linux':
            bins.append('-a')
            bins.append('{}/{}'.format(path, it))
    return bins


def main():
    trigger = os.getenv('GITHUB_REF', '')
    print('Trigger before:', trigger)
    trigger = trigger.split('/')[-1]
    print('Trigger after:', trigger)
    if not re.match(r'v\d+(\.\d+){2,}', trigger):
        version = call('python', 'setup.py', '--version')
        commit = call('git', 'describe', '--always', '--abbrev=8')
        trigger = 'v{}-{}'.format(version, commit)
    print(trigger)

    binaries = get_bins()
    try:
        output = call('hub', 'release', 'create', *binaries, '-m', trigger, trigger)
    except subprocess.CalledProcessError:
        output = call('hub', 'release', 'edit', *binaries, '-m', trigger, trigger)
    print(output)


if __name__ == '__main__':
    main()
