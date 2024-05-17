from multiprocessing import Process
import os
import signal
import subprocess
import sys
from time import sleep

import click
from utils.download_models_and_data import download_models, download_notes


class ServerError(Exception):
    pass


LOG_PATH = os.path.join('tests', 'log')
SERVER_STOP_SIGNAL_ID = 50
server_pid = -1


@click.command()
@click.option('--ip', '-i', required=False, type=str, default='127.0.0.1', help='If --run-server is selected, specifies the \
IP address to start the server on, otherwise specifies the IP address the server is already running on.')
@click.option('--port', '-p', required=True, type=int, default=8000, help='If --run-server is selected, specifies the \
port to start the server on, otherwise specifies the port the server is already running on.')
@click.option('--max-timeout', '-t', required=False, type=int, default=10, help='Specifies the maximum number of seconds \
that test waits for the page to load before failing.')
@click.option('--run-server', '-r', required=False, is_flag=True, help='Start own server and not rely on it already running.')
@click.option('--all', '-a', required=False, is_flag=True, help='Run all tests regardless of whether they fail or not.')
def run_tests(ip, port, max_timeout, run_server, all):
    signal.signal(signal.SIGINT, main_process_sigint_handler)
    global server_pid
    if run_server:
        server_pid = start_server(ip, port)

    sys.path.append(os.path.abspath('tests/'))
    test_result = 0
    for test in sorted([f for f in os.listdir('tests/') if f.startswith('test') and f.endswith('.py')]):
        comlist = ['python3', '-m', 'pytest', f'tests/{test}', '-s', '-p no:warnings', '--ip', ip, '--port', str(port), '--max-timeout', str(max_timeout), '-x']
        print(' '.join(comlist))
        res = subprocess.run(comlist, input=b'n', stderr=subprocess.PIPE)
        test_result |= res.returncode
        if res.returncode != 0 and not all:
            print("TEST FAILED, QUITTING")
            break

    if run_server:
        stop_server()

    exit(test_result)


def server_process_serverstop_handler(signum, frame):
    print("\nSTOPPING SERVER...")
    exit(0)


def empty_signal_handler(signum, frame):
    pass


def main_process_sigint_handler(signum, frame):
    global server_pid
    print("\nSTOPPING TESTS...")
    if server_pid > 0:
        stop_server()
    exit(0)


def background_server_runner(ip: str, port: str):
    print(f"\nSTARTING THE SERVER ON {ip}:{port}...")
    signal.signal(SERVER_STOP_SIGNAL_ID, server_process_serverstop_handler)
    signal.signal(signal.SIGINT, empty_signal_handler)
    f_err = open(LOG_PATH, 'a', os.O_NONBLOCK)
    download_models(force=True)
    download_notes(force=True)
    command = ['uvicorn', 'main:app', '--host', ip, '--port', port]
    subprocess.run(command, input=b'n', stderr=f_err)  # , stdout=f_err)


def start_server(ip: str, port: int) -> int:
    """Starts the server in a separate process and returns its pid."""
    os.system(f'echo > {LOG_PATH}')
    try:
        f_err = open(LOG_PATH, 'r', os.O_NONBLOCK)
    except FileNotFoundError:
        raise ServerError("Could not create log file. Aborting.")
    proc = Process(target=background_server_runner, args=(ip, str(port)), daemon=True)
    proc.start()
    log = ''
    while True:
        sleep(2)
        log += f_err.read()
        if "Application shutdown complete." in log:
            print("Stopping server because of start error")
            stop_server()
            raise ServerError("Could not start the server.")
        if "Application startup complete." in log and "Application shutdown complete." not in log:
            print("\n=============\nSERVER STARTED\n=============")
            break
    return proc.pid


def stop_server():
    global server_pid
    os.system(f'kill -s {SERVER_STOP_SIGNAL_ID} {server_pid}')
    try:
        os.remove(LOG_PATH)
    except FileNotFoundError:
        pass
    print("CLEAN UP FINISHED")


if __name__ == '__main__':
    run_tests()
