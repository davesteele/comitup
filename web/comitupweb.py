#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

from flask import Flask, render_template, request, send_from_directory,\
                  redirect, abort
import logging
from logging.handlers import TimedRotatingFileHandler
from multiprocessing import Process
import sys
import time
import urllib

sys.path.append('.')
sys.path.append('..')

from comitup import client as ciu                 # noqa

ciu_client = None
LOG_PATH = "/var/log/comitup-web.log"
TEMPLATE_PATH = "/usr/share/comitup/web/templates"


def deflog():
    log = logging.getLogger('comitup_web')
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


def do_connect(ssid, password, log):
    time.sleep(1)
    log.debug("Calling client connect")
    ciu_client.service = None
    ciu_client.ciu_connect(ssid, password)


def create_app(log):
    app = Flask(__name__, template_folder=TEMPLATE_PATH)

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        points = ciu_client.ciu_points()
        for point in points:
            point['ssid_encoded'] = urllib.parse.quote(point['ssid'])
        log.info("index.html - {} points".format(len(points)))
        return render_template("index.html", points=points)

    @app.route('/js/<path:path>')
    def send_js(path):
        return send_from_directory(TEMPLATE_PATH + '/js', path)

    @app.route('/css/<path:path>')
    def send_css(path):
        return send_from_directory(TEMPLATE_PATH + '/css', path)

    @app.route("/confirm")
    def confirm():
        ssid = request.args.get("ssid", "")
        ssid_encoded = urllib.parse.quote(ssid.encode())
        encrypted = request.args.get("encrypted", "unencrypted")

        mode = ciu_client.ciu_info()['imode']

        log.info("confirm.html - ssid {0}, mode {1}".format(ssid, mode))

        return render_template(
                                "confirm.html",
                                ssid=ssid,
                                encrypted=encrypted,
                                ssid_encoded=ssid_encoded,
                                mode=mode,
                                )

    @app.route("/connect", methods=['POST'])
    def connect():
        ssid = urllib.parse.unquote(request.form["ssid"])
        password = request.form["password"].encode()

        p = Process(target=do_connect, args=(ssid, password, log))
        p.start()

        log.info("connect.html - ssid {0}".format(ssid))
        return render_template(
                "connect.html",
                ssid=ssid,
                password=password,
                )

    @app.route("/img/favicon.ico")
    def favicon(path):
        log.info("Returning 404 for favicon request")
        abort(404)

    @app.route("/<path:path>")
    def catch_all(path):
        return redirect("http://10.41.0.1/", code=302)

    return app


def main():
    log = deflog()
    log.info("Starting comitup-web")

    global ciu_client
    ciu_client = ciu.CiuClient()

    ciu_client.ciu_state()
    ciu_client.ciu_points()

    app = create_app(log)
    app.run(host="0.0.0.0", port=80, debug=False, threaded=True)


if __name__ == '__main__':
    main()
