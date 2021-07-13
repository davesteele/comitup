
## Making a code contribution

Fork the [repository](https://github.com/davesteele/comitup), make the changes on a new branch off of _main_, and submit a [Pull Request](https://github.com/davesteele/comitup/pulls).

Contributions should pass _devtest.py_, otherwise GitHub CI tests will very likely fail.

## Submitting a Bug Report/Troubleshooting request

Before you write up a troubleshooting issue consider the following:

* Note that the [Comitup Image](https://davesteele.github.io/comitup/) is preferred. If you do use this, do an "apt-get update; apt-get upgrade" to ensure the most recent comitup version.
* If you are using the package:
  * Make sure you have the [most recent](https://davesteele.github.io/comitup/archive.html) version installed
  * No, really, Make sure the version is up-to-date. A good way to do this is to install the [davesteele-comitup-apt-source](https://davesteele.github.io/comitup/archive.html) package before an apt install or update/upgrade.
  * Verify that there are no conflicts for the dnsmasq (DHCP), wpa\_supplicant, and resolved (DNS) services, as described in the [Installing Comitup](https://github.com/davesteele/comitup/wiki/Installing-Comitup) page.
  * Inspect the logs at "systemctl status comitup", /var/log/comitup.log, and /var/log/comitup-web.log, and resolve issues.

Make a note in the issue that you have covered these topics.

Also note your hardware platform, and whether or not you are running with two WiFi adapters.

Another troubleshooting write up - https://github.com/davesteele/comitup/issues/91#issuecomment-576462758
