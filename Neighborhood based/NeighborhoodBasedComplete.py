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
Grafo_truck = nx.DiGraph()

#----------INIZIO Lettura file nodi----------------
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
istanza = open(filename, 'r')
coord_section = False  
points = {}
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
        #label=str(indice)+":"+str(peso)
        #Grafo_drone.add_node(indice,label=label, pos=(coord_x, coord_y))
        Grafo_drone.add_node(indice, pos=(coord_x, coord_y))

        
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

#dist_truck[25][12]=3000
#dist_truck[25][13]=5
#decido il nodo di partenza
random=15
lista_pesi_pacchi[random]=0

#setto il peso del deposito=0
#label=str(random)+":"+str(0)
#nx.set_node_attributes(Grafo_drone ,{random:str(label)},'label' )

#random.randint(0,30)
nodo_attuale_truck=random
nodo_attuale_drone=random
lista_visitati=[random]
Costo=0
Drone_on_truck=1
Drone_spostato=0
Autonomia_drone=25
Capacita=150
Autonomia_drone_attuale=Autonomia_drone
#ciclo esterno , quando esco aggiungo solo l'arco finale e stampo
while(len(lista_visitati)<numero_clienti):
#region
    #creo la lista dei vicini
    neihgbourlist=[]
    for i in range(1,numero_clienti_range):
            neihgbourlist.append(dist_drone[nodo_attuale_drone][i])
        
    # e ne trovo il più vicino
    indice_vicino=piu_vicino(neihgbourlist,lista_visitati)
#endregion
    Costo_drone=0
    Movimenti_drone=0
    Peso_trasportato_attuale=0
    #Sotto-ciclo drone, posso uscire se finisce l'autonomia,supero la capacità o se visito l'ultimo nodo con il drone
    Drone_percorso_test=[]
    while((Autonomia_drone_attuale>0)&(Peso_trasportato_attuale<=Capacita)&(len(lista_visitati)<numero_clienti)):
        
        #creo la lista dei vicini
        #region
        neihgbourlist=[]
        
        for i in range(1,numero_clienti_range):
                neihgbourlist.append(dist_drone[nodo_attuale_drone][i])
            
        # e ne trovo il più vicino
        indice_vicino=piu_vicino(neihgbourlist,lista_visitati)

        #endregion      
        #Provo se il drone riesce a raggiungere il nodo più vicino
        Autonomia_drone_attuale=Autonomia_drone_attuale-dist_drone[nodo_attuale_drone][indice_vicino]
        Peso_trasportato_attuale=Peso_trasportato_attuale+lista_pesi_pacchi[indice_vicino]
        #a questo punto ho 2 possibilità: 
            # 1 il drone riesce a raggiungere il nodo più vicino(if) 
            # 2 oppure no (else)
        #1
        # se riesce aggiungo l'arco al grafo del drone
        if((Autonomia_drone_attuale>=0)&(Peso_trasportato_attuale<=Capacita)):
            Drone_on_truck=0
            Drone_spostato=1
            Grafo_drone.add_edge(nodo_attuale_drone,indice_vicino,color='blue')
            Drone_percorso_test.append(indice_vicino)
            Movimenti_drone+=1
            Costo_drone+=dist_drone[nodo_attuale_drone][indice_vicino]
            lista_visitati.append(indice_vicino)
            nodo_attuale_drone=indice_vicino
            indice_vicino_precedente=indice_vicino
        #2 se il drone non riesce a raggiungere ul nodo più vicino: 3 possibilità
            #1 se il drone si è spostato e ha fatto un solo movimento mando il truck nel nodo dove si trova il drone 
            #2 il drone si è spostao con più di 1 movimento
            #3 se il drone NON si è spostato mando il truck nel nodo più vicino
        else:
            # 1 il drone si è spostao ed è riusciuto a fare solo un movimento → annullo il movimento
            if((Movimenti_drone<=1)&(Drone_spostato)):
                Grafo_drone.remove_edge(nodo_attuale_truck,nodo_attuale_drone)
                Drone_spostato=0
                nodo_attuale_drone=nodo_attuale_truck
                lista_visitati.remove(indice_vicino_precedente)
                indice_vicino=indice_vicino_precedente
                Drone_on_truck=1
            # 2 se il drone si è spostato e ha fatto più di un movimento controllo che arrivi dopo del truck,
            # se cosi è procedo all if(drone_spostato) e mando il truck dal drone
            # se il truck arriverebbe dopo il drone controllo a ritroso i nodi percorso dal drone fino a trovarne
            # uno accettabile oppure fino a che ho annullato tutte le mosse 
            if((Movimenti_drone>1)&(Drone_spostato)):
                Truck_prima_del_drone=Costo_drone>dist_truck[nodo_attuale_truck][nodo_attuale_drone]
                #Se arriva prima il drone provo il nodo precedente
                #lenghth=len(Drone_percorso_test)
                while((Truck_prima_del_drone==False)&(not(Drone_on_truck))):
                    #finche ho almeno 2 nodi serviti dal drone
                    if(len(Drone_percorso_test)>=2):
                        Ultimo_nodo_drone=Drone_percorso_test[-1]
                        Penultimo_nodo_drone=Drone_percorso_test[-2]
                    #se rimane solo un nood servito dal drone sicuramente il truck arriva dopo(o nello stesso istante)
                    #e il drone non esegue quindi nessuno spostamento
                    else:
                        Ultimo_nodo_drone=Drone_percorso_test[-1]
                        Penultimo_nodo_drone=nodo_attuale_truck
                        Drone_on_truck=1
                        Drone_spostato=0
                    Grafo_drone.remove_edge(Penultimo_nodo_drone,Ultimo_nodo_drone)
                    nodo_attuale_drone=Penultimo_nodo_drone
                    lista_visitati.remove(Ultimo_nodo_drone)
                    Drone_percorso_test.remove(Ultimo_nodo_drone)
                    Costo_drone=Costo_drone-dist_drone[Ultimo_nodo_drone][Penultimo_nodo_drone]
                    Truck_prima_del_drone=Costo_drone>dist_truck[nodo_attuale_truck][nodo_attuale_drone]

                #se non ho annullato tutte le mosse e il drone si è spostato
                if(Drone_spostato):
                    Grafo_truck.add_edge(nodo_attuale_truck,nodo_attuale_drone,color='r')
                    nodo_attuale_truck=nodo_attuale_drone
                    Costo+=dist_truck[nodo_attuale_truck][nodo_attuale_drone]
                    Drone_on_truck=1
                    if(not(nodo_attuale_drone in lista_visitati)):
                        lista_visitati.append(nodo_attuale_drone)
                    
                
            #3 altrimenti se il drone non si è spostato
            if(not(Drone_spostato)):
                #region
                #creo la lista dei vicini
                neihgbourlist=[]
                for i in range(1,numero_clienti_range):
                        neihgbourlist.append(dist_truck[nodo_attuale_drone][i])
                    
                # e ne trovo il più vicino
                indice_vicino=piu_vicino(neihgbourlist,lista_visitati)
                #endregion
                Grafo_truck.add_edge(nodo_attuale_truck,indice_vicino,color='r')
                Costo+=dist_truck[nodo_attuale_truck][indice_vicino]
                Drone_on_truck=1 
                if(not(indice_vicino in lista_visitati)):
                    lista_visitati.append(indice_vicino)
    
    #controllo che nell' ultimo nodo il truck arrivi prima del drone
        
    #infine ricarica drone
    Autonomia_drone_attuale=Autonomia_drone

    #Qua sto uscnedo dal ciclo con l'ultino cliente servito dal drone
    if((not(len(lista_visitati)<30))&(Drone_on_truck==0)):
        Grafo_truck.add_edge(nodo_attuale_truck,nodo_attuale_drone,color='r')
        Costo+=dist_truck[nodo_attuale_truck][indice_vicino]
        Drone_on_truck=1 
        if(not(indice_vicino in lista_visitati)):
            lista_visitati.append(indice_vicino)
    if(Drone_spostato):
        nodo_attuale_truck=nodo_attuale_drone
    else:
        nodo_attuale_truck=indice_vicino
        nodo_attuale_drone=nodo_attuale_truck
    Drone_spostato=0
    len_lista=len(lista_visitati)
    print("indici visitati:",len_lista)
 


print("Scaricando l'istanza, creando il grafo")
#aggiungo l'arco finale
Grafo_truck.add_edge(nodo_attuale_truck,random,color='r')
Costo=Costo+dist_truck[nodo_attuale_truck][random]
pos = nx.get_node_attributes(Grafo_drone, 'pos')

#setto colore grafo
color_map=[]
for node in Grafo_drone:
    if node == random:
        color_map.append('red')
    else: 
        color_map.append('green') 
     

#stampa grafi
#plt.figure(1)
nx.draw_networkx_edges(Grafo_truck, points, arrowsize=20)  # create a graph with the tour  # create a graph with the tour

#plt.figure(2)
edges_drone = Grafo_drone.edges()
#label = nx.get_node_attributes(Grafo_drone, 'label') 
colors = [Grafo_drone[u][v]['color'] for u,v in edges_drone]
#nx.draw(Grafo_drone,points,labels=label,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
nx.draw(Grafo_drone,points,font_size=10, node_size=100,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)
#plt.figure(3)
G3 = nx.compose(Grafo_drone, Grafo_truck)
edges = G3.edges()
colors = [G3[u][v]['color'] for u,v in edges]
#nx.draw(G3,points, labels=label,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
nx.draw(G3,points,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
#per stampare le distanze nx.draw_networkx_edge_labels(Grafo, pos)
print("Costo=",Costo)

plt.show()          # display it interactively