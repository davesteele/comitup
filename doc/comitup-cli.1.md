% comitup-cli(1)
%
% Aug 2021

# NAME

comitup-cli -- command-line interface for comitup network management

## SYNOPSIS

    $ `comitup-cli [cmd ...]`
    
    State: HOTSPOT
    Connection: hotspot-123
    Points:
        1: MyAccessPoint
        2: HisAccessPoint
    Available Commands:
        (r)eload
        (q)uit
        connect to (<n>)
        [l]ocate the device
        [x] Factory reset (no warning)
    command?:

## DESCRIPTION

The **comitup-cli** utility provides access to the comitup(8) D-Bus interface.
It is intended to serve as a debug tool, and a source code example for
connecting to the interface.

If an argument is provided, a one-shot command is attempted. Oherwise, the
program goes into an interpretive mode.

If the comitup(8) service is not running, **comitup-cli** will immediately exit.

## Command-Mode Display:

  * **State**

    The **comitup** states are **HOTSPOT**, **CONNECTING**, and **CONNECTED**. 

    In the **HOTSPOT** mode, **comitup** creates a wifi hotspot with the
    name **comitup-&lt;nnn&gt;**, where &lt;nnn&gt; is a persistent number.

    Once in **HOTSPOT** mode, the system will occasionally (~3 min) cycle
    through available defined connections, by transitioning to the
    **CONNECTING** mode. The Access Point list is updated by this process.
    Any command issued by **comitup-cli** will cause the next
    timeout instance to be skipped.

    If any other devices are connected to the Comitup hotspot, the periodic
    attempt is skipped, to avoid interrupting service to those devices.

    Once a connection is established, the system will be in the **CONNECTED**
    mode. If the connection is lost, failed, or deleted, the system will
    transition back to the **HOTSPOT** state.

  * **Connection**

    The `ssid` of the current active connection.

  * **Points**

    While in the **HOTSPOT** mode, **comitup-cli** will list the
    currently-visible access points, by `ssid`. Access points with the
    strongest signal are sorted to the top of the list. The entries are
    numbered, for use with the __connect__ command.

## Commands

  * __r__ - **Reload**

    Refresh the displayed state, mode, and list of access points.

  * __q__ - **Quit**

    Exit **comitup.cli**.

  * __d__ - **Delete connection**

    Delete the configuration information for the current wifi connection.
    This will cause **comitup** to transition to the **HOTSPOT** mode. 

    This command is not available in the **HOTSPOT** mode.

  * __&lt;n&gt;__ - **Connect to access point &lt;n&gt;**

    Define a connection for the selected access point, and then attempt to
    connect.

    This command is only available in the **HOTSPOT** mode.

  * __m__ - **Manual connection**

    Enter an SSID manually.

  * __i__ - **Get information**

    Return the comitup version and host name for the current instance.

  * __l__ - **Locate**

    Locate the headless Raspberry Pi running Comitup by blinking the front
    green LED once.

  * __n__ - **reName**

    Change the name of the host, Comitup ap_name, and comitup mdns domain name.
    This also adds an entry in 'hosts'. This causes Comitup to restart, and the
    cli session to end.

  * __x__ - **Factory Reset**

    Remove all defined WiFi connections, and restart the service. There is no
    confirmation requested. This will terminate the interpreter session. Note
    that _enable_nuke_ must be enabled in _comitup.conf_ for this to succeed.

## COPYRIGHT

Comitup is Copyright (C) 2016-2019 David Steele &lt;steele@debian.org&gt;

## SEE ALSO

comitup(8), comitup-conf(5), comitup-web(8), comitup-watch(1)

