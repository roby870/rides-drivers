import unittest
from datetime import datetime
from main import haversine, build_graph, assign_rides_to_drivers, MILES_PER_MINUTE
from driver import Driver
from ride import Ride


class TestRideAssignment(unittest.TestCase):

    def setUp(self):
        """
        Set up sample data for use in the tests.
        """
        self.rides = [
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
        ]

        self.drivers = [
            Driver(driver_id='driver_1',
                hourly_rate=20,
                location=(40.7306, -73.9352),  # East Village
                availability=[(datetime(2024, 8, 29, 8, 0), datetime(2024, 8, 29, 12, 0))]),
            Driver(driver_id='driver_2',
                hourly_rate=18,
                location=(40.7580, -73.9855),  # Times Square
                availability=[(datetime(2024, 8, 29, 9, 0), datetime(2024, 8, 29, 13, 0))]),
        ]


    def test_haversine(self):
        """
        Test the haversine function to calculate distances between two coordinates.
        """
        coord1 = (40.7128, -74.0060)  # Downtown Manhattan
        coord2 = (40.7306, -73.9352)  # East Village
        distance = haversine(coord1, coord2)
        self.assertAlmostEqual(distance, 3.9, places=1)  # Approximate distance between locations


    def test_build_graph(self):
        """
        Test if the graph is built correctly with rides and drivers' locations.
        """
        graph = build_graph(self.rides, self.drivers)
        self.assertIn((40.7128, -74.0060), graph)  # Downtown Manhattan should be a node
        self.assertIn((40.7306, -73.9352), graph)  # East Village should be a node
        self.assertTrue(len(graph[(40.7128, -74.0060)]) > 0)  # Should have at least one connection


    def test_assign_rides_to_drivers(self):
        """
        Test if rides are correctly assigned to available drivers.
        """
        graph = build_graph(self.rides, self.drivers)
        assignments = assign_rides_to_drivers(self.rides, self.drivers, graph)
        
        self.assertIn('driver_1', assignments)
        self.assertIn('driver_2', assignments)
        self.assertEqual(len(assignments['driver_1']), 0)  # No rides assigned to driver 1 
        self.assertEqual(len(assignments['driver_2']), 2)  # Driver 2 should have won the 2 rides


if __name__ == '__main__':
    unittest.main()