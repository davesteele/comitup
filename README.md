# Comitup 
 Pronounced (COMM-it-up)

This module is intended to support managing NetworkManager Wifi connections.
It will evenutually support the ability to bootstrap Wifi support over Wifi.

This makes heavy use of the Python [NetworkManager] module. The NetworkManager
 DBus [specification] includes detail on how to call the DBus functions.

[NetworkManager]: http://pythonhosted.org/python-networkmanager/
[specification]: https://developer.gnome.org/NetworkManager/unstable/spec.html

## Usage

	# python nm.py -h
	usage: comitup [-h] command [arg]
	
	Manage NetworkManager Wifi connections
	
	positional arguments:
	  command     command
	  arg         command argument
	
	optional arguments:
	  -h, --help  show this help message and exit
	
	Commands:
	  delconnection - Delete a connection id'd by ssid
	  detailconnection - Print details about a connection
	  getconnection - Print the active connection ssid
	  getip - Print the current IP address
	  listaccess - List all accessible access points
	  listconnections - List all defined connections
	  makeconnection - Create a connection for a visible access point, for future use
	  makehotspot - Create a hotspot connection for future use
	  setconnection - Connect to a connection


