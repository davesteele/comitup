#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE


import argparse
import logging
import os
import random
import sys
from logging.handlers import TimedRotatingFileHandler

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
from gi.repository.GLib import MainLoop  # noqa

from comitup import cdns         # noqa
from comitup import config       # noqa
from comitup import iptmgr       # noqa
from comitup import persist      # noqa
from comitup import statemgr     # noqa
from comitup import sysd         # noqa
from comitup import webmgr       # noqa
from comitup import wificheck    # noqa

PERSIST_PATH = "/var/lib/comitup/comitup.json"
CONF_PATH = "/etc/comitup.conf"
LOG_PATH = "/var/log/comitup.log"


def deflog():
    log = logging.getLogger('comitup')
    log.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(
                LOG_PATH,
                encoding='utf=8',
                when='D',
                interval=7,
                backupCount=8,
              )
    fmtr = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
           )
    handler.setFormatter(fmtr)
    log.addHandler(handler)

    return log


def load_data():
    conf = config.Config(
                CONF_PATH,
                defaults={
                    'ap_name': 'comitup-<nnn>',
                    'ap_password': '',
                    'web_service': '',
                    'external_callback': '/usr/local/bin/comitup-callback',
                },
             )

    data = persist.persist(
                PERSIST_PATH,
                {'id': str(random.randrange(1000, 9999))},
           )

    return (conf, data)


def check_environment(log):
    for service in ["systemd-resolved", "dnsmasq"]:
        try:
            if sysd.sd_unit_jobs("{}.service".format(service)):
                for msg in [
                    "Warning: {} service is active.".format(service),
                    "This may interfere with comitup providing "
                    "DNS and DHCP services",
                ]:
                    print(msg)
                    log.warn(msg)
        except Exception:
            pass


def parse_args():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        '-c',
        '--check',
        action='store_true',
        help="Check the wifi devices and exit",
    )

    args = parser.parse_args()

    return args


def main():
    if os.geteuid() != 0:
        exit("Comitup requires root privileges")

    args = parse_args()

    log = deflog()
    log.info("Starting comitup")

    (conf, data) = load_data()

    if args.check:
        if wificheck.run_checks():
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        wificheck.run_checks(verbose=False)

    check_environment(log)

    webmgr.init_webmgr(conf.web_service)
    iptmgr.init_iptmgr()

    statemgr.init_state_mgr(
                conf, data,
                [
                    webmgr.state_callback,
                    iptmgr.state_callback,
                    cdns.state_callback,
                ],
             )

    loop = MainLoop()
    loop.run()


if __name__ == '__main__':
    main()
