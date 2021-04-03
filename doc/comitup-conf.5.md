% comitup-conf(5)
%
% March 2021

# NAME

comitup.conf -- Comitup configuration file format

## DESCRIPTION

The _comitup.conf_ file configures the wifi management service comitup(8).
It is located in the _/etc/_ directory.

## PARAMETERS

  * _ap_name_:
    By default, comitup will create a hotspot named **comitup-&lt;nnn&gt;**,
    publish an avahi-daemon(8) host entry for **comitup-&lt;nnn&gt;**, and establish
    an mdns identity for **comitup-&lt;nnn&gt;.local**.  Setting this parameter will
    change the **comitup** string with one of the users choosing. 

    * There are three options for creating a unique identifier, the length of which is
      determined by the number of letters,
      * <n...> Random (persisted) number, 1-4 n's
      * <M...> RPi wlan0 MAC address, 1-12 M's
      * <s...> RPi Serial Number, 1-16 s's
      * Note that only one unique identifier is allowed

    * Similarly, the string &lt;hostname&gt; is replaced with the computer's hostname.
    * The unique identifier may appear anywhere in the name, for example,
      * rasp-\<nnn\>, \<MMMMMM\>RPi, \<hostname\>-\<ssss\> 

  * _ap_password_:
    If this parameter is defined in the configuration file, then the comitup hotspot will
    require that any connection to the hotspot be authenticated, using this password.

  * _web_service_:
    This defines a user web service to be controlled by **comitup**. This service will be
    disabled in the **HOTSPOT** state in preference of the comitup web service, and will be
    enabled in the **CONNECTED** state. This should be the name of the systemd web service,
    such as _apache2.service_ or _nginx.service_. This defaults to a null string,
    meaning no service is controlled.

  * _service_name_:
    This defines the mdns service name advertised by **comitup**. This defaults to "comitup",
    and will be advertised as "_comitup._tcp".

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

comitup(8), comitup-cli(1), comitup-web(8)

