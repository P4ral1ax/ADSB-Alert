"""
The dataclass descriptions for each aircraft
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Aircraft:
    __slots__ = ["callsign", "name", "last_time", "lat", "lon", "alt", "speed", "heading", "device_key"]
    
    callsign    : str   # rtladsb.device.callsign 
    name        : str   # kismet.device.base.name
    last_time   : int   # kismet.device.base.last_time
    lat         : float # kismet.device.base.location -> Kismet.common.location.last -> kismet.common.location.geopoint -> 0
    lon         : float # kismet.device.base.location -> Kismet.common.location.last -> kismet.common.location.geopoint -> 1
    alt         : float # kismet.device.base.location -> Kismet.common.location.last -> kismet.common.location.alt
    speed       : float # kismet.device.base.location -> Kismet.common.location.last -> kismet.common.location.speed
    heading     : float # kismet.device.base.location -> Kismet.common.location.last
    device_key  : str   # kismet.device.base.key

