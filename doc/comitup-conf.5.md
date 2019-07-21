% comitup-conf(5)
%
% February 2019

# NAME

comitup.conf -- Comitup configuration file format

## DESCRIPTION

The _comitup.conf_ file configures the wifi management service comitup(8).
It is located in the _/etc/_ directory.

## PARAMETERS

  * _ap_name_:
    By default, comitup will create a hotspot named **comitup-&lt;nn&gt;**, and publish
    avahi-daemon(8) host entries for **comitup-&lt;nn&gt;** and **comitup**. Setting this
    entry will change the **comitup** string with one of the users choosing. If the
    configuration variable contains an &lt;nn&gt; string, with one to 4 "n's", it will be
    replaced with a persistent, random number. Similarly, the string &lt;hostname&gt; is
    replaced with the computer's hostname.

  * _ap_password_:
    If this parameter is defined in the configuration file, then the comitup hotspot will
    require that any connection to the hotspot be authenticated, using this password.

  * _web_service_:
    This defines a user web service to be controlled by **comitup**. This service will be
    disabled in the **HOTSPOT** state in preference of the comitup web service, and will be
    enabled in the **CONNECTED** state. This should be the name of the systemd web service,
    such as _apache2.service_ or _nginx.service_. This defaults to a null string,
    meaning no service is controlled.

  * _enable_appliance_mode_:
    By default, comitup will use multiple wifi interfaces, if available, to connect to the
    local hotspot and to the internet simultaneously. Setting this to something other than
    "true" will limit comitup to the first wifi interface.

  * _external_callback_:

    The path to an external script that is called on comitup state changes. It will include
    a single argument, either 'HOTSPOT', 'CONNECTING', or 'CONNECTED'. The script will run
    as the owning user and group.

  * _primary_wifi_device_;

    Override the default choice for the primary WiFi device to use.

## COPYRIGHT

Comitup is Copyright (C) 2016-2019 David Steele &lt;steele@debian.org&gt;

## SEE ALSO

comitup(8), comitup-cli(8), comitup-web(8)

