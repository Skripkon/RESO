import os
import subprocess
import sys

import click


@click.command()
@click.option('--port', '-p', required=True, type=int, default=8000, help='If --run-server is selected, specifies the \
port to start the server on, otherwise specifies the port the server is already running on.')
@click.option('--run-server', '-r', is_flag=True, help='Start own server and not rely on it already running.')
def run_tests(port, run_server):
    tests = [f for f in os.listdir('tests/') if f.startswith('test') and f.endswith('.py')]
    # ((run_server and f.endswith('_run_server.py')) or (not run_server and f.endswith('_no_server.py')))]
    for test in tests:
        print(test)
        sys.path.append(os.path.abspath('tests/'))
        comlist = ['python3', '-m', 'pytest', f'tests/{test}', '-s', '-p no:warnings', '--port', str(port), '-m', 'run_server' if run_server else 'not run_server']
        print(comlist)
        input = b'n'
        subprocess.run(comlist, input=input, stderr=subprocess.PIPE)


if __name__ == '__main__':
    run_tests()
