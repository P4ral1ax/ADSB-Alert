"""
Helps create adsb dataclass
"""
from adsb_dataclass import *
from adsb_parse import *

# Create a new device from Scratch
def make_device(resp):
    # Parse API response into dictionary of data
    d = parse_object(resp)
    
    # Assign all the data to object
    callsign    = d.get("callsign")
    name        = d.get("name")
    last_time   = d.get("last_time")
    lat         = d.get("lat")
    lon         = d.get("lon")
    alt         = d.get("alt")
    speed       = d.get("speed")
    heading     = d.get("heading")
    device_key  = d.get("device_key")
   
    # print(f"Created New Device {d.name}")

    return(Aircraft(callsign, name, last_time, lat, lon, alt, speed, heading, device_key))

# Update existing device
def update_device(device, resp):
    # Parse API response into dictionary of data
    d = parse_object(resp)

    # Assign all the data to object
    device.callsign    = d.get("callsign")
    device.name        = d.get("name")
    device.last_time   = d.get("last_time")
    device.lat         = d.get("lat")
    device.lon         = d.get("lon")
    device.alt         = d.get("alt")
    device.speed       = d.get("speed")
    device.heading     = d.get("heading")
    device.device_key  = d.get("device_key")
    
    # print(f"Updated {device.name}")

    return()