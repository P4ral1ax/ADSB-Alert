import math
from turfpy.measurement import boolean_point_in_polygon  # https://stackoverflow.com/questions/43892459/check-if-geo-point-is-inside-or-outside-of-polygon
from geojson import Point, Polygon, Feature 

## ROC ##
# LANDING_POLYGON = [(-77.70, 43.11), (-77.67, 43.10), (-77.67, 43.01), (-77.81, 43.06)] 
# LANDING_MAX_ALT = 200
# LANDING_HEADING = [0, 80]
# TAKEOFF_POLYGON = []

## TEST ##
LANDING_POLYGON = [(-77.126, 39.384), (-76.711, 39.278), (-76.861, 38.044), (-77.279, 38.301)]
LANDING_MAX_ALT = 10000
LANDING_HEADING = [200, 260]
TAKEOFF_POLYGON = []

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

    # Is the point in the polygon 
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
        if (in_zone(lat, lon)):

            # Is it at a low enough altitude
            if (aircraft.alt < LANDING_MAX_ALT):

                # Is it heading towards the airport
                if (LANDING_HEADING[0] < aircraft.heading < LANDING_HEADING[1]):
                    # Fire Alert
                    # print(f"Detected Aircraft Landing : {aircraft.name} | LAT : {aircraft.lat} LON : {aircraft.lon} | ALT : {aircraft.alt} | Heading : {aircraft.heading}")
                    pass
    


def detect_takeoff(devices):
    pass
    # for device in devices:
    #     aircraft = devices[device]
    #     lat = aircraft.lat
    #     lon = aircraft.lon
