#!/usr/bin/python3
# Copyright (c) 2018 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2+
# License-Filename: LICENSE

import time
from multiprocessing import Process

if __name__ == '__main__':
    import os
    import sys
    fullpath = os.path.abspath(__file__)
    parentdir = '/'.join(fullpath.split('/')[:-2])
    sys.path.insert(0, parentdir)

from comitup import client

ciu = client.CiuClient()


def kickNM(delay=0):
    time.sleep(delay)
    ciu.ciu_state()
    ciu.ciu_points()


def kickNMProc(*, delay=5, async=True):
    p = Process(target=kickNM, args=(delay,))
    p.start()

    if not async:
        p.join()


def main():
    kickNMProc(async=False)


if __name__ == '__main__':
    main()
