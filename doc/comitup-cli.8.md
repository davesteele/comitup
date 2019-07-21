% comitup-cli(8)
%
% February 2019

# NAME

comitup-cli -- command-line interface for comitup network management

## SYNOPSIS

    $ `comitup-cli`
    
    State: HOTSPOT
    Connection: hotspot-1234
    Points:
        1: MyAccessPoint
        2: HisAccessPoint
    Available Commands:
        (r)eload
        (q)uit
        connect to (<n>)
    command?:

## DESCRIPTION

The **comitup-cli** utility provides access to the comitup(8) D-Bus interface.
It is intended to serve as a debug tool, and a source code example for
connecting to the interface.

If the comitup(8) service is not running, **comitup-cli** will immediately exit.

Display:

  * **State**

    The **comitup** states are **HOTSPOT**, **CONNECTING**, and **CONNECTED**. 

    In the **HOTSPOT** mode, **comitup** creates a wifi hotspot with the
    name **comitup-&lt;nn&gt;**, where &lt;nn&gt; is a persistent 2-digit number.

    Once in **HOTSPOT** mode, the system will occasionally (~1/min) cycle
    through available defined connections, by transitioning to the
    **CONNECTING** mode. The Access Point list is updated by this process.
    Any command issued by **comitup-cli** will cause the next
    timeout instance to be skipped.

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

Commands:

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

## COPYRIGHT

Comitup is Copyright (C) 2016-2019 David Steele &lt;steele@debian.org&gt;

## SEE ALSO

comitup(8), comitup-conf(5), comitup-web(8)

