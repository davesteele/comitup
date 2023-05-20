---
layout: default
---

### Wifi Network Bootstrap for the Raspberry Pi

Comitup is a software package that provides a service to establish Wifi
networking on a headless computer (that is, one with no video, keyboard, or mouse).
Comitup supports the following capabilities:

* The comitup service, which automatically connects to any previously
established 
Wifi Access Points, if possible. Otherwise, it will create a stand-alone 
Access Point with the name (SSID) 'comitup-&lt;nnn&gt;', 
where '&lt;nnn&gt;' is a unique, persistent number.
* Defined ZeroConf mdns address name for
'comitup-&lt;nnn&gt;.local', advertising the IP address of the Raspbery
Pi on all interfaces.
* Connection information is published as a _comitup._tcp service, visible
using a ZeroConf Browser.
* A comitup-web service, which provides a web interface for selecting and 
authenticating against an existing Access Point.
* A captive portal, facilitating discovery of the web service on systems
that support it.</li>
* The portal also features a "Locate" function that will blink the front
green LED on a a Raspberry Pi, allowing the user to discriminate between
multiple Comitup Pi's.
* If two wifi interfaces are available on the device, the comitup hotspot
will remain on one, and the other will be used for the upstream connection.
Routing/masquerading between the two networks is established automatically.
* A comitup-cli command-line utility for interacting with comitup.

The Comitup Image is a microSD disk image for the Raspberry Pi, providing
an operating system with the comitup service included. The Comitup Image is an
extension of standard Raspberry Pi OS which includes Comitup, and supports
the following additional
capabilities:

* The ssh service is enabled by default. Be sure to change the default user
password.
* The Raspberry Pi Ethernet port will automatically configure for the host
network if possible. If a DHCP server is not found, the port will set to
a static configuration, with an IP address of 10.0.0.2/24.
* The hostname will be set to the comitup AP name on first
boot.

### Getting Comitup

You can get Comitup by installing the package, or by downloading a Raspberry Pi
OS image including the package (the preferred method).

NOTE: Starting with the 2022-04-16 image, the local "pi" user has been replaced
with the default "comitup" user. The password matches the user name - change it
with the first logon

#### Comitup Image
To [burn](https://github.com/davesteele/comitup/wiki/Tutorial#copy-the-image-to-a-microsd-card) onto an SD card for the Raspberry Pi.

{% for img in ['lite', 'full'] %}
* Comitup {{ imgs[img]['name'] }} [Image](latest/{{ imgs[img]["latestname"] }}-img-latest.html) ({{ imgs[img]['uncompressedstr'] }}B, {{ imgs[img]['compressedstr'] }}B compressed)
  * [Download](https://steele.debian.net/comitup/{{ imgs[img]['filename'] }}) | [Torrent](torrent/{{ imgs[img]['filename'] }}.torrent) | [Magnet]({{ imgs[img]['magnet'] }}) 
  * [SHA1](torrent/{{ imgs[img]['filename'] }}.sha1.txt)
  * [PGP](torrent/{{ imgs[img]['filename'] }}.asc.txt)
  * [Info](https://steele.debian.net/comitup/{{ imgs[img]['infoname'] }})
{% endfor %}

#### Package Installation

* Raspberry Pi OS/Debian users can install the package with "sudo apt-get
  install comitup" (though Buster users shouldn't - more up-to-date-versions of
  the comitup package are HIGHLY RECOMMENDED).
* New package versions are available in the [Package Archive](archive.html) or
  the [comitup repository](ppa.html) (there is also a third-party [RPM repo](https://github.com/davesteele/comitup/issues/222)). The latest version can be downloaded
  [here](latest/comitup_latest.html).
* Remove any references to wifi interfaces in "/etc/network/interfaces" so that
  Network Manager/Comitup can manage them.
* See [Installing
  Comitup](https://github.com/davesteele/comitup/wiki/Installing-Comitup) for
  other possible installation issues.

### Documentation

* The <a href="https://github.com/davesteele/comitup/wiki">Comitup
Wiki</a> (with <a href="https://github.com/davesteele/comitup/wiki/Tutorial">Tutorial</a>).
* Man pages
  * <a href="man/comitup.pdf">comitup (8)</a>
  * <a href="man/comitup-conf.pdf">comitup-conf (5)</a>
  * <a href="man/comitup-web.pdf">comitup-web (8)</a>
  * <a href="man/comitup-cli.pdf">comitup-cli (1)</a>
* <a href="https://github.com/davesteele/comitup/blob/debian/debian/changelog">Changelog</a>

### Support/Feedback

* [Issues](https://github.com/davesteele/comitup/issues)
* [Discussions](https://github.com/davesteele/comitup/discussions)

### Related Software

<dl>
  <dt><a href="https://github.com/davesteele/comitup-watch">Comitup-Watch</a></dt>
    <dd>
      Continuously monitor the status of connected and unconnected nearby Comitup-enabled devices.
    </dd>
  <dt><a href="https://github.com/davesteele/comitup-demo">Comitup-Demo</a></dt>
    <dd>
      Demonstrate the operation of a Comitup-enabled device, reporting
      connection status progress using voice synthesis.
    </dd>
</dl>
