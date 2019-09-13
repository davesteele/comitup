#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import logging
import subprocess
import re
from multiprocessing import Process, Queue


log = logging.getLogger("comitup")

# NetworkManager is doing a poor job of maintaining the AP scan list when
# in AP mode. Use the 'iw' command to get the AP list.


def docmd(cmd):
    cmd = "timeout 5 " + cmd

    try:
        out = subprocess.check_output(cmd.split()).decode()
    except subprocess.CalledProcessError:
        out = ""

    return out


def devlist():
    """Get a list of supported devices from 'iw'"""
    log.debug("Getting device list from 'iw'")
    out = docmd("iw dev")
    devs = [x.split()[1] for x in out.split('\n') if "Interface" in x]
    return devs


def blk2dict(blk):
    """Convert a 'iw dev scan' block into a tagged dict"""

    lines = [x.strip().split(':') for x in blk.split('\n') if ':' in x]
    tups = [(x[0].strip(), x[1].strip()) for x in lines if len(x) > 1]

    return dict(tups)


def dbm2pct(dbm):
    pct = (dbm + 100.0) * 2
    pct = max(0, pct)
    pct = min(100, pct)
    return str(pct)


def devaps(dev, dump=""):
    """Get a list of Access Points (as dicts) for a device"""
    if not dump:
        log.debug("Getting AP list from 'iw' dev %s" % dev)
        dump = docmd('iw dev %s scan' % dev)

    aps = []
    for blk in re.split('\nBSS ', dump[4:]):
        try:
            ap = blk2dict(blk)
            ap['power'] = dbm2pct(float(ap['signal'].split()[0]))
            if ap['SSID']:
                aps.append(ap)
        except KeyError:
            pass

    return aps


def apgen(dev, q, dump=""):
    for ap in devaps(dev, dump):
        pt = {}
        pt['ssid'] = ap['SSID']
        pt['strength'] = ap['power']
        if 'WPA' in ap or 'RSN' in ap:
            pt['security'] = 'encrypted'
        else:
            pt['security'] = 'unencrypted'

        q.put(pt)

    q.put("DONE")


def dedup_aplist(aplist):
    apdict = {x['ssid']: x for x in aplist}

    return [apdict[x] for x in apdict]


def candidates(device=None):
    """Return a list of reachable Access Point SSIDs, sorted by power"""

    if device:
        dev_list = [device]
    else:
        dev_list = devlist()

    jobs = []
    q = Queue()
    for dev in dev_list:
        p = Process(target=apgen, args=(dev, q))
        p.start()
        jobs.append(p)

    clist = []
    donecount = 0
    while donecount < len(jobs):
        pt = q.get()
        if pt == "DONE":
            donecount += 1
        else:
            clist.append(pt)

    for p in jobs:
        p.join()

    clist = dedup_aplist(clist)

    clist = sorted(clist, key=lambda x: -float(x['strength']))

    return clist


def ap_conn_count():
    count = 0
    for dev in devlist():
        log.debug("Getting iw station dump")
        out = docmd('iw dev %s station dump' % dev)
        count += len([x for x in out.split('\n') if "Station" in x])

    return count


if __name__ == '__main__':
    print(candidates())

    print(ap_conn_count())

    import sys

    for ap in devaps(sys.argv[1], sys.stdin.read()):
        print(ap["SSID"], ap["RSN"], ap["power"], "RSN" in ap)
