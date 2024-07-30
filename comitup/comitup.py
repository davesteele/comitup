#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE


import argparse
import logging
import os
import signal
import sys
import types
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)
from gi.repository.GLib import MainLoop  # noqa

from comitup import cdns  # noqa
from comitup import config  # noqa
from comitup import nftmgr  # noqa
from comitup import nuke  # noqa
from comitup import persist  # noqa
from comitup import statemgr  # noqa
from comitup import sysd  # noqa
from comitup import webmgr  # noqa
from comitup import wificheck  # noqa

LOG_PATH: str = "/var/log/comitup.log"
log: Optional[logging.Logger] = None


def deflog(verbose: int) -> logging.Logger:
    level = logging.INFO
    if verbose:
        level = logging.DEBUG

    log = logging.getLogger("comitup")
    log.setLevel(level)
    handler = TimedRotatingFileHandler(
        LOG_PATH,
        encoding="utf=8",
        when="W0",
        backupCount=8,
    )
    fmtr = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(fmtr)
    log.addHandler(handler)

    return log


def check_environment(log: logging.Logger) -> None:
    for service in ["systemd-resolved", "dnsmasq", "dhcpd", "dhcpcd"]:
        try:
            if sysd.sd_unit_jobs("{}.service".format(service)):
                for msg in [
                    "Warning: {} service is active.".format(service),
                    "This may interfere with comitup providing "
                    "networking services",
                ]:
                    print(msg)
                    log.warning(msg)
        except Exception:
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="Check the wifi devices and exit",
    )

    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Print info and exit",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="More verbose logging",
    )

    args = parser.parse_args()

    return args


def cleanup() -> None:
    # leave the network setup as it, but kill comitup-web
    webmgr.stop_service(webmgr.COMITUP_SERVICE)
    nuke.cleanup_nuke()
    if log:
        log.info("Stopping comitup")


def handle_term(signum: int, handler: types.FrameType) -> None:
    cleanup()
    sys.exit(0)


def main():
    global log

    if os.geteuid() != 0:
        exit("Comitup requires root privileges")

    args = parse_args()

    (conf, data) = config.load_data()

    log = deflog(args.verbose or conf.getboolean("verbose"))
    log.info("Starting comitup")

    if args.info:
        for key, val in statemgr.get_info(conf, data).items():
            print("{}: {}".format(key, val))
        sys.exit(0)

    if args.check:
        if wificheck.run_checks(primary_dev=conf.primary_wifi_device):
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        wificheck.run_checks(
            verbose=False,
            primary_dev=conf.primary_wifi_device,
        )

    check_environment(log)

    webmgr.init_webmgr(conf.web_service)
    nftmgr.init_nftmgr()

    statemgr.init_state_mgr(
        conf,
        data,
        [
            webmgr.state_callback,
            nftmgr.state_callback,
            cdns.state_callback,
        ],
    )

    nuke.init_nuke()

    signal.signal(signal.SIGTERM, handle_term)

    loop = MainLoop()

    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    except Exception:
        log.error("Terminal exception encountered")
        raise
    finally:
        cleanup()


if __name__ == "__main__":
    main()
