#!/usr/bin/python

import subprocess
import re


# NetworkManager is doing a poor job of maintaining the AP scan list when
# in AP mode. Use the 'iw' command to get the AP list.

def docmd(cmd):
    try:
        out = subprocess.check_output(cmd.split()).decode()
    except subprocess.CalledProcessError:
        out = ""

    return out


def devlist():
    """Get a list of supported devices from 'iw'"""
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


def devaps(dev):
    """Get a list of Access Points (as dicts) for a device"""
    out = docmd('iw dev %s scan' % dev)

    aps = []
    for blk in re.split('\nBSS ', out[4:]):
        try:
            ap = blk2dict(blk)
            ap['power'] = dbm2pct(float(ap['signal'].split()[0]))
            if ap['SSID']:
                aps.append(ap)
        except KeyError:
            pass

    return aps


def candidates():
    """Return a list of reachable Access Point SSIDs, sorted by power"""

    clist = []
    for dev in devlist():
        for ap in devaps(dev):
            pt = {}
            pt['ssid'] = ap['SSID']
            pt['strength'] = ap['power']
            if 'WPA' in ap:
                pt['security'] = 'encrypted'
            else:
                pt['security'] = 'unencrypted'

            clist.append(pt)

    clist = sorted(clist, key=lambda x: -float(x['strength']))

    return clist


def ap_conn_count():
    count = 0
    for dev in devlist():
        out = docmd('iw dev %s station dump' % dev)
        count += len([x for x in out.split('\n') if "Station" in x])

    return count


if __name__ == '__main__':
    print(candidates())

    print(ap_conn_count())
