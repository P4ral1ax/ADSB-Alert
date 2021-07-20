"""
Helps create adsb dataclass
"""
from adsb_dataclass import *
from adsb_parse import *

# Create a new device from Scratch
# Throws excpetion ValueError
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
   
    # Create the new Object
    new_object = Aircraft(callsign, name, last_time, lat, lon, alt, speed, heading, device_key)

    # Verify not Missing essential data
    # Raises Exception
    verify_data(new_object)

    # print(f"Created New Device {d.name}")

    return(new_object)


# Update existing device
def update_device(device, resp):
    # Parse API response into dictionary of data
    d = parse_object(resp)

    # Save original if updated data is invalid
    device_original = device

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
    
    # If updated Data is missing values -> Ignore
    try:
        verify_data(device)
    except ValueError:
        return(device_original)

    return(device)


# Verifys that data exists
# Throws ValueError
def verify_data(device):
    if device.last_time == None:
        raise ValueError("Missing Last Time")
    if device.lon == None or device.lat == None:
        raise ValueError("Missing Coordinates")
    if device.name == None:
        raise ValueError("Missing Name")
    if device.alt == None:
        raise ValueError("Missing Altitude")
    return(True)
    

        