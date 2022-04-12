<h1><strong>Algorithms-for-truck-and-drone-delivery</strong></h1>
Project in python resolving the truck and single drone delivery.

<h1><strong>The problem</strong></h1>
Given a list of clients (Posizioni_clienti.txt) where each line represent a package instruction in this form: _NUMBER X\_COORDINATE Y\_COORDINATE WEIGHT_ 
we want to create a solution that minimize the distance traveled by the truck (minimize the sum of the arcs), while not exceeding the drone autonomy nor the max weigth for each trip.      

For example the first 3 nodes/clients are  

| Number | X\_COORDINATE | Y\_COORDINATE | WEIGHT |
| ------ | ------------- | ------------- | ----- |
| 01 | 10 | 21 | 16 |
| 02 | 22 | 18 | 82 |
| 03 | 7 | 7 | 76 | 


In a file called _Distanze_TRUCK.txt_ we have all the distances between the clients (nodes), 
to which it was added a random value to simulate the longer distance traveling by road vs as the crow flies.\
This file is a matrix _nxn_ where _n_ is the number of nodes, and the value at position i,j is the distance between node i and node j


This solution suppose:
- 1 truck and 1 drone
- Instant recharge of the drone as soon he reaches the truck (Drone)
- No autonomy decay due to weight (Drone)
- Can transport infinite numbers of pacakages, the only limit is the weight (Drone)
- Bascially all interactions are instant, except for the movements of the truck and the drone
***

## Algorithms
#### **Construction**: <font size="4"><strong>We start from zero to build a solution</strong></font>
- <strong>Nearest Neighbour V+D.py:</strong> simply find the closest node, send the drone and repeat, when the drone cant reach the next node, we send there the truck.   

- <strong>Cheapest Insertion V+D (strada+clienti).py:</strong> First we add nodes to the drone path using the cheapest insertion rule (until it has enough autonomy),  then we add the next best node to the truck path. we choose the best drone trip using the formula trip_score=(len(visited_list_drone_this_trip))+(cost*alpha)+(weight*beta), with differents alpha and beta

- <strong>TSP+best_node.py:</strong> First we create a path for the truck with all nodes, then we remove one node at a time and try to insert in a drone trip in the best way way possible

#### Improvement: <font size="4"><strong>we start from a correct solution and try to improve it</strong></font>
- <strong>Genetic algorithm:</strong> given some different solutions, we create childs and evalute the fitness to choose the best parents    

- <strong>2-OPT.py:</strong> 

