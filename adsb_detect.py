# Testing REST API from Kismet
import requests
import json
import adsb_dataclass
import adsb_make_device
import configparser

kismet_ip="192.168.1.252"
api_base_url=f"http://{kismet_ip}:2501"


# # Test Fuctions 
# def test_query(key):
#     # Just a test query for system information
#     # Returns : HTML response code (str)
#     url = f"{api_base_url}/system/status.json"
#     result = requests.get(url, cookies=key)
#     print(result)

def test_dataclass(key, device_id):
    path = f"/devices/by-key/{device_id}/device.json"
    resp = get_request(key, path)
    device = adsb_make_device.make_device(resp)
    return(device)




def get_timestamp(key):
    # Get the current timestamp from Kismet
    # Returns : Timstamp (str)
    time_resp = get_request(key, "/system/timestamp.json")
    timestamp = json.loads(time_resp.text)
    timestamp_sec = timestamp.get("kismet.system.timestamp.sec")
    return(timestamp_sec)


def get_request(key, url_path):
    # Uses API key and Path to do a request
    # Returns : The object result (str)
    url = f"{api_base_url}{url_path}"
    result = requests.get(url, cookies=key)
    return(result)


def main():
    # Read API Key from designated file
    print("\nReading API Key...")
    f = open("config.txt", "r")
    api_key = f.read() 
    print(f"Key Found : {api_key[0:5]}******************")

    # Requests requires Dictionary Format for Cookies
    print(f"Creating Key Dictionary...")
    key_dict = {"KISMET": api_key}
    
    print("\n*** Starting ***")
    curr_time = get_timestamp(key_dict)
    print(f"Current Timestamp (Epoch) : {curr_time}")

    print("Testing Dataclass Creation...")
    test_device = test_dataclass(key_dict, "C026A0800000000_60501C32F1F")
    print("Created Dataclass...")
    print(test_device)
    

main()


