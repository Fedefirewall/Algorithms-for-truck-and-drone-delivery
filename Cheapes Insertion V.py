#IMPORTAZIONE LIBRERIE
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes.function import neighbors 
import numpy as np      


#Ricerca del nodo più vicino 
def nearest_node(neihgbourlist,lista_visitati):
    first_time=1
    for i in range(1,len(neihgbourlist)):  
        #se la distanza non è zero e il nodo non è nella lista dei visitati
        if(not(i in lista_visitati)):
            actual_value=neihgbourlist[i]
            actual_index=i

            if(first_time):
                min_value=actual_value
                min_index=actual_index
                first_time=0

            if(actual_value<min_value):
                min_value=actual_value
                min_index=actual_index
    return min_index

def find_best_node(node1,node2,client_number_range,visited_list, dist_truck):
    first_time=1
       
    for i in range(1,client_number_range):  
         #se il nodo non è nella lista dei visitati
        if(not(i in visited_list)):
            #calcolo il costo di questo nodo, 
            #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
            actual_value=(dist_truck[i][node1]) + (dist_truck[i][node2])
            actual_index=i

            if(first_time):
                min_value=actual_value
                min_index=actual_index
                first_time=0

            if(actual_value<min_value):
                min_value=actual_value
                min_index=actual_index
    return min_index


#Creazione grafi
Graph_truck = nx.DiGraph()        

#LETTURA DEL FILE DI INPUT
filename = 'File_Input_Truck.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
coord_section = False
points = {}

#Inizio lettura coordinate e inserimento nel grafo del truck
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

#Inizializzo la matrice delle distanze 
dist = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice 
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)


#----------Inizio Lettura file distanze truck----------------
filename = 'FileInput1.txt'      #nome file puntatore
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
actual_node = 15

#Dichiaro la lista dei nodi visitati durante l'algoritmo
visited_list = [actual_node]

Cost = 0    #Costo iniziale del veicolo

#while(len(visited_list)<client_number):
    
#Creo la lista dei vicini
neihgbourlist = [0]
for i in range(1, client_number_range): 
    neihgbourlist.append(dist[actual_node][i])
#Inserisco in nearest_index il nodo più vicino al actual_node
nearest_index = nearest_node(neihgbourlist, visited_list)

print(nearest_index, "-->")
Graph_truck.add_edge(actual_node,nearest_index)
Graph_truck.add_edge(nearest_index,actual_node)
Cost += (dist[actual_node][nearest_index]*2)
visited_list.append(nearest_index)
actual_node=nearest_index
client_number -= 1
print(Cost)
color_map=[]

#primi due nodi aggiunti

#inizio il ciclo
while(len(visited_list)<client_number):
    #per ogni coppia di nodi cerco il nodo con costo minore tale che la
    #somma dei nuovi archi sia minima
    for node1,node2,a in Graph_truck.edges(data=True):
        best_node_test=find_best_node(node1,node2,client_number_range,visited_list, dist_truck)

        


for node in Graph_truck:
    if node == actual_node:
        color_map.append('red')
    else: 
        color_map.append('green') 
nx.draw(Graph_truck, points,node_color=color_map, node_size=100,with_labels=True, arrowsize=20)  #Creo il grafo con il tour
plt.show()          #Mostro il grafo