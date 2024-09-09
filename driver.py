from interval_tree import IntervalTree


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