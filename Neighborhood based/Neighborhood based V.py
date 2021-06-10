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

filename = 'FileInput.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istanza = open(filename, 'r')  
coord_section = False
points = {}

Grafo = nx.DiGraph()               #G sarà il nostro grafo

#Inizio lettura coordinate e inserimento nel grafo
for line in istanza.readlines():
    if re.match('START.*', line):
        coord_section = True
        continue
    elif re.match('FINE.*', line):
        break

    if coord_section:                                                 #CREAZIONE GRAFO
        coord = line.split(' ')
        indice = int(coord[0])
        coord_x = float(coord[1])
        coord_y = float(coord[2])
        points[indice] = (coord_x, coord_y)
        Grafo.add_node(indice, pos=(coord_x, coord_y))
numero_clienti=indice
numero_clienti_range=numero_clienti+1  
istanza.close()

dist = [ [ 0 for i in range(numero_clienti_range) ] for j in range(numero_clienti_range) ]

#matrice delle distanze
for i in range(1,numero_clienti_range):   
    for j in range(1,numero_clienti_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)


#decido il nodo di partenza
random=10
nodo_attuale=random
lista_visitati=[nodo_attuale]
Costo=0
while(len(lista_visitati)<numero_clienti):
    #creo la lista dei vicini
    neihgbourlist=[]
    for i in range(1,numero_clienti_range):
            neihgbourlist.append(dist[nodo_attuale][i])
        
    # e ne trovo il più vicino
    indice_vicino=piu_vicino(neihgbourlist,lista_visitati)

    print(indice_vicino)
    #per stampare le distanze -> Grafo.add_edge(nodo_attuale,indice_vicino,length=dist[nodo_attuale][indice_vicino])
    Grafo.add_edge(nodo_attuale,indice_vicino,)
    Costo=Costo+dist[nodo_attuale][indice_vicino]
    lista_visitati.append(indice_vicino)
    nodo_attuale=indice_vicino

print("Scaricando l'istanza, creando il grafo")
#aggiungo l'arco finale
Grafo.add_edge(nodo_attuale,random,length=dist[nodo_attuale][random])
Costo=Costo+dist[nodo_attuale][random]
pos = nx.get_node_attributes(Grafo, 'pos')

#setto colore grafo
color_map=[]
for node in Grafo:
    if node == random:
        color_map.append('red')
    else: 
        color_map.append('green') 
nx.draw(Grafo, points,node_color=color_map, node_size=100,with_labels=True, arrowsize=20)  # create a graph with the tour
#per stampare le distanze nx.draw_networkx_edge_labels(Grafo, pos)
print("Costo=",Costo)

plt.show()          # display it interactively