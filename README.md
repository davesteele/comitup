



Comitup
======

Bootstrap Wifi using Wifi
-------------------------

The __comitup__ service establishes wifi connectivity for a headless Linux system, using wifi as the only access mechanism to the system.

If the computer cannot automatically connect to a local wifi access point, __comitup__ will create a custom hotspot, and establish a __comitup-web__ web service on that network. The web service can be used to remotely select and authenticate a visible wifi connection. 

The hotspot is named _comitup-&lt;nnnn&gt;_, where _&lt;nnnn&gt;_ is a persistent 4-digit number. The website is accessible on that hotspot as _ht&#8203;tp://comitup.local_ or _ht&#8203;tp://comitup-&lt;nnnn&gt;.local_ from any device which supports [Bonjour/ZeroConf/Avahi] [zeroconf]. For other devices, use a Zeroconf browser ([Android][], [Windows][]) to determine the IP address of the web service, and browse to _ht&#8203;tp://&lt;ipaddress&gt;_.

[zeroconf]: https://en.wikipedia.org/wiki/Zero-configuration_networking
[Android]: https://play.google.com/store/apps/details?id=com.melloware.zeroconf&hl=en
[Windows]: http://hobbyistsoftware.com/bonjourbrowser

The __comitup-cli__ utility is available to interact with _comitup_ from a local terminal session.

Man pages
---------

* [comitup.8](https://github.com/davesteele/comitup/blob/master/doc/comitup.8.ronn)
* [comitup-conf.5](https://github.com/davesteele/comitup/blob/master/doc/comitup-conf.5.ronn)
* [comitup-web.8](https://github.com/davesteele/comitup/blob/master/doc/comitup-web.8.ronn)
* [comitup-cli.1](https://github.com/davesteele/comitup/blob/master/doc/comitup-cli.1.ronn)
