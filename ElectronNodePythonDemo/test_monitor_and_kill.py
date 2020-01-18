"""
a simple script that starts up other scripts to test
"""

import os
from subprocess import run, Popen
import atexit
import time

subprocesses = [Popen(['python', 'do_nothing.py']),
                Popen(['python', 'do_nothing.py']),
                Popen(['python', 'do_nothing.py']),
                ]

pids = [os.getpid()] + [p.pid for p in subprocesses]

monitor = Popen(['python', 'monitor_and_kill.py'] +
                [str(pid) for pid in pids])


def kill_everything():
    print("killing everything on exit")
    for p in subprocesses:
        p.terminate()

atexit.register(kill_everything)

while True:
    print("App running: ")
    print("Hit ^C To stop:")
    time.sleep(1.0)

