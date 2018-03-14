#!/usr/bin/python3
# Copyright (c) 2017 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2+
# License-Filename: LICENSE

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import os
import time
from multiprocessing import Process
import urllib
import base64
from flask import Flask, render_template, request

import sys
sys.path.append('.')
sys.path.append('..')

from comitup import client as ciu                 # noqa

ciu_client = None


def do_connect(ssid, password):
    time.sleep(1)
    ciu_client.ciu_connect(ssid, password)


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        points = ciu_client.ciu_points()
        for point in points:
            point['ssid_encoded'] = urllib.parse.quote(point['ssid'])
        return render_template("index.html", points=points)


    @app.route("/confirm")
    def confirm():
        ssid = request.args.get("ssid", "")
        ssid_encoded = urllib.parse.quote(ssid.encode())
        encrypted = request.args.get("encrypted", "unencrypted")
        return render_template(
                                "confirm.html",
                                ssid=ssid,
                                encrypted=encrypted,
                                ssid_encoded=ssid_encoded,
                                )


    @app.route("/connect", methods=['POST'])
    def connect():
        ssid = urllib.parse.unquote(request.form["ssid"])
        password = request.form["password"].encode()

        p = Process(target=do_connect, args=(ssid, password))
        p.start()

        return render_template("connect.html",
                                ssid=ssid,
                                password=password,
                            )

    return app


def main():
    global ciu_client
    ciu_client = ciu.CiuClient()

    app = create_app()
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)


if __name__ == '__main__':
    main()
