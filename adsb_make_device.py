"""
Helps create adsb dataclass
"""
from adsb_dataclass import *
from adsb_parse import *

def make_device(resp):
    d = parse_object(resp)

    callsign    = d.get("callsign")
    name        = d.get("name")
    last_time   = d.get("last_time")
    lat         = d.get("lat")
    lon         = d.get("lon")
    alt         = d.get("alt")
    speed       = d.get("speed")
    heading     = d.get("heading")
    device_key  = d.get("device_key")
   
    return(Aircraft(callsign, name, last_time, lat, lon, alt, speed, heading, device_key))
