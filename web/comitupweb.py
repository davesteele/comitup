#!/usr/bin/python
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
app = Flask(__name__)

import sys
sys.path.append('.')
sys.path.append('..')

from comitup import client as ciu                 # noqa


def do_connect(ssid, password):
    time.sleep(1)
    ciu.ciu_connect(ssid, password)


@app.route("/")
def index():
    points = ciu.ciu_points()
    for point in points:
        point['ssid_encoded'] = urllib.parse.quote_plus(point['ssid'])
    return render_template("index.html", points=points)


@app.route("/confirm")
def confirm():
    ssid = request.args.get("ssid", "")
    ssid_encoded = urllib.parse.quote_plus(base64.b32encode(ssid.encode()))
    encrypted = request.args.get("encrypted", "unencrypted")
    return render_template(
                            "confirm.html",
                            ssid=ssid,
                            encrypted=encrypted,
                            ssid_encoded=ssid_encoded,
                            )


@app.route("/connect", methods=['POST'])
def connect():
    ssid = base64.b32decode(urllib.parse.unquote_plus(request.form["ssid"]))
    password = request.form["password"].encode()

    p = Process(target=do_connect, args=(ssid, password))
    p.start()

    return render_template("connect.html",
                            ssid=ssid.encode(),
                            password=password,
                        )


def main():
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)


if __name__ == '__main__':
    main()
