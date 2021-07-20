import adsb_parse
import requests
import json
import adsb_dataclass
import adsb_make_device
import configparser
import datetime
import time

KISMET_IP="192.168.1.252"
API_BASE_URL=f"http://{KISMET_IP}:2501"
TIME_LIMIT_INTERVAL=360


## Print all Devices ##
def show_all_devices(devices_dict):
    counter = 0
    for device in devices_dict:
        print("-----------------------------------")
        print(f"Callsign : {devices_dict[device].callsign}\nHeading : {devices_dict[device].heading}\nSpeed: {devices_dict[device].speed}\nAltitude : {devices_dict[device].alt}")
        if (counter == 5):
            break
        counter = counter + 1


## Updates Existing Devices and Adds new Devices ##
def update_devices(devices_dict, devices, key):

    # Go through entire list of devices
    for i in range(len(devices)):
        d = devices[i]

        # Get Info Once for Device ID
        resp = get_device_info(key, d)

        # If exists, update info. Else create new object and add to dictionary
        if d in devices_dict.keys():
            # Update object using device ID to grab from dictionary
            device_updated = adsb_make_device.update_device(devices_dict.get(d), resp)
            devices_dict[d] = device_updated
        else:
            try:  
                # Add new device with the device ID being the key in the dictionary
                device_new = adsb_make_device.make_device(resp) # Throws ValueError
                time_convert = datetime.datetime.fromtimestamp(int(get_timestamp(key)))
                devices_dict[d] = device_new
                print(f"New Device : {d} | {device_new.name} |  {time_convert} | {len(devices_dict)} Devices")
            # Missing Data : Ignore
            except AttributeError:
                pass
            # Missing Essential Data : Skip Device
            except ValueError as err:
                print(f"{d} : {err.args}")


    # Return dictionary after all objects updated
    return(devices_dict)


## Cleans out Old Devices ##
def filter_devices(key, devices_dict):
    # Get the current timestamp
    timestamp = int(get_timestamp(key))
    # For each key in the Dictionary
    for i in list(devices_dict):
        device = devices_dict[i]
        # If the last seen is older than the search interval then delete
        # Might Need Try Statement? Data is verified so this shouldnt be an issue
        if ((timestamp - device.last_time) > TIME_LIMIT_INTERVAL):
            del devices_dict[i]
            print(f"Deleted {i} | {device.name} | Last Seen {timestamp - device.last_time} Sec Ago | {len(devices_dict)} Devices")
        else:
            pass
    return(devices_dict)

    
## Gets the Device Info API Response ##
def get_device_info(key, device_id):
    path = f"/devices/by-key/{device_id}/device.json"
    resp = get_request(key, path)
    return(resp)


## Gets the list of ADS-B devices in specified timeframe ##
def get_devices(key, timestamp):
    path = f"/devices/views/phy-RTLADSB/last-time/{timestamp}/devices.json"
    resp = get_request(key, path)
    return(resp)


## Gets the current timestamp ##
def get_timestamp(key):
    # Get the current timestamp from Kismet
    # Returns : Timstamp (str)
    time_resp = get_request(key, "/system/timestamp.json")
    timestamp = json.loads(time_resp.text)
    timestamp_sec = timestamp.get("kismet.system.timestamp.sec")
    return(timestamp_sec)


## All "get" requests go through this command ##
def get_request(key, url_path):
    # Uses API key and Path to do a request
    # Returns : The object result (str)
    url = f"{API_BASE_URL}{url_path}"
    result = requests.get(url, cookies=key)
    return(result)


def parse_config(file):
    pass

## Main Function ##
def main():
    # Read API Key from designated file
    print("\nReading API Key...")
    f = open("config.txt", "r")
    api_key = f.read() 
    print(f"Key Found : {api_key[0:5]}******************")

    # Requests requires Dictionary Format for Cookies
    print(f"Creating Key Dictionary...")
    key_dict = {"KISMET": api_key}
    
    # Enter Loop
    print("\n*** Starting ***")

    ### Main Loop ###
    device_dict = {}
    try:
        while True:
            # Get Timstamp
            curr_time = get_timestamp(key_dict)
            # print(f"Current Timestamp : {curr_time}")

            # Look at all active devices (Last 30m) TODO - Make Adjustable in Config
            time_limit = str(int(curr_time) - TIME_LIMIT_INTERVAL)
            resp = get_devices(key_dict, time_limit)
            new_device_list = adsb_parse.parse_all_devices(resp)

            # Update Device Dictionary with new list
            device_dict = update_devices(device_dict, new_device_list, key_dict)
            # Clean Old Devices
            device_dict = filter_devices(key_dict, device_dict) # -> Just gives dictionary changed size suring iteration
            
            time.sleep(10)

            #  Print Devices
            # show_all_devices(device_dict)

    except KeyboardInterrupt:
        print('Program Interrupted... Exiting')


main()

# TODO - Add "cleanup" function to remove Out of Range or Old Devices OR Make seperate dictionary
# TODO - Setup configuration file for IP, Time Range, Base URL, Other options - > Config Parser
# TODO - Geo + Trajcetory Detection https://geopy.readthedocs.io/en/stable/#module-geopy.distance
# TODO - Takeoff detection
# TODO (DONE) - Ignore devices with missing or nonetype data in important fields (last_time, name, coordinates, heading) - Use Exeptions