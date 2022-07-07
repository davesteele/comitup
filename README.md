




Comitup
======

[![Build Status](https://github.com/davesteele/comitup/actions/workflows/testnox.yml/badge.svg?branch=master)](https://github.com/davesteele/comitup/actions)

[Home Page](https://davesteele.github.io/comitup/)

[Wiki](https://github.com/davesteele/comitup/wiki)

Bootstrap Wifi using Wifi
-------------------------

The __comitup__ service establishes wifi connectivity for a headless Linux
system, using wifi as the only access mechanism to the system.

If the computer cannot automatically connect to a local wifi access point,
__comitup__ will create a custom hotspot, and establish a __comitup-web__
web service on that network. The web service can be used to remotely select
and authenticate a visible wifi connection. 

The hotspot is named _comitup-&lt;nnn&gt;_, where _&lt;nnn&gt;_ is a
persistent number. The website is accessible on that hotspot as
_ht&#8203;tp://comitup-&lt;nnn&gt;.local_
from any device which supports [Bonjour/ZeroConf/Avahi][zeroconf]. For
other devices, use a Zeroconf browser ([Android][], [Windows][]) to
determine the IP address of the "Comitup Service", and browse to
_http&#58;//&lt;ipaddress&gt;_. This address will be _http&#58;//10.41.0.1/_

The __comitup__ service implements a [captive portal](https://en.wikipedia.org/wiki/Captive_portal) while in HOTSPOT mode. On supported systems (IOS,
Android, MacOS, Linux, or anything running Firefox), the connection web
page will come up automatically when connecting to the access point.

Comitup can remember multiple upstream connections, and will search among them
in the connection attempt, making it easier to move your device to different
locations.

If two wifi interfaces are available, the first will persistently remain
the hotspot, and the second will get the external connection. When both
are connected, forwarding and masquerading are enabled so that
hotspot-connected devices can access external networks.

On the Raspberry Pi, the comitup-web service, running in the hotspot mode,
supports a "Locate" feature that blinks the green led on the front of the unit.

[zeroconf]: https://en.wikipedia.org/wiki/Zero-configuration_networking
[Android]: https://play.google.com/store/apps/details?id=com.melloware.zeroconf&hl=en
[Windows]: http://hobbyistsoftware.com/bonjourbrowser

The __comitup-cli__ utility is available to interact with _comitup_ from a
local terminal session.

__comitup__ requires NetworkManager and systemd.

See the [Home Page](https://davesteele.github.io/comitup/) for installation information.

Man pages
---------

* [comitup.8](https://davesteele.github.io/comitup/man/comitup.pdf)
* [comitup-conf.5](https://davesteele.github.io/comitup/man/comitup-conf.pdf)
* [comitup-web.8](https://davesteele.github.io/comitup/man/comitup-web.pdf)
* [comitup-cli.1](https://davesteele.github.io/comitup/man/comitup-cli.pdf)
