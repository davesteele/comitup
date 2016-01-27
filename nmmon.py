#!/usr/bin/python

import dbus
import gobject

from collections import defaultdict
from dbus.mainloop.glib import DBusGMainLoop

import logging

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

import nm   # noqa



#
# globals
#

log = logging.getLogger('comitup')

bus = dbus.SystemBus()

device_path = None
device_listener = None


def null_fn():
    pass

nm_dev_connect = null_fn
nm_dev_fail = null_fn

#
# functions
#

def set_device_callbacks(up, down):
    global nm_dev_connect
    global nm_dev_fail

    nm_dev_connect = up
    nm_dev_fail = down



def nm_device_change(state, *args):
    #print "device at state %s connecting to %s" % (state, "something")

    # see for device states:
    # https://developer.gnome.org/NetworkManager/stable/spec.html
    # #type-NM_DEVICE_STATE
    if state == 100:
        nm_dev_connect()
    elif state == 120:
        nm_dev_fail()


def set_device_listener(path):
    global device_listener

    if device_listener:
        device_listener.remove()

    log.debug("adding listener for path %s" % path)

    device_listener = bus.add_signal_receiver(
        nm_device_change,
        signal_name="StateChanged",
        dbus_interface="org.freedesktop.NetworkManager.Device",
        path=path
    )


def check_device_listener(force=False):
    global device_path

    current_path = nm.get_device_path()

    if force or (current_path and current_path != device_path):
        device_path = current_path
        set_device_listener(device_path)


def nm_state_change(state):
    global device_path

    #print("state: ", state)

    # https://developer.gnome.org/NetworkManager/stable/spec.html
    # #type-NM_STATE
    if state >= 50:
        log.debug("We're connected with state %s" % state)

        check_device_listener()


bus.add_signal_receiver(
    nm_state_change,
    signal_name="StateChanged",
    dbus_interface="org.freedesktop.NetworkManager"
)

nm_state_change(nm.nm_state())


def set_nm_listeners():
    bus.add_signal_receiver(
        check_device_listener,
        signal_name="DeviceAdded",
        dbus_interface="org.freedesktop.NetworkManager"
    )

    bus.add_signal_receiver(
        check_device_listener,
        signal_name="DeviceRemoved",
        dbus_interface="org.freedesktop.NetworkManager"
    )

    check_device_listener()


def init_nmmon():
    set_nm_listeners()


def main():
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('starting')

    init_nmmon()

    def up():
        print("wifi up")

    def down():
        print("wifi down")


    set_device_callbacks(up, down)

    loop = gobject.MainLoop()
    loop.run()


if __name__ == '__main__':
    main()
