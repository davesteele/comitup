
from typing import List

NM_DEVICE_STATE_ACTIVATED: int
NM_DEVICE_STATE_FAILED: int
NM_DEVICE_STATE_DISCONNECTED: int

class NMDbusInterfaceType(type): ...

class NMDbusInterface(object): ...

class Device(NMDbusInterface):
    DeviceType: int
    Interface: str

class Wireless(Device): ...

class NetworkManager(NMDbusInterface):
    @staticmethod
    def GetDevices() -> List[Device]: ...
