from requests.adapters import HTTPAdapter, MaxRetryError
from requests.packages.urllib3.util.retry import Retry
from urllib3.exceptions import NewConnectionError
from requests.exceptions import Timeout
import requests.exceptions
import adsb_parse
import requests
import json
import adsb_make_device
import adsb_detect
import configparser
import datetime
import time

KISMET_IP=""
TIME_LIMIT_INTERVAL=600
REFRESH_WAIT=10

## Send Alerts to Kismet + Devices ##
def send_alert(key, msg):
    pass


## Check If Kismet Brokey & Block if so ##
def check_kismet_status(key):
    while True:
        try:
            # If can get the API status -> Assume API Functional
            url = (f"http://{KISMET_IP}:2501/system/status.json")
            requests.get(url, cookies=key, timeout=1)
            return()
        # Catch any timeout or request Exception -> API Brokey
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(f"Unable to Connect to API : Retrying Connection : {datetime.datetime.now()}")
            time.sleep(10)
        except Timeout:
            print(f"API Timed Out : Retrying Connection : {datetime.datetime.now()}")
            time.sleep(10)


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
        try:
            resp = get_device_info(key, d) 
        except Exception:
            print(f"{d} | Failed to get Information, Skipping")
            break

        # If exists, update info. Else create new object and add to dictionary
        if d in devices_dict.keys():
            try: 
                # Update object using device ID to grab from dictionary
                # Skip if missing important data
                device_updated = adsb_make_device.update_device(devices_dict.get(d), resp) # Throws exception
                devices_dict[d] = device_updated
            except ValueError as err:
                print("Update Missing Data : Ignoring")
            except Timeout as err:
                print("Update Failed : Ignoring")
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
                # print(f"{d} : {str(err)}")
                pass
            # Request Couldn't complete
            except Exception as err:
                # Add function to wait until kismet is back
                pass


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
# Throws Exceptions (RequestException, Timeout)
def get_device_info(key, device_id):
    path = f"/devices/by-key/{device_id}/device.json"

    # Try to get device Data
    try:
        resp = get_request(key, path)
    except requests.exceptions.RequestException:
        print(f"{device_id} | Reached Max Retries...")
        raise Timeout
    except Timeout:
        print(f"{device_id} | Request Timed Out...")
        raise Timeout
    except Exception:
        print(f"Connection Refused...")
        raise Timeout
        
    # Return Result
    return(resp)


## Gets the list of ADS-B devices in specified timeframe ##
def get_devices(key, timestamp):
    path = f"/devices/views/phy-RTLADSB/last-time/{timestamp}/devices.json"
    # Get device list ## Throws Exceptions
    resp = get_request(key, path)
    return(resp)


## Gets the current timestamp ##
def get_timestamp(key):
    # Get the current timestamp from Kismet
    # Returns : Timstamp (str)
    try:
        time_resp = get_request(key, "/system/timestamp.json")
        timestamp = json.loads(time_resp.text)
        timestamp_sec = timestamp.get("kismet.system.timestamp.sec")
        return(timestamp_sec)
    except Exception:
        print("Request Failed. Using Local Time")
        return(str(round(time.time())))


## All "get" requests go through this command ##
# Throws Exception MaxRetryError
# Throws Exception Timeout
def get_request(key, url_path):
    # Uses API key and Path to do a request
    # Returns : The object result (str)

    # Define args for HTTP Adapter  
    retry_strategy = Retry(
        total=3,  # 3 Retries
        status_forcelist=[400, 401, 403, 404, 429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )

    # Create HTTP session adapter
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.session()
    http.mount("http://", adapter)

    # Try Request 
    ## THROWS EXCEPTION MaxRetryError ##
    url = f"{API_BASE_URL}{url_path}"
    # print(f"Get : {url}")
    result = http.get(url, cookies=key, timeout=1)
    return(result)
    

## Read Configuration File and Set Values ##
def parse_config(file):
    # Remind Python that they are infact Global variables
    global KISMET_IP
    global REFRESH_WAIT
    global TIME_LIMIT_INTERVAL

    # Parse Config File for Settings
    parser = configparser.ConfigParser()
    parser.read(file)
    KISMET_IP = parser.get('Config', 'KismetIP')
    REFRESH_WAIT = int(parser.get('Config', 'Refresh'))
    TIME_LIMIT_INTERVAL = int(parser.get('Config', 'DeviceLife'))
    key = parser.get('Config', 'APIKey')

    # Remind Python that the IP goes in the URL
    global API_BASE_URL
    API_BASE_URL=f"http://{KISMET_IP}:2501"

    # Return Key (Don't Save as Global Variable)
    return(key)


## Main Function ##
def main():
    # Read Config File
    try:
        api_key = parse_config("config.txt") 
    except:
        print("Missing or Incorrect Configuration File. Exiting.")
        quit()
    print(f"\nKey Found : {api_key[0:5]}******************")
    print(f"Kismet IP : {KISMET_IP}")
    print(f"Refresh Rate : {REFRESH_WAIT}")
    print(f"Device Life : {TIME_LIMIT_INTERVAL}")

    # Requests requires Dictionary Format for Cookies
    key_dict = {"KISMET": api_key}
    
    # Enter Loop
    print("\n*** Starting ***")
    ### Main Loop ###
    device_dict = {}
    try:
        while True:
            # print(f"--Loop-- | {datetime.datetime.now()}") 
            # Check Kismet Status (Is It Up?)
            # Block until back up
            check_kismet_status(key_dict)

            # Get Timstamp
            curr_time = get_timestamp(key_dict)
            # print(f"--Timestamp-- | {datetime.datetime.now()}")
            # print(f"Current Timestamp : {curr_time}")

            
            try:
                # Look at all active devices (Last 30m)
                time_limit = str(int(curr_time) - TIME_LIMIT_INTERVAL)
                resp = get_devices(key_dict, time_limit)
                new_device_list = adsb_parse.parse_all_devices(resp)

                # Update Device Dictionary with new list
                device_dict = update_devices(device_dict, new_device_list, key_dict)
                # Clean Old Devices
                device_dict = filter_devices(key_dict, device_dict) # -> Just gives dictionary changed size suring iteration

                # Detect Takeoff
                device_dict = adsb_detect.detect_landings(device_dict)
           
                # Detect Landing
                adsb_detect.detect_takeoff(device_dict)
            except Exception:
                print("Somthing Failed, Skipping Loop")
                pass

            # Wait for set refresh time
            time.sleep(REFRESH_WAIT)

    # Catch ctrl + c and be like "ok sure whatever"
    except KeyboardInterrupt:
        print('Program Interrupted... Exiting')


main()


## Part 1 - Detection
# TODO - Add ICAO To Dataclass
# TODO - Takeoff detection  
# TODO - Make Dashboard  |  https://pusher.com/tutorials/live-dashboard-python/
# TODO - Fix Config Workflow
# TODO - Tune Alerting
# TODO - Add Better bad Request Handling

## Part 2 - Trends 
# TODO - Log All times a Device is Seen (Use ICAO as Key)
# TODO - Log All Detections (Type + ICAO)
# TODO - Device trends by all or single device (by device or all)
# TODO - Trends of Detections
# TODO - Detect Wierd Trends

## Part 3 - GUI?????