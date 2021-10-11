#Importazione librerie
import re #Libreria per leggere i file dati in input
import networkx as nx #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
import numpy as np
import random

def piu_vicino(neihgbourlist,lista_visitati):
    first_time=1
    indice_minimo=-1
    for i in range(0,len(neihgbourlist)):  
        #se la distanza nonè zero e il nodo non è nella lista dei visitati
        if(not(i+1 in lista_visitati)):
            valore_attuale=neihgbourlist[i]
            indice_attuale=i+1

            
            if(first_time):
                valore_minimo=valore_attuale
                indice_minimo=indice_attuale
                first_time=0

            if(valore_attuale<valore_minimo):
                valore_minimo=valore_attuale
                indice_minimo=indice_attuale
    return indice_minimo

#Grafi
Grafo_drone = nx.DiGraph()
Grafo_iniziale_Truck = nx.DiGraph()
Grafo_truck = nx.DiGraph()

#----------INIZIO Lettura file nodi----------------
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
istanza = open(filename, 'r')
coord_section = False  
points = {}
point = []
lista_pesi_pacchi=[-1]

    #Inizio lettura coordinate e inserimento nel grafo
for line in istanza.readlines():
    if re.match('START.*', line):
        coord_section = True
        continue
    elif re.match('FINE.*', line):
        break

    #CREAZIONE GRAFO
    if coord_section:   
        coord = line.split(' ')
        indice = int(coord[0])
        coord_x = float(coord[1])
        coord_y = float(coord[2])
        peso= float(coord[3])
        lista_pesi_pacchi.append(peso)
        points[indice] = (coord_x, coord_y)
        x = [coord_x, coord_y]
        #label=str(indice)+":"+str(peso)
        #Grafo_drone.add_node(indice,label=label, pos=(coord_x, coord_y))
        #Grafo_drone.add_node(indice, pos=(coord_x, coord_y))
        point.append(x)

        
numero_clienti=indice
numero_clienti_range=numero_clienti+1  
istanza.close()


#matrice delle distanze drone
dist_drone = [ [ 0 for i in range(numero_clienti_range) ] for j in range(numero_clienti_range) ]
for i in range(1,numero_clienti_range):   
    for j in range(1,numero_clienti_range):
        dist_drone[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)


#----------Inizio Lettura file distanze truck----------------
filename = 'Distanze_TRUCK.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istanza = open(filename, 'r')  
dist_section = False
i=1
dist_truck = [ [ 0 for i in range(numero_clienti_range) ] for j in range(numero_clienti_range) ]
    #Inizio lettura coordinate e inserimento nel grafo
for line in istanza.readlines():
    if re.match('START.*', line):
        dist_section=True
        continue
    elif re.match('FINE.*', line):
        break

    #CREAZIONE matrice
    if dist_section:   
        coord = line.split(' ')
        for j in range(0,numero_clienti):
            dist_truck[i][j+1] = float(coord[j])
    i+=1
istanza.close()

#DECIDO NODO DI PARTENZA
random=15
lista_pesi_pacchi[random]=0
Grafo_iniziale_Truck.add_node(random)


nodo_attuale_truck=random
nodo_attuale_drone=random
lista_visitati=[random]

#Costo totale percorso
Costo=0

#VARIABILI DEL DRONE
Drone_on_truck=1
Drone_spostato=0
#Autonomia_drone=25
Capacita=150
#Autonomia_drone_attuale=Autonomia_drone

#LISTA DEI NODI VICINI A UN NODO
neihgbourlist=[]
for i in range(1,numero_clienti_range):
    neihgbourlist.append(dist_drone[nodo_attuale_drone][i])
        
#TROVO IL NODO PIù VICINO
indice_vicino=piu_vicino(neihgbourlist,lista_visitati)
Grafo_iniziale_Truck.add_node(indice_vicino)
Grafo_iniziale_Truck.add_edge(random, indice_vicino)

nx.draw(Grafo_iniziale_Truck, with_labels = True)
plt.show()
#print(indice_vicino)

Costo_drone=0
Movimenti_drone=0
Peso_trasportato_attuale=0

#print(points)
#Elimino dalla lista del drone il nodo iniziale del truck e il nodo più vicino
del points[random]
del points[indice_vicino]

#NUOVA LISTA DA CUI PARTIRà IL DRONE PER FARE CHRISTOFIDES CON TUTTI I CONTROLLI (lista da passare a tsp)
point = list(list(points.values()))

#INIZIO CHRISTOFIDES DRONE
#region
def tsp(data):
    # build a graph
    G = build_graph(data)
    print("Graph: ", G)

    # build a minimum spanning tree
    MSTree = minimum_spanning_tree(G)
    print("MSTree: ", MSTree)

    # find odd vertexes
    odd_vertexes = find_odd_vertexes(MSTree)
    print("Odd vertexes in MSTree: ", odd_vertexes)

    # add minimum weight matching edges to MST
    minimum_weight_matching(MSTree, G, odd_vertexes)
    print("Minimum weight matching: ", MSTree)

    # find an eulerian tour
    eulerian_tour = find_eulerian_tour(MSTree, G)

    print("Eulerian tour: ", eulerian_tour)

    current = eulerian_tour[0]
    path = [current]
    visited = [False] * len(eulerian_tour)
    visited[0] = True

    length = 0

    for v in eulerian_tour[1:]:
        if not visited[v]:
            path.append(v)
            visited[v] = True

            length += G[current][v]
            current = v

    path.append(path[0])

    print("Result path: ", path)
    print("Result length of the path: ", length)

    return length, path


def get_length(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1.0 / 2.0)


def build_graph(data):
    Autonomia_drone = 25
    graph = {}
    for this in range(len(data)):
        for another_point in range(len(data)):
            if (this != another_point and Autonomia_drone > 0):
                if this not in graph:
                    graph[this] = {}
                    Autonomia_drone =- int(dist_drone(this))

                graph[this][another_point] = get_length(data[this][0], data[this][1], data[another_point][0],
                                                        data[another_point][1])
    print(Autonomia_drone)
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

    def union(self, *objects):
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest


def minimum_spanning_tree(G):
    tree = []
    subtrees = UnionFind()
    for W, u, v in sorted((G[u][v], u, v) for u in G for v in G[u]):
        if subtrees[u] != subtrees[v]:
            tree.append((u, v, W))
            subtrees.union(u, v)

    return tree


def find_odd_vertexes(MST):
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
        odd_vert.remove(closest)


def find_eulerian_tour(MatchedMSTree, G):
    # find neigbours
    neighbours = {}
    for edge in MatchedMSTree:
        if edge[0] not in neighbours:
            neighbours[edge[0]] = []

        if edge[1] not in neighbours:
            neighbours[edge[1]] = []

        neighbours[edge[0]].append(edge[1])
        neighbours[edge[1]].append(edge[0])

    # print("Neighbours: ", neighbours)

    # finds the hamiltonian circuit
    start_vertex = MatchedMSTree[0][0]
    EP = [neighbours[start_vertex][0]]

    while len(MatchedMSTree) > 0:
        for i, v in enumerate(EP):
            if len(neighbours[v]) > 0:
                break

        while len(neighbours[v]) > 0:
            w = neighbours[v][0]

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

#endregion

tsp(point)


    