#Importazione librerie
import re #Libreria per leggere i file dati in input
import networkx as nx #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.drawing.layout import _sparse_fruchterman_reingold
import numpy as np
import time
from time import sleep
import random


filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istanza = open(filename, 'r')  
coord_section = False
points = {}


#Inizio lettura coordinate e
for line in istanza.readlines():
    if re.match('START.*', line):
        coord_section = True
        continue
    elif re.match('FINE.*', line):
        break

    if coord_section:                                              
        coord = line.split(' ')
        indice = int(coord[0])
        coord_x = float(coord[1])
        coord_y = float(coord[2])
        points[indice] = (coord_x, coord_y)
numero_clienti=indice
numero_clienti_range=numero_clienti+1  
istanza.close()

dist = [ [ 0 for i in range(numero_clienti_range) ] for j in range(numero_clienti_range) ]
dist2 = [ [ 0 for i in range(numero_clienti_range) ] for j in range(numero_clienti_range) ]


#matrice delle distanze
for i in range(1,numero_clienti_range):   
    for j in range(1,numero_clienti_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)
        DistDrone = str(dist[i][j])
 
FileInputVeicolo = open("Distanze_TRUCK.txt", "w") 
FileInputVeicolo.write("START\n") 
#matrice distanze per Veicolo
for i in range(1,numero_clienti_range):   
    for j in range(1,numero_clienti_range):
        if j != i:
            if j > i:
                x = random.uniform(0,5)
                dist2[i][j]=(math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)) + x
                 
            else:
                dist2[i][j] = dist2[j][i]
        else: 
               dist2[i][j] = 0

        DistVeic1 = str(dist2[i][j])
        FileInputVeicolo.write(DistVeic1)
        FileInputVeicolo.write(" ") 

    FileInputVeicolo.write("\n")    

FileInputVeicolo.write("FINE") 
