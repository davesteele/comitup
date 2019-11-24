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
import subprocess

sys.path.append('.')
sys.path.append('..')

from comitup import client as ciu                 # noqa
from comitup.iwscan import candidates
from uuid import uuid4
import os

ciu_client = None
LOG_PATH = "/var/log/comitup-web.log"
PUPPETEER_SCRIPT_FILEPATH= "/etc/opt/comitup-ias-puppeteer-scripts"


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


def do_connect(ssid, password, log, username=None, ias_login_script=None):
    time.sleep(1)
    log.debug("Calling client connect")
    ciu_client.service = None
    if username is not None:
        def add_8012x_nm_connection_file(ssid, username, password):
            # TODO: move this into a new dbus endpoint at comitup.statemgr.Comitup.connect_8012x or something
            # set umask with only root rw permissions
            oldmask = os.umask(0o66)
            with open(os.open(f"/etc/NetworkManager/system-connections/{ssid}.nmconnection", os.O_CREAT | os.O_WRONLY, 0o600), 'w') as connection_file:
                connection_file.write(render_template("8012x.nmconnection.template", uuid=uuid4(), ssid=ssid, username=username, password=password))
            os.umask(oldmask)

        add_8012x_nm_connection_file(ssid, username, password)
        subprocess.check_call('sudo systemctl restart NetworkManager'.split())
        log.debug('waiting for connection to ' + ssid)

        def is_connected(ssid):
            import NetworkManager
            from importlib import reload
            from comitup import nm

            try:
                # this is super weird because the NetworkManager definitions is based of dynamically-loaded dbus information.
                # this means that if NetworkManager is down (which it should be while it restarts), GetDevices() doesn't exist.,
                # so we try to acccess it, then if we hit an AttributeError, reload the networkmanager and try again
                devices = NetworkManager.NetworkManager.GetDevices()
                return any(nm.get_active_ssid(device) == ssid for device in NetworkManager.NetworkManager.GetDevices())
            except NetworkManager.ObjectVanished:
                return False
            except AttributeError:
                reload(NetworkManager)
                return False

        while(not is_connected(ssid)):
            time.sleep(0.5)
            log.debug('still waiting...')
    else:
        ciu_client.ciu_connect(ssid, password)
    log.debug(f'successfully connected! script: {ias_login_script}')
    if ias_login_script is not None:
        from ias import runner
        runner.run(puppeteer_script_filepath=os.path.join(PUPPETEER_SCRIPT_FILEPATH, ias_login_script), username=username, password=password)


def create_app(log):
    app = Flask(__name__)

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
        return send_from_directory('templates/js', path)

    @app.route('/css/<path:path>')
    def send_css(path):
        return send_from_directory('templates/css', path)

    @app.route("/confirm")
    def confirm():
        ssid = request.args.get("ssid", "")
        ssid_encoded = urllib.parse.quote(ssid.encode())
        encrypted = request.args.get("encrypted", "unencrypted")

        # networkmanager only lists the active hotspot access point if it is the running on the only wifi device available.
        # iwscan however, works regardless, so check the authentication details with that.
        # TODO: move this into the comitup service and add command-line access as well
        is_8021x = next(can for can in candidates() if can['ssid'] == ssid)\
            ['is_enterprise'] == 'True'

        ias_login_scripts = [
            f.name for f in os.scandir(PUPPETEER_SCRIPT_FILEPATH)
            if f.is_file() and f.name.endswith('.js') and not f.name == '_example.js'
        ]

        mode = ciu_client.ciu_info()['imode']

        log.info("confirm.html - ssid {0}, mode {1}".format(ssid, mode))

        return render_template(
            "confirm.html",
            ssid=ssid,
            encrypted=encrypted,
            ssid_encoded=ssid_encoded,
            mode=mode,
            is_8021x=is_8021x,
            ias_login_scripts=ias_login_scripts
        )

    @app.route("/connect", methods=['POST'])
    def connect():
        form = request.form
        ssid = urllib.parse.unquote(form["ssid"])
        password = form["password"]
        # username should only be sent if is_8021x was set at the confirmation render
        username = form['username'] if 'username' in form else None

        ias_login_script = form['ias_login_script'] if 'ias_login_script' in form and form['ias_login_script'] is not 'none' else None 
        log.info(f"chosen login script: {ias_login_script}")

        p = Process(target=do_connect, args=(ssid, password, log, username, ias_login_script))
        p.start()

        log.info("connect.html - ssid {0}".format(ssid))
        return render_template(
            "connect.html",
            ssid=ssid,
            password=password,
        )

    @app.route("/img/favicon.ico")
    def favicon():
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
