"""
Parses API response into usable data
"""
import json

# Parses dataclass
def parse_object(resp):

    # Load Response Data
    data = json.loads(resp.text)
    
    # Create Dictionary to give to dataclass
    device_data = {}

    # Get All Location Data
    base_location = data.get("kismet.device.base.location")
    location_last = base_location.get("kismet.common.location.last")
    geopoint      = location_last["kismet.common.location.geopoint"]
    device_data["lat"]      = geopoint[0]
    device_data["lon"]      = geopoint[1]
    device_data["alt"]      = location_last["kismet.common.location.alt"]
    device_data["speed"]    = location_last["kismet.common.location.speed"]
    device_data["heading"]  = location_last["kismet.common.location.heading"]

    # Get Callsign
    rtladsb_device = data.get("rtladsb.device")
    device_data["callsign"]     = rtladsb_device["rtladsb.device.callsign"]

    # Get Other Values
    device_data["name"]         = data.get("kismet.device.base.name")
    device_data["last_time"]    = data.get("kismet.device.base.last_time")
    device_data["device_key"]   = data.get("kismet.device.base.key")
    
    # Return to create Dataclass
    return(device_data)
