import os
import subprocess
import sys

import click


@click.command()
@click.option('--ip', '-i', required=False, type=str, default='127.0.0.1', help='If --run-server is selected, specifies the \
IP address to start the server on, otherwise specifies the IP address the server is already running on.')
@click.option('--port', '-p', required=True, type=int, default=8000, help='If --run-server is selected, specifies the \
port to start the server on, otherwise specifies the port the server is already running on.')
@click.option('--max-timeout', '-t', required=False, type=int, default=10, help='Specifies the maximum number of seconds \
that test waits for the page to load before failing.')
@click.option('--run-server', '-r', is_flag=True, help='Start own server and not rely on it already running.')
def run_tests(ip, port, max_timeout, run_server):
    tests = [f for f in os.listdir('tests/') if f.startswith('test') and f.endswith('.py')]
    for test in tests:
        print(test)
        sys.path.append(os.path.abspath('tests/'))
        comlist = ['python3', '-m', 'pytest', f'tests/{test}', '-s', '-p no:warnings', '--ip', ip, '--port', str(port), '--max-timeout', str(max_timeout), '-x', '-m', 'run_server' if run_server else 'not run_server']
        print(comlist)
        input = b'n'
        res = subprocess.run(comlist, input=input, stderr=subprocess.PIPE)
        if res.returncode != 0:
            print("TEST FAILED, QUITTING")
            break


if __name__ == '__main__':
    run_tests()
