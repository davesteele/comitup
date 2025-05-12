#!/usr/bin/python3

import subprocess
import sys
from datetime import date

"""
This script is an aid to updating the GPG key to be used for signing the
personal repository, coordinating with the davesteele-apt-source pacakage.

This is invoked via the reprepro config distributions "signwith" tag.
"""

# This is my current key
key = "0959C4A3DCF89FBF"
killdate = date(2025, 10, 22)

if date.today() > killdate:
    print("time to update {} to a new key".format(sys.argv[0]))
    sys.exit(1)

# args are defined with the "signfile" tag in reprepro man page
(infile, outinline, outdetached) = sys.argv[1:4]

if outinline:
    cmd = "gpg --clear-sign --local-user {}! -o {} {}".format(
        key, outinline, infile
    )
    print('running "{}"'.format(cmd))
    cp = subprocess.run(cmd, shell=True, check=True)

if outdetached:
    cmd = "gpg --detach-sign -a --local-user {}! -o {} {}".format(
        key, outdetached, infile
    )
    print('running "{}"'.format(cmd))
    cp = subprocess.run(cmd, shell=True, check=True)
