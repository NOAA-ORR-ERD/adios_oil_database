#!/usr/bin/env python

"""
simple little script that makes a process killing daemon
"""

import sys
import psutil


if __name__ == "__main__":
    main_process = sys.argv[1]
    sub_processes = sys.argv[2:]

kill_subprocesses(*process_ids):
    for pid in process_ids:
        p = psutil.Process(pid)
        p.terminate()  #or p.kill()



def monitor():
    pass
