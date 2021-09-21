import re
import math
import random

#LETTURA DEL FILE DI INPUT
filename = 'File_Input_Truck.txt'      #nome file puntatore
with open(filename, 'r') as f:    #Apertura del file
    data = f.read()         #Lettura dei dati

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
client_number=index
client_number_range=client_number+1  
istance.close()

#Inizializzo la matrice delle distanze 
dist = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice 
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)

#Verifico la disuguaglianza triangolare 
for i in range(1, client_number_range):
    for j in range(1, client_number_range):
        for k in range(1, client_number_range):
            if dist[i][j] <= (dist[i][k] + dist[k][j]):     #Disuguaglianza triangolare
                pass 


