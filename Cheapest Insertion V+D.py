#IMPORTAZIONE LIBRERIE
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes.function import neighbors 
import numpy as np      


#Ricerca del nodo più vicino 
def nearest_node(neighbors_distance,lista_visitati):
    first_time=1
    for i in range(1,len(neighbors_distance)):  
        #se la distanza non è zero e il nodo non è nella lista dei visitati
        if(not(i in lista_visitati)):
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

def find_best_edge():
    #per ogni coppia di nodi cerco il nodo con costo minore tale che la
    #somma dei nuovi archi sia minima

    #scorro gli archi
    first_time=1
    for node1,node2,attributes in Graph_truck.edges(data=True):
        
        #scorro i nodi
        for i in range(1,client_number_range):  
            #se il nodo non è nella lista dei visitati
            if(not(i in visited_list)):
                #calcolo il costo di questo nodo, 
                #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
                new_edge_cost=(dist_truck[i][node1]) + (dist_truck[i][node2])
                actual_index=i
                old_edge_cost=dist_truck[node1][node2]
                actual_cost=compute_solution_cost()-old_edge_cost+new_edge_cost

                if(first_time):
                    min_index=actual_index
                    cost_min=actual_cost
                    node1_best=node1
                    node2_best=node2                  
                    first_time=0

                if(actual_cost<cost_min):
                    cost_min=actual_cost
                    min_index=actual_index
                    node1_best=node1
                    node2_best=node2 

    return min_index,node1_best,node2_best;

def compute_solution_cost():    
    cost=0
    for node1,node2,attributes in Graph_truck.edges(data=True):
        cost+=dist_truck[node1][node2]
    return cost
    
#Creazione grafi
Graph_truck = nx.DiGraph()  
Graph_drone = nx.DiGraph()      

#LETTURA DEL FILE DI INPUT
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
coord_section = False
points = {}

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
        Graph_truck.add_node(index, pos=(coord_x, coord_y))
client_number=index
client_number_range=client_number+1  
istance.close()

#Inizializzo la matrice delle distanze del drone
dist = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice del drone
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)


#----------Inizio Lettura file distanze truck----------------
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
starting_node = 15

#Dichiaro la lista dei nodi visitati durante l'algoritmo
visited_list = [starting_node]

cost = 0    #costo iniziale del veicolo

#while(len(visited_list)<client_number):
    
#Creo la lista con le distanze dei vicini
neighbors_distance = [0]
for i in range(1, client_number_range): 
    neighbors_distance.append(dist[starting_node][i])
#Inserisco in nearest_index il nodo più vicino all starting_node
nearest_index = nearest_node(neighbors_distance, visited_list)

#Aggiungo i primi 2 nodi
print(nearest_index, "-->")
Graph_truck.add_edge(starting_node,nearest_index,length=round(dist_truck[starting_node][nearest_index],2))
Graph_truck.add_edge(nearest_index,starting_node,length=round(dist_truck[starting_node][nearest_index],2))
visited_list.append(nearest_index)
###non credo serva aggiungere il nodo attuale###
#actual_node=nearest_index
clients_visited=client_number
clients_visited -= 1
print("Ora ho "+str(len(visited_list))+" nodi, con costo "+str(cost))
#creo i colori dei nodi
color_map=[]
for node in Graph_truck:
        if node == starting_node:
            color_map.append('red')
        else: 
            color_map.append('green') 



#inizio il ciclo
while(len(visited_list)<client_number):
    #aggiungo l arco piu conveniente    
    best_node_index,node1_best,node2_best=find_best_edge()

    #Ora ho trovato il nodo con detour di costo minimo, 
    #quindi lo aggiungo e rimuovo l edge corrispondente
   
    Graph_truck.add_edge(best_node_index,node1_best,length=round(dist_truck[best_node_index][node1_best],2))
    Graph_truck.add_edge(best_node_index,node2_best,length=round(dist_truck[best_node_index][node2_best],2))
    Graph_truck.remove_edge(node1_best,node2_best)
    visited_list.append(best_node_index)
    print("Il nodo migliore e "+str(best_node_index)+" collegato ai nodi "+str(node1_best)+" e "+str(node2_best))
    print("Ora ho "+str(len(visited_list))+" nodi")

    cost=compute_solution_cost()
    print("Il costo della solzuoen finale e "+str(cost))
   # nx.draw(Graph_truck, points,node_color=color_map, node_size=100,with_labels=True, arrowsize=20)  #Creo il grafo con il tour
    #pos = nx.get_node_attributes(Graph_truck, 'pos')
    #nx.draw_networkx_edge_labels(Graph_truck, pos)
  #  plt.show()          #Mostro il grafo
  #  plt.clf()
    

        



#stampa grafi
plt.figure(1)
nx.draw_networkx_edges(Graph_truck, points, arrowsize=20)  # create a graph with the tour  # create a graph with the tour

plt.figure(2)
edges_drone = Graph_drone.edges()
#label = nx.get_node_attributes(Graph_drone, 'label') 
colors = [Graph_drone[u][v]['color'] for u,v in edges_drone]
#nx.draw(Graph_drone,points,labels=label,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
nx.draw(Graph_drone,points,font_size=10, node_size=100,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)
plt.figure(3)
G3 = nx.compose(Graph_drone, Graph_truck)
edges = G3.edges()
colors = [G3[u][v]['color'] for u,v in edges]
#nx.draw(G3,points, labels=label,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
nx.draw(G3,points,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
#per stampare le distanze nx.draw_networkx_edge_labels(Grafo, pos)
print("Costo=",Costo)

plt.show()          # display it interactively


