import math
import heapq
from datetime import datetime, timedelta


MILES_PER_MINUTE = 0.25 #Arbitrary velocity assigned to every driver.


class IntervalNode:
    """
    Represents a single node in an interval tree, containing an interval [low, high].

    Attributes:
        low (datetime): The starting point of the interval.
        high (datetime): The ending point of the interval.
        max (datetime): The maximum value in the subtree rooted at this node.
        left (IntervalNode): The left child of this node in the interval tree.
        right (IntervalNode): The right child of this node in the interval tree.
    
    Methods:
        __init__(low, high): Initializes an IntervalNode with the specified low and high values.
    """
    def __init__(self, low, high):
        self.low = low
        self.high = high
        self.max = high
        self.left = None
        self.right = None

class IntervalTree:
    """
    A data structure that supports efficient storage and querying of intervals, 
    allowing for quick lookup of intervals that overlap with a given interval.

    Attributes:
        root (IntervalNode): The root node of the interval tree.
    
    Methods:
        insert_interval(low, high): Inserts a new interval [low, high] into the interval tree.
        modify_intervals(low, high): Modifies intervals in the tree by removing any overlapping interval
                                     and reinserting the non-overlapping parts.
        is_available(low, high):
            Checks if the interval [low, high] is fully contained within any existing interval in the tree.
    """
    def __init__(self):
        self.root = None

    def _insert(self, root, low, high):
        """
        Inserts a new interval [low, high] into the interval tree.
        This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root node of the subtree where the interval will be inserted.
            low (datetime): The starting point of the interval.
            high (datetime): The ending point of the interval.

        Returns:
            IntervalNode: The new root of the subtree after insertion.
        """
        if root is None:
            return IntervalNode(low, high)
        if low < root.low: 
            root.left = self._insert(root.left, low, high)
        else:
            root.right = self._insert(root.right, low, high)
        root.max = max(root.max, high)
        return root

    def insert_interval(self, low, high):
        """
        Inserts a new interval [low, high] into the interval tree.

        Args:
            low (datetime): The starting point of the interval.
            high (datetime): The ending point of the interval.
        """
        if self.root is None:
            self.root = IntervalNode(low, high)
        else:
            self.root = self._insert(self.root, low, high)

    def _do_overlap(self, interval1, interval2):
        """
        Checks if two intervals overlap.
        This is an internal method and should not be called directly.

        Args:
            interval1 (IntervalNode): The first interval node.
            interval2 (IntervalNode): The second interval node.

        Returns:
            bool: True if the intervals overlap, False otherwise.
        """
        return interval1.low <= interval2.high and interval2.low <= interval1.high 

    def _search_overlap(self, root, low, high):
        """
        Searches for all intervals that overlap with the given interval [low, high] in the subtree rooted at root.
        This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root node of the subtree to search.
            low (datetime): The starting point of the interval to check for overlaps.
            high (datetime): The ending point of the interval to check for overlaps.

        Returns:
            list of tuples: A list of tuples where each tuple represents an overlapping interval [low, high].
        """
        if root is None:
            return []
        interval = IntervalNode(low, high)
        result = []
        if self._do_overlap(root, interval):
            result.append((root.low, root.high))
        if root.left is not None and root.left.max >= low:
            result.extend(self._search_overlap(root.left, low, high))
        result.extend(self._search_overlap(root.right, low, high))
        return result

    def _find_overlaps(self, low, high):
        """
        Returns a list of all intervals in the tree that overlap with the interval [low, high].
        This is an internal method and should not be called directly.

        Args:
            low (datetime): The starting point of the interval to check for overlaps.
            high (datetime): The ending point of the interval to check for overlaps.

        Returns:
            list of tuples: A list of tuples where each tuple represents an overlapping interval [low, high].
        """
        return self._search_overlap(self.root, low, high)

    def _find_min(self, root):
        """
        Finds the node with the minimum low value in the subtree rooted at root.
        This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root of the subtree to search.

        Returns:
            IntervalNode: The node with the minimum low value.
        """
        while root.left is not None:
            root = root.left
        return root
    
    def _delete_interval(self, root, low, high):
        """
        Recursively deletes an interval [low, high] from the interval tree.
        This method is used internally to handle the deletion of an interval
        from a subtree rooted at the given node. This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root of the subtree from which the interval should be deleted.
            low (datetime): The starting point of the interval to delete.
            high (datetime): The ending point of the interval to delete.

        Returns:
            IntervalNode: The root of the subtree after the deletion, with the interval [low, high] removed.
        """
        if root is None:
            return None
        if low < root.low:
            root.left = self._delete_interval(root.left, low, high)
        elif low > root.low:
            root.right = self._delete_interval(root.right, low, high)
        elif root.low == low and root.high == high: #we found the interval 
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            temp = self._find_min(root.right) #if the node has two children, we search the lowest value from the right part of the subtree
            root.low, root.high = temp.low, temp.high #we replace the interval with the lowest value from the right branch 
            root.right = self._delete_interval(root.right, temp.low, temp.high)
        #after deleting the interval, we refresh the max value on the top's nodes
        if root.left is None and root.right is None: 
            root.max = root.high
        elif root.left is None:
            root.max = max(root.high, root.right.max)
        elif root.right is None:
            root.max = max(root.high, root.left.max)
        else:
            root.max = max(root.high, root.left.max, root.right.max)
        return root

    def _delete(self, low, high):
        """
        Deletes an interval [low, high] from the interval tree. This is an internal method and should not be called directly.

        This method is a wrapper around the _delete_interval method and is used
        to initiate the deletion process from the root of the tree.

        Args:
            low (datetime): The starting point of the interval to delete.
            high (datetime): The ending point of the interval to delete.
        """
        self.root = self._delete_interval(self.root, low, high)

    def modify_intervals(self, low, high):
        """
        Modifies the interval tree by removing any intervals that overlap with the given interval [low, high]
        and then reinserting the non-overlapping portions back into the tree.

        Args:
            low (datetime): The starting point of the interval to modify.
            high (datetime): The ending point of the interval to modify.

        Notes:
            - For any interval [a, b] that overlaps with [low, high]:
                - If a < low, the interval [a, low] is reinserted.
                - If high < b, the interval [high, b] is reinserted.
        """
        overlapping_intervals = self._find_overlaps(low, high)
        for interval in overlapping_intervals:
            self._delete(interval[0], interval[1])
            if interval[0] < low:
                self.insert_interval(interval[0], low)
            if high < interval[1]:
                self.insert_interval(high, interval[1])


    def _is_available(self, node, low, high):
        """
        Recursively checks if an interval [low, high] is fully contained within any interval 
        in the subtree rooted at the given node.

        Args:
            node (IntervalNode): The root of the current subtree being checked.
            low (datetime): The starting point of the interval to check.
            high (datetime): The ending point of the interval to check.

        Returns:
            bool: True if the interval [low, high] is fully contained within an interval in this subtree, 
            False otherwise.
        """
        if not node:
            return False
        if low >= node.low and high <= node.high:
            return True
        if node.left and node.left.max >= low:
            if self._is_available(node.left, low, high):
                return True
        return self._is_available(node.right, low, high)
    

    def is_available(self, low, high):
        """
        Checks if an interval [low, high] is fully contained within any existing interval in the tree.

        Args:
            low (datetime): The starting point of the interval to check.
            high (datetime): The ending point of the interval to check.

        Returns:
            bool: True if the interval [low, high] is fully contained within an existing interval, False otherwise.
        """
        return self._is_available(self.root, low, high)


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


class Ride:
    """
    Represents a ride that includes pickup and drop-off information, 
    and provides functionality to find the most suitable driver.

    Attributes:
        pickup_time (datetime): The time when the ride is scheduled to start.
        pickup_location (tuple): The geographic coordinates (latitude, longitude) of the pickup location.
        pickup_address (str): The address of the pickup location.
        dropoff_location (tuple): The geographic coordinates (latitude, longitude) of the drop-off location.
        dropoff_address (str): The address of the drop-off location.
        estimated_ride_duration (int): The estimated duration of the ride in minutes.

    Methods:
        find_best_driver(drivers, graph): Finds the most suitable driver for the ride based on distance, availability, and hourly rate.
    """
    def __init__(self, pickup_time, pickup_location, pickup_address, dropoff_location, dropoff_address, estimated_ride_duration):
        self.pickup_time = pickup_time
        self.pickup_location = pickup_location
        self.pickup_address = pickup_address
        self.dropoff_location = dropoff_location
        self.dropoff_address = dropoff_address
        self.estimated_ride_duration = estimated_ride_duration

    def _dijkstra(self, graph, start, end):
        """
        Computes the shortest path from the start node to the end node in the given graph 
        using Dijkstra's algorithm.

        Args:
            graph (dict): A dictionary where the keys are nodes and the values are lists of tuples 
                        representing neighboring nodes and edge weights (distance in minutes).
            start (tuple[float, float]): Tuple of latitude and longitude, the starting node for the shortest path calculation.
            end (tuple[float, float]): Tuple of latitude and longitude, the ending node for the shortest path calculation.

        Returns:
            float: The shortest distance from the start node to the end node.
        """
        queue = [(0, start)]
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        visited = set()
        while queue:
            current_distance, current_node = heapq.heappop(queue)
            if current_node in visited:
                continue
            if current_node == end:
                return current_distance
            visited.add(current_node)
            if current_distance > distances[current_node]:
                continue
            for neighbor, weight in graph[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(queue, (distance, neighbor))
        return distances[end] if distances[end] != float('inf') else None

    def find_best_driver(self, drivers, graph):
        """
        Finds the most suitable driver for the ride based on proximity, availability, and hourly rate.

        This method evaluates each driver based on the distance to the pickup location, 
        their availability for the ride duration, and their hourly rate. It uses Dijkstra's algorithm 
        to calculate the distance from the driver's location to the pickup location, and selects the driver 
        who is closest and has the lowest hourly rate among those who are available.

        Args:
            drivers (list of Driver): A list of Driver objects to consider for the ride.
            graph (dict): A dictionary representing the geographic graph where the keys are nodes and the values 
                        are lists of tuples representing neighboring nodes and edge weights (distances in minutes).

        Returns:
            Driver: The Driver object representing the most suitable driver for the ride.
        """
        best_driver = None
        min_distance = float('inf')
        ride_end_time = self.pickup_time + timedelta(minutes=self.estimated_ride_duration)
        for driver in drivers:
            distance_to_pickup = self._dijkstra(graph, driver.location, self.pickup_location)
            if not driver.has_available_intervals(self.pickup_time - timedelta(minutes=distance_to_pickup), ride_end_time):  #Consider the time taken from the driver's location to the pickup location.
                continue
            if distance_to_pickup < min_distance:
                min_distance = distance_to_pickup
                hourly_rate = driver.hourly_rate
                best_driver = driver
            elif (distance_to_pickup == min_distance and driver.hourly_rate < hourly_rate): #For the same distance, choose the cheaper driver.
                hourly_rate = driver.hourly_rate
                best_driver = driver
        return best_driver


class Driver:
    """
    Represents a driver available for ride assignments.

    Attributes:
        driver_id (str): A unique identifier for the driver.
        hourly_rate (float): The hourly rate charged by the driver.
        location (tuple[float, float]): The geographic coordinates (latitude, longitude) of the driver's current location.
        availability (list[tuple[datetime, datetime]]): A list of tuples representing the driver's available time intervals 
                                       (start_time, end_time).
        interval_tree (IntervalTree): An interval tree data structure used to manage and query the driver's 
                                      availability intervals.

    Methods:
        has_available_intervals(start_time, end_time): Checks if the driver is available during the specified time interval.
        reserve_interval(start_time, end_time): Reserves a time interval by modifying the driver's availability.
    """
    def __init__(self, driver_id, hourly_rate, location, availability):
        self.driver_id = driver_id
        self.hourly_rate = hourly_rate
        self.location = location
        self.availability = availability
        self.interval_tree = IntervalTree()
        for start, end in availability:
            self.interval_tree.insert_interval(start, end)

    def has_available_intervals(self, start_time, end_time):
        """
        Checks if the driver is available during the specified time interval.

        Args:
            start_time (datetime): The start time of the interval to check.
            end_time (datetime): The end time of the interval to check.

        Returns:
            bool: True if the driver has availability during the specified time interval, False otherwise.
        """
        return self.interval_tree.is_available(start_time, end_time)
        
    def reserve_interval(self, start_time, end_time):
        """
        Reserves a time interval by modifying the driver's availability.

        This method updates the driver's interval tree by removing the reserved time interval from the 
        driver's availability. 

        Args:
            start_time (datetime): The start time of the interval to reserve.
            end_time (datetime): The end time of the interval to reserve.
        """
        self.interval_tree.modify_intervals(start_time, end_time)


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
