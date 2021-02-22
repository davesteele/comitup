
## Making a code contribution

Fork the [repository](https://github.com/davesteele/comitup), make the changes on a new branch off of _master_ (or _main_, if I've gotten around to creating it), and submit a [Pull Request](https://github.com/davesteele/comitup/pulls).

## Submitting a Bug Report/Troubleshooting request

Before you write up a troubleshooting issue consider the following:

* Note that the [Comitup Image](https://davesteele.github.io/comitup/) is preferred.
* If you are using the package:
  * Make sure you have the [most recent](https://davesteele.github.io/comitup/archive.html) version installed
  * Verify that there are no conflicts for the dnsmasq (DHCP), wpa_supplicant, and resolved (DNS) services, as described in the [Installing Comitup](https://github.com/davesteele/comitup/wiki/Installing-Comitup) page.
  * Inspect the logs at "systemctl status comitup", /var/log/comitup.log, and /var/log/comitup-web.log, and resolve issues.

Make a note in the issue that you have covered these topics.

Another troubleshooting write up - https://github.com/davesteele/comitup/issues/91#issuecomment-576462758
