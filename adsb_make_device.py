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
    new_object = Aircraft(callsign, name, last_time, lat, lon, alt, speed, heading, device_key, last_alert=0)

    # Verify not Missing essential data
    # Raises Exception
    verify_data(new_object)

    # print(f"Created New Device {d.name}")

    return(new_object)


# Update existing device
# Throws exception
def update_device(device, resp):
    # Parse API response into dictionary of data
    d = parse_object(resp)

    # Checking for diff in message
    device_original_last = device.last_time

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
    
    # Print if Data actually Updates
    # if device.last_time != device_original_last:
    #     print(f"Updated {device.name} | Prev lon : {device_original_last} | New lon {device.last_time}")
    
    # If updated Data is missing values : Throw Exception
    try:
        verify_data(device)
    except ValueError:
        print(f"{device} : Missing Data, Not Updating")
        return()

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

# Update the last alert time to the last time device was seen
# If device doesn't update last time then device wont switch alert status
def update_last_alert(device):
    device.last_alert = device.last_time
    return(device)
