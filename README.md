



Comitup
======

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

The hotspot is named _comitup-&lt;nnnn&gt;_, where _&lt;nnnn&gt;_ is a
persistent 4-digit number. The website is accessible on that hotspot as
_ht&#8203;tp://comitup.local_ or _ht&#8203;tp://comitup-&lt;nnnn&gt;.local_
from any device which supports [Bonjour/ZeroConf/Avahi] [zeroconf]. For
other devices, use a Zeroconf browser ([Android][], [Windows][]) to
determine the IP address of the "Comitup Service", and browse to
_http&#58;//&lt;ipaddress&gt;_. In most cases, this address will be _http&#58;//10.42.0.1/_

[zeroconf]: https://en.wikipedia.org/wiki/Zero-configuration_networking
[Android]: https://play.google.com/store/apps/details?id=com.melloware.zeroconf&hl=en
[Windows]: http://hobbyistsoftware.com/bonjourbrowser

The __comitup-cli__ utility is available to interact with _comitup_ from a
local terminal session.

__comitup__ requires NetworkManager and systemd.

Man pages
---------

* [comitup.8](https://davesteele.github.io/comitup/man/comitup.html)
* [comitup-conf.5](https://davesteele.github.io/comitup/man/comitup-conf.html)
* [comitup-web.8](https://davesteele.github.io/comitup/man/comitup-web.html)
* [comitup-cli.1](https://davesteele.github.io/comitup/man/comitup-cli.html)