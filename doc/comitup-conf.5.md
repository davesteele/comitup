% comitup-conf(5)
%
% July 2021

# NAME

comitup.conf -- Comitup configuration file format

## DESCRIPTION

The _comitup.conf_ file configures the wifi management service comitup(8).
It is located in the _/etc/_ directory.

## PARAMETERS

  * _ap\_name_:
    By default, comitup will create a hotspot named **comitup-&lt;nnn&gt;**,
    publish an avahi-daemon(8) host entry for **comitup-&lt;nnn&gt;**, and establish
    an mdns identity for **comitup-&lt;nnn&gt;.local**.  Setting this parameter will
    change the **comitup** string with one of the users choosing. If the
    configuration variable contains an &lt;nnn&gt; string, with between one and four "n's", it
    will be replaced with a persistent, random number. Similarly, the string
    &lt;hostname&gt; is replaced with the computer's hostname.

    For the Avahi Service Discovery publication to work correctly, the name
    should be ASCII, with no special characters or white space.

  * _ap\_password_:
    If this parameter is defined in the configuration file, then the comitup hotspot will
    require that any connection to the hotspot be authenticated, using this password.

  * _web\_service_:
    This defines a user web service to be controlled by **comitup**. This service will be
    disabled in the **HOTSPOT** state in preference of the comitup web service, and will be
    enabled in the **CONNECTED** state. This should be the name of the systemd web service,
    such as _apache2.service_ or _nginx.service_. This defaults to a null string,
    meaning no service is controlled.

  * _service\_name_:
    This defines the mdns service name advertised by **comitup**. This defaults to "comitup",
    and will be advertised as "_comitup._tcp".

  * _enable\_appliance\_mode_:
    By default, comitup will use multiple wifi interfaces, if available, to connect to the
    local hotspot and to the internet simultaneously. Setting this to something other than
    "true" will limit comitup to the first wifi interface.

  * _external\_callback_:

    The path to an external script that is called on comitup state changes. It will include
    a single argument, either 'HOTSPOT', 'CONNECTING', or 'CONNECTED'. The script will run
    as the owning user and group.

  * _primary\_wifi\_device_;

    Override the default choice for the primary WiFi device to use.

  * _verbose_:

    Set to '1' (or 'yes' or 'true') to enable more verbose logging.

  * _enable\_nuke_:

    Set to '1' (or 'yes' or 'true') to enable a hardware-based factory reset
    function. This will cause all WiFi connection settings to be deleted. On a
    Raspberry Pi, short out pins 39 and 40 on the GPIO header for three seconds
    to invoke. The green LED will flash three times to indicate success.

    This capability is also availble via _comitup-cli_ and the D-BUS interface.

  * _ipv6\_link\_local_;

    Set to '1' to force Comitup to create only "link-local" IPv6 addresses for
    the upstream WiFi connection, affording a higher level of protection for
    that link. "link-local" addresses cannot route to the Internet. Delete
    existing connections after changing the value of this parameter.

## COPYRIGHT

Comitup is Copyright (C) 2016-2021 David Steele &lt;steele@debian.org&gt;

## SEE ALSO

comitup(8), comitup-cli(1), comitup-web(8)

