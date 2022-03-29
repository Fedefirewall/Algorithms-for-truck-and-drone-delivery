# Algoritms-for-truck-and-drone-delivery
Project in python resolving the truck and single drone delivery.

The problem:
Given a list of clients (Posizioni_clienti.txt) where each line represent a package instruction in this form: _NUMBER X_COORDINATE Y_COORDINATE WEIGHT_ 
we want to create a solution that minimize the distance traveled by the truck (minimize the sum of the arcs).
In a file called _Distanze_TRUCK.txt_ we have all the distances between the clients (nodes), 
to which it was added a random value to simulate the longer distance traveling by road vs as the crow flies

This solution suppose:
- 1 truck and 1 drone
- Instant recharge of the drone as soon he reaches the truck (Drone)
- No autonomy decay due to weight (Drone)
- Can transport infinite numbers of pacakages, the only limit is the weight (Drone)
- Bascially all interactions are instant, except for the movements of the truck and the drone

The algorithms:
Construction: We start from zero to build a solution
Nearest Neighbour V+D.py : simply find the closest node, send the drone and repeat, when the drone cant reach the next node, we send there the truck

Cheapest Insertion V+D (strada+clienti).py : First we add nodes to the drone path using the cheapest insertion rule (until it has enough autonomy), 
                                            then we add the next best node to the truck path. we choose the best drone trip using the formula 
                                            trip_score=(len(visited_list_drone_this_trip))+(cost*alpha)+(weight*beta), with differents alpha and beta
                                            
TSP+best_node.py: First we create a path for the truck with all nodes, then we remove one node at a time and try to insert in a drone trip in the best way way possible

Improvement: we start from a correct solutiona dn try to improve it
Genetic algorithm: given some different solutions, we create childs and evalute the fitness to choose the best parents



