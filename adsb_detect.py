# Testing REST API from Kismet
from adsb_parse import *
import requests
import json
import adsb_dataclass
import adsb_make_device
import configparser
import time

kismet_ip="192.168.1.252"
api_base_url=f"http://{kismet_ip}:2501"


# # Test Fuctions 
# def test_query(key):
#     # Just a test query for system information
#     # Returns : HTML response code (str)
#     url = f"{api_base_url}/system/status.json"
#     result = requests.get(url, cookies=key)
#     print(result)

# def test_dataclass(key, device_id):
#     path = f"/devices/by-key/{device_id}/device.json"
#     resp = get_request(key, path)
#     device = adsb_make_device.make_device(resp)
#     return(device)


#
# Updates Existing Devices and Adds new Devices
#
def update_devices(devices_dict, devices, key):
    for i in range(len(devices)):
        d = devices[i]

        # Get Info Once for Device ID
        resp = get_device_info(key, d)

        # If exists, update info. Else create new object and add to dictionary
        if d in devices_dict.keys():
            # Update object with using callsign to grab from dictionary
            adsb_make_device.update_device(devices_dict.get(d), resp)
        else: 
            device_new = adsb_make_device.make_device(resp)
            print(f"Found New Device : {d} : {device_new.name}")
            devices_dict[d] = device_new

    # Return dictionary after all objects updated
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


#
# Gets the current timestamp
#
def get_timestamp(key):
    # Get the current timestamp from Kismet
    # Returns : Timstamp (str)
    time_resp = get_request(key, "/system/timestamp.json")
    timestamp = json.loads(time_resp.text)
    timestamp_sec = timestamp.get("kismet.system.timestamp.sec")
    return(timestamp_sec)

#
# All "get" requests go through this command
#
def get_request(key, url_path):
    # Uses API key and Path to do a request
    # Returns : The object result (str)
    url = f"{api_base_url}{url_path}"
    result = requests.get(url, cookies=key)
    return(result)



#
# Main Function
#
def main():
    # Read API Key from designated file
    print("\nReading API Key...")
    f = open("config.txt", "r")
    api_key = f.read() 
    print(f"Key Found : {api_key[0:5]}******************")

    # Requests requires Dictionary Format for Cookies
    print(f"Creating Key Dictionary...")
    key_dict = {"KISMET": api_key}
    
    # Print Timestamp
    print("\n*** Starting ***")

    ### Main Loop ###
    device_dict = {}
    try:
        while True:
            # Get Timstamp
            curr_time = get_timestamp(key_dict)
            print(f"Current Timestamp : {curr_time}")

            # Look at all active devices (Last 30m)
            time_limit = str(int(curr_time) - 1800)
            resp = get_devices(key_dict, time_limit)
            new_device_list = parse_all_devices(resp)

            # Update Device Dictionary with new list
            device_dict = update_devices(device_dict, new_device_list, key_dict)
            
            time.sleep(10)
    except KeyboardInterrupt:
        print('Program Interrupted... Exiting')





    # # Test Dataclasses
    # print("Testing Dataclass Creation...")
    # test_device = test_dataclass(key_dict, "C026A0800000000_60501C32F1F")
    # print("Created Dataclass...")
    # print(test_device)
    

main()


