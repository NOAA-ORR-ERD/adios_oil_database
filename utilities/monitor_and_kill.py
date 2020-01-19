#!/usr/bin/env python

"""
simple little script that makes a process killing daemon
"""

import sys
import time
import psutil


def kill_subprocesses():
    for pid in sub_processes:
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess:
            continue  # not there, so we don't care
        p.kill()  # or p.terminate()


def monitor(pid):
    """
    monitor the presense of the main process
    """

    ## maybe use this instead?
    # psutil.wait_procs(procs, timeout=None, callback=None)
    while True:
        if psutil.pid_exists(pid):
            print(pid, "still running")
            time.sleep(0.5)
        else:
            print("main process not there: killing subprocesses and quitting")
            kill_subprocesses()
            sys.exit()

if __name__ == "__main__":
    print("Starting monitor")
    main_process = int(sys.argv[1])
    sub_processes = [int(p) for p in sys.argv[2:]]

    print("main process id: ", main_process)
    print("subprocesses:", sub_processes)
    monitor(main_process)
