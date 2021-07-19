"""
Parses API response into usable data
"""
import json

# Parses response into Dictionary of usefull data
def parse_object(resp):

    # Load Response Data
    data = json.loads(resp.text)
    
    # Create Dictionary to give to dataclass
    device_data = {}
    try: 
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
        
        # Return dictionary
        return(device_data)
    except AttributeError:
        # Missing Data : Ignore
        return({})

# Parse the response for all ADS-B devices
# Return All Devices Kismet IDs in a list
def parse_all_devices(resp):
    list_devices = []
    devices = json.loads(resp.text)
    for device in devices:
        list_devices.append(device.get("kismet.device.base.key"))
    return(list_devices)


# Just get the callsign of a device ID
def get_callsign(resp):
    data = json.loads(resp.text)

    # Get Callsign
    rtladsb_device = data.get("rtladsb.device")
    callsign = rtladsb_device["rtladsb.device.callsign"]

    return(callsign)