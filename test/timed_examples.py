#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import reusables
import shlex

# Compare find all files vs linux `find`

path = "/home"
runs = 20

command = "find {0} -iname '*.gif' -o -iname '*.jpg' -o -iname '*.png' " \
          "-o -iname '*.jpeg'".format(path)
command = shlex.split(command)

start_1 = time.time()
for _ in range(runs):
    cmd_run = reusables.run(command)
    results = cmd_run.stdout.decode("utf-8").strip().split("\n")
print("Find took {0:.3f} seconds on average".format((time.time() -
                                                     start_1) / runs))

start_2 = time.time()
for _ in range(runs):
    results2 = reusables.find_all_files("/home/james",
                                        ext=(".gif", ".jpg", ".png", ".jpeg"))

print("Reusables took {0:.3f} seconds on average".format((time.time() -
                                                          start_2) / runs))

assert len(results) == len(results2)


