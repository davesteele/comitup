from typing import Any, Dict, List

import dbus

NM_DEVICE_STATE_ACTIVATED: int
NM_DEVICE_STATE_FAILED: int
NM_DEVICE_STATE_DISCONNECTED: int
NM_DEVICE_STATE_REASON_NO_SECRETS: int

class ObjectVanished(Exception): ...
class NMDbusInterfaceType(type): ...

class NMDbusInterface(object):
    object_path: dbus.ObjectPath

class Device(NMDbusInterface):
    DeviceType: int
    Interface: str
    Ip4Address: str
    ActiveConnection: Connection
    @staticmethod
    def SpecificDevice() -> Device: ...
    @staticmethod
    def Disconnect() -> None: ...
    @staticmethod
    def GetAllAccessPoints() -> List[AccessPoint]: ...
    class Ip4Config:
        Addresses: List[List[str]]
    class Ip6Config:
        Addresses: List[List[str]]

class Wireless(Device): ...

class NetworkManager(NMDbusInterface):
    State: int
    @staticmethod
    def GetDevices() -> List[Device]: ...
    @staticmethod
    def ActivateConnection(
        connection: Connection, dev: Device, path: str
    ) -> Connection: ...
    @staticmethod
    def DeactivateConnection(connection: Connection) -> Connection: ...

class Settings(NMDbusInterface):
    @staticmethod
    def ListConnections() -> List[Connection]: ...
    @staticmethod
    def ReloadConnections() -> None: ...
    @staticmethod
    def AddConnection(settings: Dict[str, Any]) -> None: ...

class Connection(NMDbusInterface):
    uuid: str
    Connection: Any
    @staticmethod
    def Delete() -> None: ...
    @staticmethod
    def GetSettings() -> Dict[str, Any]: ...

class AccessPoint(NMDbusInterface):
    Strength: int
    Ssid: str
    Flags: int
    WpaFlags: int
    RsnFlags: int
