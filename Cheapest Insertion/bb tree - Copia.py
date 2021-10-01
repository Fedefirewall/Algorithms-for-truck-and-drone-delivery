 #Importazione librerie
#test git vscode
import re #Libreria per leggere i file dati in input
import networkx as nx #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
import numpy as np



filename = 'FileInput.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istanza = open(filename, 'r')  
coord_section = False
points = {}

Grafo = nx.Graph()               #G sarà il nostro grafo

#Inizio lettura coordinate e inserimento nel grafo

for line in istanza.readlines():
    if re.match('START.*', line):
        coord_section = True
        continue
    elif re.match('FINE.*', line):
        break

    if coord_section:           #CREAZIONE GRAFO
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


for i in range(1,numero_clienti_range):   
    for j in range(1,numero_clienti_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)
        #print(i,j,dist[i][j])

#decido il nodo di partenza
random=3
nodo_attuale=random
nodi_visitati=[nodo_attuale]
while(len(nodi_visitati)!=numero_clienti):

    #creo la lista dei vicini del nodo di partenza
   
    for i in range(1,numero_clienti_range):
        if (i==nodo_attuale|(i in nodi_visitati)):
            pass
        else:
            #se la lista dei noid voisatati è 1 allora istanzio neighborlist,altrimenti faccio append
            if(len(nodi_visitati)==1):
                neihgbourlist=[i,dist[nodo_attuale][i]]
            else:
                neihgbourlist = np.vstack([neihgbourlist, [i,dist[nodo_attuale][i]]])
            #aggiungo il nodo alla lsita dei visitati
            nodi_visitati.append(i)

#trovo il piu piccolo
  
    for row in neihgbourlist:
        indice=row[0]
        valore=row[1]

        #e il relativo indice
        #index_min = np.argmin(neihgbourlist)+1

    
        #aggiungo l'arco    
        #Grafo.add_edge(random,index_min)

print("Scaricando l'istanza, creando il grafo")


pos = nx.get_node_attributes(Grafo, 'pos')
nx.draw(Grafo, points,node_color="r", node_size=100,with_labels=True)  # create a graph with the tour
plt.show()          # display it interactively