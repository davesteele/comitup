% comitup(8)
%
% February 2019

# NAME

comitup -- Manage wifi connections on headless, unconnected systems

## SYNOPSIS

`comitup [options]`

## DESCRIPTION

The **comitup** service provides a means to establish a connection between a
computer and a wifi access point, in the case where wifi is the only means
available to access the computer.

On startup, the service will attempt to connect to wifi using established
networkmanager(8) connections. If this is not successful, **comitup** will
establish a wifi hotspot with the name _comitup-&lt;nn&gt;_, where &lt;nn&gt; is
a persistent 2-digit number.

While the hotspot is active, a comitup-web(8) service is available to manage
connecting to an access point.

If two wifi interfaces are available, the hotspot will remain active on the
first interface, and the internet connection will be made on the second.
Otherwise, the hotspot will be replaced with the internet connection.

In all states, avahi-daemon(8) is used to publish the mdns host name
_comitup-&lt;nn&gt;.local_, making the web service accessible
as e.g. _http://comitup-12.local_, for systems supporting Zeroconf. For other
systems, a _comitup_ Workstation entry is published which is visible to Zeroconf
browsing applications, allowing the IP address to be manually determined.
The web service address is _http://10.41.0.1_.

**comitup** logs to _/var/log/comitup.log_.

## Options
  * _-h_, _--help_ - Print help and exit
  * _-c_, _--check_ - Check the wifi device configuration and exit

## D-Bus Interface

**Comitup** provides a D-Bus object which claims the name
_com.github.davesteele.comitup_ on the path
_/com/github/davesteele/comitup_, supporting the
interface _com.github.davesteele.comitup_. The interface includes the
following methods.

  * _get_info()_

    Input: None

    Output: _DICT_ENTRY_

    Return information about the current **Comitup** service. The keys are
    as follows:

      * _version_ - The package version.

      * _apname_ - The currently configured AP hotspot name.

      * _hostnames_ - A list of host names that are published for the service
        IP address.

      * _imode_ - The current interface mode for comitup. This returns the string
        'single' or 'router'. In 'single' mode, the hotspot is terminated when
        **CONNECTED**. In 'router' mode, the hotspot is retained, the upstream
        connection is made with the other wifi device, and traffic is routed
        between them. The web service is terminated when **CONNECTED**.

  * _access_points()_

    Input: None

    Output: Array of _DICT_ENTRY_

    Return a list of visible access points. This is represented as an array
    of D-Bus _DICT_ENTRY_. Each _DICT_ENTRY_ contains strings associated with
    the following keys, _ssid_, _strength_ (0 to 100) and _security_
    (_encrypted_ or _unencrypted_).

  * _state()_

    Input: None

    Output: _state_, _connection_

    This returns strings for the current **comitup** state (either
    **HOTSPOT**, **CONNECTING**, or **CONNECTED**) and the _ssid_ name for
    the current connection on the wifi device.

  * _connect()_

    Input: _ssid_, _password_

    Output: None

    Delete any existing connection for _ssid_, create a new connection, and
    attempt to connect to it. The password may be a zero length string if
    not needed.

  * _delete_connection()_

    Input: _ssid_

    Output: None

    Delete the connection for _ssid_. The system will not be able to reconnect
    using this connection.

## COPYRIGHT

Comitup is Copyright (C) 2016-2019 David Steele &lt;steele@debian.org&gt;.

## SEE ALSO

comitup-conf(5), comitup-cli(8), comitup-web(8)
