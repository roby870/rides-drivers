import heapq
from datetime import timedelta


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