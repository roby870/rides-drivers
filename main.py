import math
from datetime import datetime, timedelta
from driver import Driver
from ride import Ride 


MILES_PER_MINUTE = 0.25 #Arbitrary velocity assigned to every driver.


def haversine(coord1, coord2):
    """
    Calculate the great-circle distance between two points on the Earth's surface.

    This function uses the Haversine formula to calculate the distance between 
    two points on the surface of a sphere, given their latitude and longitude.
    The result is returned in miles.

    Args:
        coord1: tuple of float
            A tuple representing the latitude and longitude of the first point 
            (latitude, longitude).
        coord2: tuple of float
            A tuple representing the latitude and longitude of the second point 
            (latitude, longitude).

    Returns:
        distance: float
            The distance between the two points in miles.
    """
    R = 3958.8  # Radius of the Earth in miles
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def build_graph(rides, drivers):
    """
    Build a graph representing locations and estimated travel times between them.

    This function creates a graph where each node represents a location (either
    a pickup or dropoff point for rides, or a driver's initial location) and edges represent
    the estimated travel times between these locations. 

    Args:
        rides: list of Ride objects
        drivers: list of Driver objects

    Returns:
        graph: dict
            A dictionary where keys are locations (tuples of latitude and longitude)
            and values are lists of tuples. Each tuple contains a neighboring location
            and the estimated ride duration (in minutes).
    """
    graph = {}  
    dropoff_locations = []
    for ride in rides:
        if ride.pickup_location not in graph:
            graph[ride.pickup_location] = []
        if ride.dropoff_location not in graph:
            graph[ride.dropoff_location] = []
        graph[ride.pickup_location].append((ride.dropoff_location, ride.estimated_ride_duration))
        graph[ride.dropoff_location].append((ride.pickup_location, ride.estimated_ride_duration))
        dropoff_locations.append(ride.dropoff_location)
    for dropoff_location in dropoff_locations:
        for ride in rides:
            if all(ride.pickup_location != t[0] for t in graph[dropoff_location]): #Make sure to add the connection just once.
                distance_miles = haversine(dropoff_location, ride.pickup_location)
                travel_time = distance_miles / MILES_PER_MINUTE
                graph[dropoff_location].append((ride.pickup_location, travel_time))
    for driver in drivers:
        if driver.location not in graph:
            graph[driver.location] = []
            for ride in rides:
                if any(start <= ride.pickup_time <= end for start, end in driver.availability): 
                    if all(ride.pickup_location != t[0] for t in graph[driver.location]): #Make sure to add the connection just once.
                        distance_miles = haversine(driver.location, ride.pickup_location)
                        travel_time = distance_miles / MILES_PER_MINUTE
                        graph[driver.location].append((ride.pickup_location, travel_time))
    return graph


#If we want to make sure that we give all the drivers at least one ride, we could do a first step
#where we assign a first ride to each driver (the available ride nearest him).
def assign_rides_to_drivers(rides, drivers, graph):
    """
    Assigns rides to the most suitable drivers based on ride pickup times, driver availability, 
    and geographic location to minimize idle time between rides.

    This function first sorts the rides by their pickup times and then iterates through each ride 
    to find the best available driver. The selected driver is assigned the ride, and their availability 
    is updated based on the ride's duration. The driver's location is updated to the drop-off location 
    of the ride.

    Args:
        rides (list of Ride): A list of Ride objects.
        drivers (list of Driver): A list of Driver objects.
        graph (dict): A dictionary where keys are locations (tuples of latitude and longitude)
                        and values are lists of tuples. Each tuple contains a neighboring location
                        and the estimated ride duration (in minutes).

    Returns:
        dict: A dictionary where the keys are driver IDs and the values are lists of assigned Ride 
              objects. Each list contains the rides assigned to that driver.
    """
    assignments = {driver.driver_id: [] for driver in drivers}
    rides.sort(key=lambda x: x.pickup_time)
    for ride in rides:
        best_driver = ride.find_best_driver(drivers, graph)
        if best_driver:
            assignments[best_driver.driver_id].append(ride)
            ride_end_time = ride.pickup_time + timedelta(minutes=ride.estimated_ride_duration)
            best_driver.reserve_interval(ride.pickup_time, ride_end_time)
            best_driver.location = ride.dropoff_location
    return assignments


""" 
I assume all rides start and end on the same day. 
If any ride starts earlier or ends later than the current day, 
I assume the program will be provided with drivers who also start earlier or end later than the current day. 
The solution is flexible enough to handle those cases.
"""
rides = [
    Ride(pickup_time=datetime(2024, 8, 29, 10, 0), 
         pickup_location=(40.7128, -74.0060),  # Downtown Manhattan
         pickup_address="Downtown Manhattan", 
         dropoff_location=(40.7306, -73.9352),  # East Village
         dropoff_address="East Village", 
         estimated_ride_duration=45),
    Ride(pickup_time=datetime(2024, 8, 29, 9, 0), 
         pickup_location=(40.7580, -73.9855),  # Times Square
         pickup_address="Times Square", 
         dropoff_location=(40.7128, -74.0060),  # Downtown Manhattan
         dropoff_address="Downtown Manhattan", 
         estimated_ride_duration=30),
    Ride(pickup_time=datetime(2024, 8, 29, 11, 0), 
         pickup_location=(40.7306, -73.9352),  # East Village
         pickup_address="East Village", 
         dropoff_location=(40.7480, -73.9857),  # Empire State Building
         dropoff_address="Empire State Building", 
         estimated_ride_duration=20),
    Ride(pickup_time=datetime(2024, 8, 29, 8, 30), 
         pickup_location=(40.7480, -73.9857),  # Empire State Building
         pickup_address="Empire State Building", 
         dropoff_location=(40.7128, -74.0060),  # Downtown Manhattan
         dropoff_address="Downtown Manhattan", 
         estimated_ride_duration=40),
    Ride(pickup_time=datetime(2024, 8, 29, 12, 0), 
         pickup_location=(40.7295, -73.9965),  # Washington Square Park
         pickup_address="Washington Square Park", 
         dropoff_location=(40.7306, -73.9352),  # East Village
         dropoff_address="East Village", 
         estimated_ride_duration=15),
    Ride(pickup_time=datetime(2024, 8, 29, 13, 0), 
         pickup_location=(40.7488, -73.9680),  # United Nations
         pickup_address="United Nations", 
         dropoff_location=(40.7580, -73.9855),  # Times Square
         dropoff_address="Times Square", 
         estimated_ride_duration=25),
    Ride(pickup_time=datetime(2024, 8, 29, 14, 0), 
         pickup_location=(40.7614, -73.9776),  # Carnegie Hall
         pickup_address="Carnegie Hall", 
         dropoff_location=(40.7480, -73.9857),  # Empire State Building
         dropoff_address="Empire State Building", 
         estimated_ride_duration=30),
    Ride(pickup_time=datetime(2024, 8, 29, 15, 0), 
         pickup_location=(40.7527, -73.9772),  # Grand Central Terminal
         pickup_address="Grand Central Terminal", 
         dropoff_location=(40.7580, -73.9855),  # Times Square
         dropoff_address="Times Square", 
         estimated_ride_duration=20),
    Ride(pickup_time=datetime(2024, 8, 29, 16, 0), 
         pickup_location=(40.7061, -74.0086),  # Wall Street
         pickup_address="Wall Street", 
         dropoff_location=(40.7488, -73.9680),  # United Nations
         dropoff_address="United Nations", 
         estimated_ride_duration=35),
    Ride(pickup_time=datetime(2024, 8, 29, 17, 0), 
         pickup_location=(40.7061, -74.0086),  # Wall Street
         pickup_address="Wall Street", 
         dropoff_location=(40.7295, -73.9965),  # Washington Square Park
         dropoff_address="Washington Square Park", 
         estimated_ride_duration=25)
]


drivers = [
    Driver(driver_id='driver_1',
           hourly_rate=20,
           location=(40.7306, -73.9352),  # East Village
           availability=[(datetime(2024, 8, 29, 8, 0), datetime(2024, 8, 29, 12, 0))]),
    Driver(driver_id='driver_2',
           hourly_rate=18,
           location=(40.7580, -73.9855),  # Times Square
           availability=[(datetime(2024, 8, 29, 9, 0), datetime(2024, 8, 29, 13, 0))]),
    Driver(driver_id='driver_3',
           hourly_rate=22,
           location=(40.7488, -73.9680),  # United Nations
           availability=[(datetime(2024, 8, 29, 10, 0), datetime(2024, 8, 29, 14, 0))]),
    Driver(driver_id='driver_4',
           hourly_rate=19,
           location=(40.7614, -73.9776),  # Carnegie Hall
           availability=[(datetime(2024, 8, 29, 12, 0), datetime(2024, 8, 29, 16, 0))]),
    Driver(driver_id='driver_5',
           hourly_rate=21,
           location=(40.7061, -74.0086),  # Wall Street
           availability=[(datetime(2024, 8, 29, 14, 0), datetime(2024, 8, 29, 18, 0))])
]


graph = build_graph(rides, drivers)
assignments = assign_rides_to_drivers(rides, drivers, graph)
for driver_id, assigned_rides in assignments.items():
    if(len(assigned_rides) == 0):
        print(f"Driver {driver_id} hasn't been assigned to any rides.")
    else:
        print(f"Driver {driver_id} has been assigned the following rides:")
        for ride in assigned_rides:
            print(f"  Pickup at {ride.pickup_time} from {ride.pickup_location} to {ride.dropoff_location}")
