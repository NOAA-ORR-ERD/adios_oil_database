#!/usr/bin/env python

import os
import time

pid = os.getpid()

i = 0
while True:
    i += 1
    print(f"{pid} doing nothing for the {i}th time")
    time.sleep(2.0)

