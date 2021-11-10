#IMPORTAZIONE LIBRERIE
from os import path
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.algorithms.centrality.eigenvector import eigenvector_centrality_numpy
from networkx.classes.function import neighbors 
import numpy as np 
import random

#Creazione grafi
Graph_truck_CC = nx.Graph()     #Grafo completamente connesso
Graph_truck_MST = nx.Graph()    #Grafo dell'MST
Graph_truck_OV = nx.Graph()     #Grafo con i nodi dispari dopo MST
Graph_truck_MWM = nx.Graph()    #Grafo Minimum weight matching dei nodi dispari.
Graph_truck_ET = nx.Graph()     #Grafo Eulerian Tour dove i nodi dispari sono diventati pari
Graph_truck_Final = nx.Graph() #Grafo finale
   

#LETTURA DEL FILE DI INPUT
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data_drone = f.read()    #Ci sono i dati del file drone

istance = open(filename, 'r')  
coord_section = False      #Cosa è coord_section?
points = {}
point = []
#---------------Inizio lettura coordinate e inserimento nel grafo-------------
for line in istance.readlines():
    if re.match('START.*', line):
        coord_section = True
        continue
    elif re.match('FINE.*', line):
        break

    if coord_section:                                                 #CREAZIONE GRAFO
        coord = line.split(' ')
        index = int(coord[0])
        coord_x = float(coord[1])
        coord_y = float(coord[2])
        points[index] = (coord_x, coord_y)
        x = [coord_x, coord_y]
        point.append(x)
        #Graph_truck.add_node(index, pos=(coord_x, coord_y))
client_number=index
client_number_range=client_number+1  
istance.close()

#Inizializzo la matrice delle distanze del drone
dist = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice del drone
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)


def tsp(data):

    #Tutto quello che è stato fatto è per il drone, ora inizio a creare la lista del drone dove tolgo i nodi del truck
    #Devo dunque modificare data per almeno il primo ciclo, dove il truck parte da un nodo x e va al più vicnio
    start_node_Truck = 15     #Questo nodo lo devo togliere dalla lista data
    

    # build a graph
    G = build_graph(data)
    print("Graph: ", G)
    nx.draw(Graph_truck_CC, with_labels = True)
    #plt.show()

    # build a minimum spanning tree
    MSTree = minimum_spanning_tree(G)
    print("MSTree: ", MSTree)
    nx.draw(Graph_truck_MST, with_labels = True)
    #plt.show()

    # find odd vertexes
    odd_vertexes = find_odd_vertexes(MSTree)
    print("Odd vertexes in MSTree: ", odd_vertexes)
    nx.draw(Graph_truck_OV, with_labels = True)
    #plt.show()

    # add minimum weight matching edges to MST
    minimum_weight_matching(MSTree, G, odd_vertexes)
    print("Minimum weight matching: ", MSTree)
    nx.draw(Graph_truck_MWM, with_labels = True)
    #plt.show()


    # find an eulerian tour
    eulerian_tour = find_eulerian_tour(MSTree, G)
    print("Eulerian tour: ", eulerian_tour)
    nx.draw(Graph_truck_ET, with_labels = True)
    #plt.show()
    

    current = eulerian_tour[0]
    path = [current]
    visited = [False] * len(eulerian_tour)
    visited[0] = True

    length = 0

    for v in eulerian_tour[1:]:
        if not visited[v]:
            path.append(v)
            visited[v] = True
            Graph_truck_Final.add_node(current)
            Graph_truck_Final.add_node(v)
            Graph_truck_Final.add_edge(current, v)

            length += G[current][v]
            current = v
        
    #path.append(path[0])

    print("Result path: ", path)
    print("Result length of the path: ", length)
    nx.draw(Graph_truck_Final, with_labels = True)
    #plt.show()

    return path, length


def get_length(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1.0 / 2.0)


def build_graph(data):      
    graph = {}
    for this in range(len(data)):
        for another_point in range(len(data)):
            if this != another_point:
                if this not in graph:
                    graph[this] = {}
                    Graph_truck_CC.add_node(this)

                graph[this][another_point] = get_length(data[this][0], data[this][1], data[another_point][0],
                                                        data[another_point][1])
                
            Graph_truck_CC.add_edge(this, another_point)

    return graph


class UnionFind:
    def __init__(self):
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        # find path of objects leading to the root
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def __iter__(self):
        return iter(self.parents)

    def union(self, *objects):    #Devo cambiare la funzione MAX
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest


def minimum_spanning_tree(G):    #Anche qua stampo il percorso ogni volta che faccio l'append così da avere alla fine 
    tree = []                    #il grafico anche dell'MST
    subtrees = UnionFind()
    for W, u, v in sorted((G[u][v], u, v) for u in G for v in G[u]):
        if subtrees[u] != subtrees[v]:   #W è il costo del tratto u-v, ed u,v sono i nodi del grafico
            tree.append((u, v, W))
            Graph_truck_MST.add_node(u)
            Graph_truck_MST.add_node(v)
            Graph_truck_MST.add_edge(u,v)
            subtrees.union(u, v)
    return tree


def find_odd_vertexes(MST):      #Ogni volta che trova il nodo dispari, ne cambio il colore per distinguerlo dagli altri
    tmp_g = {}
    vertexes = []
    for edge in MST:
        if edge[0] not in tmp_g:
            tmp_g[edge[0]] = 0

        if edge[1] not in tmp_g:
            tmp_g[edge[1]] = 0

        tmp_g[edge[0]] += 1
        tmp_g[edge[1]] += 1

    for vertex in tmp_g:
        if tmp_g[vertex] % 2 == 1:
            vertexes.append(vertex)
            Graph_truck_OV.add_node(vertex)
    return vertexes


def minimum_weight_matching(MST, G, odd_vert):
    import random
    random.shuffle(odd_vert)

    while odd_vert:
        v = odd_vert.pop()
        length = float("inf")
        u = 1
        closest = 0
        for u in odd_vert:
            if v != u and G[v][u] < length:
                length = G[v][u]
                closest = u

        MST.append((v, closest, length))
        Graph_truck_MWM.add_node(v)
        Graph_truck_MWM.add_node(closest)
        Graph_truck_MWM.add_edge(v,closest)
        odd_vert.remove(closest)


def find_eulerian_tour(MatchedMSTree, G):  #Quando faccio l'append aggiorno il grafico finale.
    # find neigbours
    neighbours = {}
    for edge in MatchedMSTree:
        if edge[0] not in neighbours:
            neighbours[edge[0]] = []
            

        if edge[1] not in neighbours:
            neighbours[edge[1]] = []
            
            

        
        neighbours[edge[0]].append(edge[1])
        neighbours[edge[1]].append(edge[0])
        

    print("Neighbours: ", neighbours)

    # finds the hamiltonian circuit
    start_vertex = MatchedMSTree[0][0]
    EP = [neighbours[start_vertex][0]]

    while len(MatchedMSTree) > 0:
        for i, v in enumerate(EP):
            if len(neighbours[v]) > 0:
                break

        while len(neighbours[v]) > 0:
            w = neighbours[v][0]
            Graph_truck_ET.add_node(v)
            Graph_truck_ET.add_node(w)
            Graph_truck_ET.add_edge(v,w)
            
            remove_edge_from_matchedMST(MatchedMSTree, v, w)

            del neighbours[v][(neighbours[v].index(w))]
            del neighbours[w][(neighbours[w].index(v))]
            
            i += 1
            
            EP.insert(i, w)
            v = w
            
        
    return EP


def remove_edge_from_matchedMST(MatchedMST, v1, v2):

    for i, item in enumerate(MatchedMST):
        if (item[0] == v2 and item[1] == v1) or (item[0] == v1 and item[1] == v2):
            del MatchedMST[i]

    return MatchedMST


#VARIABILI DRONE
drone_autonomy = 35
drone_capacity = 3000
add_edge_to_drone = []
edge_tabu = []
add_edge_to_tabu = []


truck_path, truck_lenght = tsp(point)
#print(dist)
#print(truck_path)
def find_longest_street(path, tabu):
    longest_street = 0
    for element_1 in path:
        node1_index = path.index(element_1)
        element_2 = path[node1_index + 1]
        if element_1 not in tabu:
            if path.index(element_2) == path.index(element_1) + 1:
                max_street = dist[element_1][element_2] 
                if max_street > longest_street:
                    longest_street = max_street
                    node1_long = element_1
                    node2_long = element_2
                else: continue
        else:
            if element_2 not in tabu:
                if path.index(element_2) == path.index(element_1) + 1:
                    max_street = dist[element_1][element_2] 
                    if max_street > longest_street:
                        longest_street = max_street
                        node1_long = element_1
                        node2_long = element_2
                    else: continue  
    return node1_long, node2_long, longest_street

#Ora ricerco i suoi vicini
def find_edge_for_drone(path, node1, node2):
    global drone_autonomy
    add_edge_to_drone = []
    actual_drone_autonomy = drone_autonomy
    actual_drone_autonomy -= dist[node1][node2]
    add_edge_to_drone.append([node1, node2])
    while(actual_drone_autonomy > 0):
        for element in truck_path:
            if path.index(element) == path.index(node1) - 1:
                precedent_node = element
                precedent_distance = dist[element][node1]
                continue
            elif truck_path.index(element) == path.index(node2) + 1:
                forward_node = element
                forward_distance = dist[node2][element]
                continue
            
        if precedent_distance > forward_distance:
            actual_drone_autonomy -= precedent_distance
            if actual_drone_autonomy > 0:
                add_edge_to_drone.append([precedent_node, node1])
                node1 = precedent_node        
        else:
            actual_drone_autonomy -= forward_distance
            if actual_drone_autonomy > 0:
                add_edge_to_drone.append([node2, forward_node])
                node2 = forward_node
    if len(add_edge_to_drone) < 2:
        for i in add_edge_to_drone:
            for element in i:
                if element not in add_edge_to_tabu:
                    add_edge_to_tabu.append(element)
    else:
        return add_edge_to_drone
    return add_edge_to_drone, add_edge_to_tabu


for i in range(0, 100):
    
    #Ricerca dell'arco più lungo all'interno del ciclo finale del truck
    node_1, node_2, distance = find_longest_street(truck_path, edge_tabu)
    print("Il percorso più lungo va dal nodo ", node_1, " al nodo ", node_2, " con costo: ", distance)

    #Ricerca degli archi da mettere nel ciclo del drone che salvo in una lista
    edge_for_drone, edge_tabu = find_edge_for_drone(truck_path, node_1, node_2)
    

    #Se c'è solo un arco, lo tengo in memoria, e riparto col ciclo con l'altro arco più lungo
    if len(edge_for_drone) > 2:
        print("Gli archi da togliere nel grafo del truck e da inserire nel grafico del drone sono: ", edge_for_drone)
    else:
        print("Gli archi da non considerare per la ricerca dell'arco maggiore sono: ", edge_tabu)
    
    
    

    





        
    




        








