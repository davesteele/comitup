#!/usr/bin/python

import shutil
import json
import os

def addrepo(dist, debs):
    cmd = "reprepro -Vb repo --ignore=wrongdistribution includedeb "
    debs = ['deb/' + x for x in debs]
    cmd += dist + " " + " ".join(debs)

    os.system(cmd)

for entry in ['db', 'dists', 'pool']:
    try:
        shutil.rmtree('./repo/' + entry)
    except OSError:
        pass

with open('pkgs.json') as fp:
    debs = json.load(fp)

addrepo('comitup-jessie', debs['latest_pkgs'])

