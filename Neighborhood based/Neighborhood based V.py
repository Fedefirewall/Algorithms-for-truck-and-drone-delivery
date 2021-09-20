#Importazione librerie
import re #Libreria per leggere i file dati in input
import networkx as nx #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
import numpy as np

def piu_vicino(neihgbourlist,lista_visitati):
    first_time=1
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


def compute_solution_cost():    
    cost=0
    for node1,node2,attributes in Graph_truck.edges(data=True):
        cost+=dist_truck[node1][node2]
    return cost

#LETTURA DEL FILE DI INPUT
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r') 
coord_section = False
points = {}

Graph_truck = nx.DiGraph()               #G sarà il nostro grafo

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



#decido il nodo di partenza
random=15
nodo_attuale=random
lista_visitati=[nodo_attuale]
cost=0
while(len(lista_visitati)<client_number):
    #creo la lista dei vicini
    neihgbourlist=[]
    for i in range(1,client_number_range):
            neihgbourlist.append(dist_truck[nodo_attuale][i])
        
    # e ne trovo il più vicino
    indice_vicino=piu_vicino(neihgbourlist,lista_visitati)

    print(indice_vicino)
    #per stampare le distanze -> Grafo.add_edge(nodo_attuale,indice_vicino,length=dist[nodo_attuale][indice_vicino])
    Graph_truck.add_edge(nodo_attuale,indice_vicino,)
    cost=cost+dist_truck[nodo_attuale][indice_vicino]
    lista_visitati.append(indice_vicino)
    nodo_attuale=indice_vicino

print("Scaricando l'istanza, creando il grafo")
#aggiungo l'arco finale
Graph_truck.add_edge(nodo_attuale,random,length=dist_truck[nodo_attuale][random])
cost=cost+dist_truck[nodo_attuale][random]
pos = nx.get_node_attributes(Graph_truck, 'pos')

#setto colore grafo
color_map=[]
for node in Graph_truck:
    if node == random:
        color_map.append('red')
    else: 
        color_map.append('green') 
nx.draw(Graph_truck, points,node_color=color_map, node_size=100,with_labels=True, arrowsize=20)  # create a graph with the tour
#per stampare le distanze nx.draw_networkx_edge_labels(Grafo, pos)
cost=compute_solution_cost()
print("Costo=",cost)

plt.show()          # display it interactively