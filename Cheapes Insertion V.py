#IMPORTAZIONE LIBRERIE
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes.function import neighbors  #TEST MARCE
import numpy as np       #CIAO

#LETTURA DEL FILE DI INPUT
filename = 'FileInput.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istanza = open(filename, 'r')  
coord_section = False
points = {}

#Controllo del nodo più vicino 
def piu_vicino(neihgbourlist,lista_visitati):
    first_time=1
    for i in range(0,len(neihgbourlist)):  
        #se la distanza non è zero e il nodo non è nella lista dei visitati
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

#Creazione grafo
Graph = nx.DiGraph()        

#Inizio lettura coordinate e inserimento nel grafo
for line in istanza.readlines():
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
        Graph.add_node(index, pos=(coord_x, coord_y))
client_number=index
numero_clienti_range=client_number+1  
istanza.close()

#Inizializzo la matrice delle distanze 
dist = [ [ 0 for i in range(numero_clienti_range) ] for j in range(numero_clienti_range) ]
#Calcolo le distanze e riempio la matrice 
for i in range(1,numero_clienti_range):   
    for j in range(1,numero_clienti_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)

#Decido il nodo di partenza, ovvero il nostro deposito. 
actual_node = 15

#Dichiaro la lista dei nodi visitati durante l'algoritmo
visited_list = [actual_node]

Cost = 0    #Costo iniziale del veicolo

#while(len(visited_list)<client_number):
    
#Creo la lista dei vicini
neihgbourlist = []
for i in range(1, numero_clienti_range): 
    neihgbourlist.append(dist[actual_node][i])
#Inserisco in nearest_index il nodo più vicino al actual_node
nearest_index = piu_vicino(neihgbourlist, visited_list)

print(nearest_index, "-->")
Graph.add_edge(actual_node,nearest_index)
Cost += (dist[actual_node][nearest_index]*2)
visited_list.append(nearest_index)
actual_node=nearest_index
client_number -= 1
print(Cost)
color_map=[]

for node in Graph:
    if node == actual_node:
        color_map.append('red')
    else: 
        color_map.append('green') 

while(len(visited_list)<client_number):
    pass


nx.draw(Graph, points,node_color=color_map, node_size=100,with_labels=True, arrowsize=20)  #Creo il grafo con il tour
plt.show()          #Mostro il grafo