#!/usr/bin/python

#
# Copyright 2016 David Steele <dsteele@gmail.com>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import sys
sys.path.append('.')
sys.path.append('..')

import cherrypy                                   # noqa
import os                                         # noqa
from jinja2 import Environment, FileSystemLoader  # noqa
from comitup import client as ciu                 # noqa

env = None


class HelloWorld(object):
    def index(self):
        tmpl = env.get_template('index.html')

        points = ciu.ciu_points()

        return tmpl.render(points=points)
    index.exposed = True

    def confirm(self, ssid="", encrypted="unencrypted"):
        tmpl = env.get_template('confirm.html')

        return tmpl.render({'ssid': ssid, 'encrypted': encrypted})
    confirm.exposed = True

    def connect(self, ssid="", password=""):
        tmpl = env.get_template('confirm.html')

        ciu.ciu_connect(ssid, password)
        return tmpl.render({'ssid': ssid, 'password': password})
    connect.exposed = True


cherrypy.root = HelloWorld()


def main():
    global env

    proj_path = os.path.dirname(os.path.abspath(__file__))
    conf_path = os.path.join(proj_path, "comitupweb.conf")
    env_path = os.path.join(proj_path, "templates")

    env = Environment(loader=FileSystemLoader(env_path))

    cherrypy.config.update(file=conf_path)

    cherrypy.server.start()


if __name__ == '__main__':
    main()
