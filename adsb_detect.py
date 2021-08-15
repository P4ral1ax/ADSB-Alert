import math
from turfpy.measurement import boolean_point_in_polygon  # https://stackoverflow.com/questions/43892459/check-if-geo-point-is-inside-or-outside-of-polygon
from geojson import Point, Polygon, Feature 
import adsb_make_device

ALERT_RANGE=1800 # 30 Min

## ROC ##
LANDING_POLYGON = [(-77.70, 43.11), (-77.67, 43.10), (-77.67, 43.01), (-77.81, 43.06)] 
LANDING_MAX_ALT = 400 # (METRES) 
LANDING_HEADING = [0, 80]
TAKEOFF_POLYGON = []

## TEST ##
# LANDING_POLYGON = [(-77.126, 39.384), (-76.711, 39.278), (-76.861, 38.044), (-77.279, 38.301)]
# LANDING_MAX_ALT = 10000
# LANDING_HEADING = [200, 260]
# TAKEOFF_POLYGON = []

## Where all detection is done ##
def in_zone(lat, lon):
    # Create point representing plane
    location = Feature(geometry=Point((lat, lon)))
    # Create polygon representing detection area
    detection_area = Polygon(
        [
            [
                LANDING_POLYGON[0],
                LANDING_POLYGON[1],
                LANDING_POLYGON[2],
                LANDING_POLYGON[3],
            ]
        ]
    )

    # Is the point in the polygon? 
    in_area = boolean_point_in_polygon(location, detection_area)
    return(in_area)


# Detect if any planes are preparing to land on our side
def detect_landings(devices):
    for device in devices:
        aircraft = devices[device]
        lat = aircraft.lat
        lon = aircraft.lon   

        # Seperated for Ez reading
        # Is it in target zone
        # Fuck you I'll use 4 if statements in a row if I want to (thats a 2 extra just in this comment)
        if (in_zone(lat, lon)):

            # Is it at a low enough altitude
            if (aircraft.alt < LANDING_MAX_ALT):

                # Is it heading towards the airport
                if (LANDING_HEADING[0] < aircraft.heading < LANDING_HEADING[1]):
                    
                    # Has this recently fired alert? Yes -> Pass, No -> Enter 
                    if ((aircraft.last_time - aircraft.last_alert) > ALERT_RANGE):
                        updated_aircraft = adsb_make_device.update_last_alert(aircraft)
                        devices[device] = updated_aircraft 
                        print(f"Detected Aircraft Landing : {updated_aircraft.name} | LAT : {updated_aircraft.lat} LON : {updated_aircraft.lon} | ALT : {updated_aircraft.alt} | Heading : {updated_aircraft.heading}\n    Last Alert : {updated_aircraft.last_alert}")

    # Return Updated Devices
    # Need this because we need to update the last time a device was alerted on
    return(devices)                     
    


def detect_takeoff(devices):
    pass
    # for device in devices:
    #     aircraft = devices[device]
    #     lat = aircraft.lat
    #     lon = aircraft.lon
