#region
#IMPORTAZIONE LIBRERIE
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes.function import neighbors 
import numpy as np     
from typing import Any, List
#region
class CustomError_noedges(Exception):
    def __init__(self,*args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    
    def __str__(self):
        print("Nessun arco tra questi nodi:"+(self.message))
        if self.message:
            return "Nessun arco tra questi nodi:"+(self.message)
        else:
            return "base has edge error custom"

class Custom_Graph(nx.Graph):
    def custom_remove_edge(self,node1,node2):
        if self.has_edge(node1,node2):
            self.remove_edge(node1,node2)
        elif self.has_edge(node2,node1):
            self.remove_edge(node2,node1)
        else:
            raise CustomError_noedges(str(node1)+" "+str(node2))
        
#classe per salvare i sotto cicli del drone
class Visited_node_drone:
    def __init__(self, index, trip_number):
        self.index = index
        self.trip_number = trip_number

def print_graph_for_debug():
    graph_total = nx.compose(graph_drone, graph_truck)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    
    #creo i colori dei nodi
    color_map=[]
    for node in graph_total:
    
            if (node == truck_node_index): 
                color_map.append('red')
            elif (node in visited_list_truck_indexes): 
                color_map.append('white')
            else: 
                color_map.append('green') 
    #colori degli archi aggiunti ogni volta vh faccio add edge

    plt.clf()   #clearo il grafico precedente
    nx.draw(graph_total,points,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
    #per stampare le distanze nx.draw_networkx_edge_labels(Grafo, pos)
    
    plt.show()         # display it interactively   

def compute_visited_list_truck():
    visited_list_truck_indexes_1=[node1 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_2=[node2 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes=visited_list_truck_indexes_1+visited_list_truck_indexes_2
    visited_list_truck_indexes=list(set(visited_list_truck_indexes))
    return visited_list_truck_indexes

def compute_visited_list():
    visited_list_truck_indexes_1=[node1 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_2=[node2 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_3=[node1 for node1,node2 in graph_drone.edges]
    visited_list_truck_indexes_4=[node2 for node1,node2 in graph_drone.edges]
    visited_list_truck_indexes=visited_list_truck_indexes_1+visited_list_truck_indexes_2+visited_list_truck_indexes_3+visited_list_truck_indexes_4
    visited_list_truck_indexes=list(set(visited_list_truck_indexes))
    return visited_list_truck_indexes
#Ricerca del nodo più vicino 
def nearest_node(neighbors_distance,visited_list_indexes):
    first_time=1
    for i in range(1,len(neighbors_distance)):  
        #se la distanza non è zero e il nodo non è nella lista dei visitati
        if(not(i in visited_list_indexes)):
            actual_value=neighbors_distance[i]
            actual_index=i

            if(first_time):
                min_value=actual_value
                min_index=actual_index
                first_time=0

            if(actual_value<min_value):
                min_value=actual_value
                min_index=actual_index
    return min_index

def find_best_edge(graph, dist, trip_number):
    #per ogni coppia di nodi cerco il nodo con costo minore tale che la
    #somma dei nuovi archi sia minima

    #scorro gli archi
    min_index=0
    cost_min=10000
    for node1,node2,attributes in graph.edges(data=True):

        # controllo se entrambi i 2 nodi sono stati visitati dal drone in questo ciclo OPPURE se trip_number=0 e l'arco non e bloccato (trip_number=0  indica che che sto utilizzando il truck)
        if ((trip_number==0 and [node1,node2] not in truck_locked_edges) or (any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):
            #scorro i nodi
            for i in range(1,client_number_range):  
                #se il nodo non è nella lista dei visitati
                if(not(i in visited_list_indexes)):
                    #calcolo il costo di questo nodo, 
                    #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
                    new_edge_cost=(dist[i][node1]) + (dist[i][node2])
                    actual_index=i
                    old_edge_cost=dist[node1][node2]
                    actual_cost=compute_solution_cost(dist)-old_edge_cost+new_edge_cost


                    if(actual_cost<cost_min):
                        cost_min=actual_cost
                        min_index=actual_index
                        node1_best=node1
                        node2_best=node2 

    return min_index,node1_best,node2_best;

def compute_solution_cost(dist):    
    cost=0
    for node1,node2,attributes in graph_truck.edges(data=True):
        cost+=dist[node1][node2]
    return cost

def compute_drone_cost(trip_number):
    cost=0
    possible_truck_movements=[]
    
    #nodi visitati in questo viaggio
    # per ogni nodo negli archi del drone
    for node1,node2,attributes in graph_drone.edges(data=True):
        # controllo se entrambi i 2 nodi sono stati visitati in questo ciclo
        if ((any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):  
            cost+=dist_drone[node1][node2]
            #print(node1,node2,dist_drone[node1][node2],cost)

    possible_truck_movements_1=[nodeB for nodeA,nodeB,attributes in graph_drone.edges(data=True) if nodeA==truck_node_index]
    possible_truck_movements_2=[nodeA for nodeA,nodeB,attributes in graph_drone.edges(data=True) if nodeB==truck_node_index]
    possible_truck_movements_all=possible_truck_movements_1+possible_truck_movements_2
    for node in possible_truck_movements_all:
        if (any(x.index == node and x.trip_number==trip_number for x in visited_list_drone)):
            possible_truck_movements.append(node)
        
    #print(possible_truck_movements)
    #mi salvo in una lista il costo della strada e il realtivo tratto che verra effettuato dal truck
    cost_routes=[]
    for i in range(len(possible_truck_movements)):
        #route avra (costo se il truck va a quel nodo, nodo)
        route=[(cost-dist_drone[truck_node_index][possible_truck_movements[i]]),possible_truck_movements[i]]
        cost_routes.append(route)
    return cost_routes

def compute_drone_cost_new(trip_number):
    cost=0
    #nodi visitati in questo viaggio
    # per ogni nodo negli archi del drone
    for node1,node2,attributes in graph_drone.edges(data=True):
        # controllo se entrambi i 2 nodi sono stati visitati in questo ciclo
        if ((any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):  
            cost+=dist_drone[node1][node2]
            #print(node1,node2,dist_drone[node1][node2],cost)
    return cost

def revert_this_trip(trip_number):
    global visited_list_drone
    global visited_list_indexes
    edges_remove=graph_drone.edges()
    for node1,node2 in edges_remove:
        # controllo se entrambi i 2 nodi sono stati visitati in questo ciclo
        if ((any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):  
            graph_drone.custom_remove_edge(node1,node2)
        if (len(graph_drone.edges(node1))==0):
            visited_list_drone = [node for node in visited_list_drone if node.index!=node1]
        if (len(graph_drone.edges(node2))==0):
            visited_list_drone = [node for node in visited_list_drone if node.index!=node2]

    visited_list_indexes=compute_visited_list()

def find_best_drone_route(cost_routes):
    #spiegare come vengono calcolati i 2 costi possibli, scelgo quello maggiore
    if len(cost_routes)<2:  
        return cost_routes[0]

    if(cost_routes[0][0]>=cost_routes[1][0]):
        return cost_routes[0]
    else:
        return cost_routes[1]

def drone_Cristofides_trip():
    global visited_list_indexes
    best_trip_score=0
    global drone_trip_counter
    trip_counter_best=0
    #prendo tutti gli archi disponibili nel percorso del truck e vedo quello ceh fa percorrere piu strada al drone
    for node1,node2 in graph_truck.edges:
        if([node1,node2] not in truck_locked_edges):
            graph_drone.add_edge(node1,node2,length=round(dist_drone[node1][node2],2),color='#97E5FF')
            visited_list_drone.append(Visited_node_drone(node1,drone_trip_counter))
            visited_list_drone.append(Visited_node_drone(node2,drone_trip_counter))

            cost=compute_drone_cost_new(drone_trip_counter)

            while(cost<=drone_autonomy and len(visited_list_indexes)<client_number):
                best_node_index,node1_start,node2_start=find_best_edge(graph_drone,dist_drone,drone_trip_counter)
                #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
                #quindi lo aggiungo e rimuovo l edge corrispondente
                graph_drone.add_edge(best_node_index,node1_start,length=round(dist_drone[best_node_index][node1_start],2),color='#97E5FF')
                graph_drone.add_edge(best_node_index,node2_start,length=round(dist_drone[best_node_index][node2_start],2),color='#97E5FF')
                visited_list_indexes=compute_visited_list()
                visited_list_drone.append(Visited_node_drone(best_node_index,drone_trip_counter))
                # conto quanti clienti sta servendo il drone in questo viaggio
                visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==drone_trip_counter]
                sub_clients_counter=len(visited_list_drone_this_trip)
                #lo rimuovo in ogni caso cosi risolvo il rpoblema dell arco obbligatorio
                graph_drone.custom_remove_edge(node1_start,node2_start)
                cost=compute_drone_cost_new(drone_trip_counter)

            visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==drone_trip_counter]
            cost=compute_drone_cost_new(drone_trip_counter)
            trip_score=len(visited_list_drone_this_trip)
            #print_graph_for_debug()
            #se ho trovato un perocorso migliore me lo salvo
            if trip_score>best_trip_score:
                best_trip_score=trip_score
                node1_start_best=node1
                node2_start_best=node2
                trip_counter_best=drone_trip_counter

            revert_this_trip(drone_trip_counter)
            #print_graph_for_debug()
            drone_trip_counter+=1
        
    #ora che ho trovato il migliore lo confermo
    graph_drone.add_edge(node1_start_best,node2_start_best,length=round(dist_drone[node1_start_best][node2_start_best],2),color='b')
    visited_list_drone.append(Visited_node_drone(node1_start_best,trip_counter_best))
    visited_list_drone.append(Visited_node_drone(node2_start_best,trip_counter_best))
    cost=compute_drone_cost_new(trip_counter_best)
    #e blocco l arco del truck
    truck_locked_edges.append([node1_start_best,node2_start_best])

    while(cost<=drone_autonomy and len(visited_list_indexes)<client_number):
        best_node_index,node1_start_best,node2_start_best=find_best_edge(graph_drone,dist_drone,trip_counter_best)
        #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
        #quindi lo aggiungo e rimuovo l edge corrispondente
        graph_drone.add_edge(best_node_index,node1_start_best,length=round(dist_drone[best_node_index][node1_start_best],2),color='b')
        graph_drone.add_edge(best_node_index,node2_start_best,length=round(dist_drone[best_node_index][node2_start_best],2),color='b')
        visited_list_indexes=compute_visited_list()
        visited_list_drone.append(Visited_node_drone(best_node_index,trip_counter_best))
        # conto quanti clienti sta servendo il drone in questo viaggio
        visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==trip_counter_best]
        sub_clients_counter=len(visited_list_drone_this_trip)
        #lo rimuovo in ogni caso cosi risolvo il rpoblema dell arco obbligatorio
        graph_drone.custom_remove_edge(node1_start_best,node2_start_best)
        cost=compute_drone_cost_new(trip_counter_best)    
            
    #print_graph_for_debug()
    return node1_start_best,node2_start_best

#Creazione grafi
graph_truck = Custom_Graph()  
graph_drone = Custom_Graph()    

#----------Inizio lettura coordinate e inserimento nel grafo e distanze drone-------------
#region
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
coord_section = False
points = {}


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
        graph_truck.add_node(index, pos=(coord_x, coord_y))
client_number=index
client_number_range=client_number+1  
istance.close()

#Inizializzo la matrice delle distanze del drone
dist_drone = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice del drone
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist_drone[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)

#endregion
#----------Inizio Lettura file distanze truck----------------
#region
filename = 'Distanze_TRUCK.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
dist_section = False
i=1
dist_truck = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
    #Inizio lettura coordinate e inserimento nel grafo
for line in istance.readlines():
    if re.match('START.*', line):
        dist_section=True
        continue
    elif re.match('FINE.*', line):
        break

    #CREAZIONE matrice
    if dist_section:   
        coord = line.split(' ')
        for j in range(0,client_number):
            dist_truck[i][j+1] = float(coord[j])
    i+=1
istance.close()

#Decido il nodo di partenza, ovvero il nostro deposito. 
starting_node = 20
truck_node_index = starting_node

#Dichiaro la lista dei nodi visitati durante l'algoritmo
visited_list_indexes = [starting_node]
#Dichiaro la lista dei nodi visitati dal truck durante l'algoritmo
visited_list_truck_indexes = [starting_node]

cost = 0    #costo iniziale del veicolo
drone_on_truck=1
drone_autonomy=35
capacity=100

visited_list_drone=[]
truck_locked_edges=[]

# conto quanti viaggi fa il drone
drone_trip_counter=0
# conto quanti clienti fa il drone
drone_clients_counter=0
#endregion
#-------FINE INIZIALIZZAZIONE-------
#endregion


#INIZIO CODICE
#Creo la lista con le distanze dei vicini
neighbors_distance = [0]
for i in range(1, client_number_range): 
    neighbors_distance.append(dist_drone[truck_node_index][i])
#Inserisco in nearest_index il nodo più vicino al truck
nearest_index = nearest_node(neighbors_distance, visited_list_indexes)
graph_truck.add_edge(truck_node_index,nearest_index,length=round(dist_truck[truck_node_index][nearest_index],2),color='r')
visited_list_truck_indexes=compute_visited_list_truck()
visited_list_indexes=compute_visited_list()

#ciclo esterno del truck
first_time=1
last_node=0
drone_trip_counter=0
while(len(visited_list_indexes)<client_number):
    drone_trip_counter+=1
    sub_clients_counter=0
    drone_autonomy_temp=drone_autonomy
    drone_returned=False

    #CHEAPEST INSERTION TRUCK
    #controllo se il truck può fare solo un nodo: sono gia ad almeno un nodo, quindi aggiungo l arco piu conveniente    
    best_node_index,node1_best,node2_best=find_best_edge(graph_truck,dist_truck,0)
    #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
    #quindi lo aggiungo e rimuovo l edge corrispondente
    graph_truck.add_edge(best_node_index,node1_best,length=round(dist_truck[best_node_index][node1_best],2),color='r')
    graph_truck.add_edge(best_node_index,node2_best,length=round(dist_truck[best_node_index][node2_best],2),color='r')
    visited_list_indexes.append(best_node_index)
    visited_list_truck_indexes=compute_visited_list_truck()
    #rimuovo solo se non sono al 2 ciclo, senno per la storia del undirected eliminerei il primo arco
    if(len(visited_list_truck_indexes)>3):
        graph_truck.custom_remove_edge(node1_best,node2_best)

    #print_graph_for_debug()


    #CICLO DEL DRONE
    if(len(visited_list_indexes)<client_number):
        drone_Cristofides_trip()

    cost=compute_solution_cost(dist_truck)


     

cost=compute_solution_cost(dist_truck)
print("Costo=",cost)
print("Nodo iniziale=",starting_node)
print("Autonomia drone", drone_autonomy)

print_graph_for_debug()




