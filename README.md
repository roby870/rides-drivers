# rides-drivers


This is a script which solves the following code challenge:

We have a lot of rides in New York for tomorrow, and we have a lot drivers in New York. We need to do a backend algorithm to figure out which ride to give to which driver so that:

There is no conflict, e.g., we don't give the 2 different rides at 9 AM to the same driver

We want to give the ride a lower priced driver if possible.

If we give a ride to pick up a passenger from New York time square and drop off the passenger at JFK airport to a driver, the next ride we give to the same driver should preferably pick up from JFK airport, this way, the driver doesn't have to drive a lot without a paying passenger on the car.

You may assume as input a collection of rides. Each ride consists of pickup time, pickup location (latitude/longitude), pickup address, drop off location/address and estimated ride duration. 

Note: Assumption of Inputs is a part of challenge.
