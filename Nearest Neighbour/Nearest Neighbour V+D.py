#Importazione librerie
import re #Libreria per leggere i file dati in input
import networkx as nx #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes import graph
import numpy as np
import random
import json

#classe che identifica una coppia di nodi senza archi tra di essi
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

#classe per rimuovere archi (da chiamare dopo avere fatto il controllo di capacità e autonomia)
class Custom_Graph(nx.Graph):
    def custom_remove_edge(self,node1,node2,solution):
        if self.has_edge(node1,node2):
            self.remove_edge(node1,node2)
        elif self.has_edge(node2,node1):
            self.remove_edge(node2,node1)
        else:
            solution
            #print_graph_for_debug(solution)
            raise CustomError_noedges(str(node1)+" "+str(node2))

#funzione che unisce il grafo del Truck con quello del Drone
def print_graph_for_debug(solution):
    graph_total = nx.compose(graph_truck,graph_drone)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    visited_list_truck=solution[0]
    visited_list_drone=[]
    drone_paths=[path for path in solution if solution.index(path)!=0]
    for path in solution:
        if solution.index(path)!=0:
            visited_list_drone+=path
    #creo i colori dei nodi
    color_map=[]
    for node in graph_total:
        if (node == starting_node): 
            color_map.append('#ff8000')
        elif (node in visited_list_truck): 
            color_map.append('#d16e66')
        elif (node in visited_list_drone): 
            index=[i for i, path in enumerate(drone_paths) if node in path]
            color_map.append(paths_colors[index[0]+1])
        else: 
            color_map.append('green') 
    #colori degli archi aggiunti ogni volta che faccio "add edge"
    
    figure.canvas.manager.window.wm_geometry("+%d+%d" % (-10, 00)) #da una grandezza standard alla figura
    plt.clf()   #clearo il grafico precedente
    nx.draw(graph_total,points,font_size=9, node_size=170,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
    labels = nx.get_edge_attributes(graph_total, 'length') 
    #per stampare le distanze
    nx.draw_networkx_edge_labels(graph_total,points, edge_labels=labels, font_size=7)
     
    
    plt.show()         #stampa il grafico 

#funzione che determina il nodo più vicino al nodo corrente
def piu_vicino(neihgbourlist,lista_visitati):
    first_time=1
    indice_minimo=-1
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

#funzione che ritorna il costo speso dal Truck
def compute_solution_cost(path_truck):    
    cost=0
    for i in range (len(path_truck)-1):
        cost+=dist_truck[path_truck[i]][path_truck[i+1]]
    cost+=dist_truck[path_truck[i+1]][path_truck[0]]
    return cost



#Grafi
graph_drone = nx.Graph()
graph_truck = nx.Graph()

#----------INIZIO Lettura file nodi----------------
filename = 'Posizioni_clienti.txt'      #nome file puntatore
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
        #graph_drone.add_node(indice,label=label, pos=(coord_x, coord_y))
        graph_drone.add_node(indice, pos=(coord_x, coord_y))

        
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

    #CREAZIONE matrice TRUCK
    if dist_section:   
        coord = line.split(' ')
        for j in range(0,numero_clienti):
            dist_truck[i][j+1] = float(coord[j])
    i+=1
istanza.close()

#dist_truck[25][12]=3000
#dist_truck[25][13]=5
#decido il nodo di partenza
starting_node=29
lista_pesi_pacchi[starting_node]=0

#setto il peso del deposito=0
#label=str(starting_node)+":"+str(0)
#nx.set_node_attributes(graph_drone ,{starting_node:str(label)},'label' )

#random.randint(0,30)
nodo_attuale_truck=starting_node
nodo_attuale_drone=starting_node
lista_visitati=[starting_node]
solution=[[starting_node]]

Drone_on_truck=1
Drone_spostato=0
#vincoli drone
Autonomia_drone=35
Capacita=300
autonomia_drone_attuale=Autonomia_drone
drone_cycle_number=0

paths_colors=['red','#7C69FF','#00EB2D','#DDD900','#928017','#A1B1F8','#9DFD83','#8CFF00',\
'#C6FF00','#0040FE','#5B998D','#A36CB1 ','#687044','#B391CB','#27670C']
figure=plt.figure(figsize=(9.5,9.5))

#ciclo esterno , quando esco aggiungo solo l'arco finale e stampo
while(len(lista_visitati)<numero_clienti):
    drone_cycle_number+=1
    solution.append([])
#region
    #creo la lista dei vicini
    neihgbourlist=[]
    for i in range(1,numero_clienti_range):
            neihgbourlist.append(dist_drone[nodo_attuale_drone][i])
        
    # e ne trovo il più vicino
    indice_vicino=piu_vicino(neihgbourlist,lista_visitati)
    solution[drone_cycle_number].append(nodo_attuale_drone)
#endregion
    Costo_drone=0
    Movimenti_drone=0
    peso_trasportato_attuale=0
    #Sotto-ciclo drone, posso uscire se finisce l'autonomia,supero la capacità o se visito l'ultimo nodo con il drone
    Drone_percorso_test=[]
    
    #verifica vincoli
    while((autonomia_drone_attuale>0)&(peso_trasportato_attuale<=Capacita)&(len(lista_visitati)<numero_clienti)):
        
        #creo la lista dei vicini
        #region
        neihgbourlist=[]
        
        for i in range(1,numero_clienti_range):
                neihgbourlist.append(dist_drone[nodo_attuale_drone][i])
            
        # e ne trovo il più vicino
        indice_vicino=piu_vicino(neihgbourlist,lista_visitati)
        

        #endregion      
        #Provo se il drone riesce a raggiungere il nodo più vicino
        autonomia_drone_attuale=autonomia_drone_attuale-dist_drone[nodo_attuale_drone][indice_vicino]
        print("sto provando a fare",nodo_attuale_drone,indice_vicino)
        peso_trasportato_attuale=peso_trasportato_attuale+lista_pesi_pacchi[indice_vicino]
        #a questo punto ho 2 possibilità: 
            # 1 il drone riesce a raggiungere il nodo più vicino(if) 
            # 2 oppure no (else)
        #1
        # se riesce aggiungo l'arco al grafo del drone
        if((autonomia_drone_attuale>=0)&(peso_trasportato_attuale<=Capacita)):
            Drone_on_truck=0
            Drone_spostato=1
            graph_drone.add_edge(nodo_attuale_drone,indice_vicino,color=paths_colors[drone_cycle_number])
            solution[drone_cycle_number].append(indice_vicino)
            #print_graph_for_debug(solution)
            Drone_percorso_test.append(indice_vicino)
            Movimenti_drone+=1
            Costo_drone+=dist_drone[nodo_attuale_drone][indice_vicino]
            lista_visitati.append(indice_vicino)
            nodo_attuale_drone=indice_vicino
            indice_vicino_precedente=indice_vicino
        #2 se il drone non riesce a raggiungere il nodo più vicino: 3 possibilità
            #1 se il drone si è spostato e ha fatto un solo movimento mando il truck nel nodo dove si trova il drone 
            #2 il drone si è spostato con più di 1 movimento
            #3 se il drone NON si è spostato mando il truck nel nodo più vicino
        else:
            print("Autonomia: ",autonomia_drone_attuale)
            print("Peso: ",peso_trasportato_attuale)
            # 1 il drone si è spostao ed è riusciuto a fare solo un movimento → annullo il movimento e ci mando il Truck
            if((Movimenti_drone<=1)&(Drone_spostato)):
                graph_drone.custom_remove_edge(nodo_attuale_truck,nodo_attuale_drone)
                solution[drone_cycle_number].clear()
                #print_graph_for_debug(solution)
                Drone_spostato=0
                nodo_attuale_drone=nodo_attuale_truck #ci mando il Truck
                lista_visitati.remove(indice_vicino_precedente)
                indice_vicino=indice_vicino_precedente
                Drone_on_truck=1
            # 2 se il drone si è spostato e ha fatto più di un movimento controllo che arrivi dopo il Truck,
            # se cosi è procedo all' if(drone_spostato) e mando il Truck dal Drone
            # se il truck arriverebbe dopo il drone controllo a ritroso i nodi percorso dal drone fino a trovarne
            # uno accettabile oppure fino a che ho annullato tutte le mosse 
            if((Movimenti_drone>1)&(Drone_spostato)):
                Truck_prima_del_drone=Costo_drone>dist_truck[nodo_attuale_truck][nodo_attuale_drone]
                #Se arriva prima il drone provo il nodo precedente
                #lenghth=len(Drone_percorso_test)
                while((Truck_prima_del_drone==False)&(not(Drone_on_truck))):
                    #finche ho almeno 2 nodi serviti dal drone
                    if(len(Drone_percorso_test)>=2):
                        Ultimo_nodo_drone=Drone_percorso_test[-1] #ultimo elemento
                        Penultimo_nodo_drone=Drone_percorso_test[-2] #penultimo nodo
                    #se rimane solo un nodo servito dal drone sicuramente il truck arriva dopo(o nello stesso istante)
                    #e il drone non esegue quindi nessuno spostamento
                    else:
                        Ultimo_nodo_drone=Drone_percorso_test[-1]
                        Penultimo_nodo_drone=nodo_attuale_truck
                        Drone_on_truck=1
                        Drone_spostato=0
                    graph_drone.custom_remove_edge(Penultimo_nodo_drone,Ultimo_nodo_drone)
                    solution[drone_cycle_number].pop(-1) #pop è come remove, ma lo restituisce anche
                    #print_graph_for_debug(solution)
                    nodo_attuale_drone=Penultimo_nodo_drone
                    lista_visitati.remove(Ultimo_nodo_drone)
                    Drone_percorso_test.remove(Ultimo_nodo_drone)
                    Costo_drone=Costo_drone-dist_drone[Ultimo_nodo_drone][Penultimo_nodo_drone]
                    Truck_prima_del_drone=Costo_drone>dist_truck[nodo_attuale_truck][nodo_attuale_drone]

                #se non ho annullato tutte le mosse e il drone si è spostato
                if(Drone_spostato):
                    graph_truck.add_edge(nodo_attuale_truck,nodo_attuale_drone,color='r')
                    solution[0].append(nodo_attuale_drone) #aggiungo alla lista del Truck
                   # print_graph_for_debug(solution)
                    nodo_attuale_truck=nodo_attuale_drone
                    Drone_on_truck=1
                    if(not(nodo_attuale_drone in lista_visitati)):
                        lista_visitati.append(nodo_attuale_drone)
                    
                
            #3 altrimenti se il drone non si è spostato -> mando il Truck al nodo più vicino
            if(not(Drone_spostato)):
                #region
                #creo la lista dei vicini
                neihgbourlist=[]
                for i in range(1,numero_clienti_range):
                    neihgbourlist.append(dist_truck[nodo_attuale_drone][i])
                    
                # e ne trovo il più vicino
                indice_vicino=piu_vicino(neihgbourlist,lista_visitati)
                #endregion
                graph_truck.add_edge(nodo_attuale_truck,indice_vicino,color='r')
                solution[0].append(indice_vicino)
                #print_graph_for_debug(solution)
                Drone_on_truck=1 
                if(not(indice_vicino in lista_visitati)):
                    lista_visitati.append(indice_vicino)
                solution[drone_cycle_number].clear()
        
        
    #infine ricarica drone
    autonomia_drone_attuale=Autonomia_drone

    #Qua sto uscendo dal ciclo con l'ultimo cliente servito dal drone
    if((not(len(lista_visitati)<30))&(Drone_on_truck==0)):
        graph_truck.add_edge(nodo_attuale_truck,nodo_attuale_drone,color='r')
        solution[0].append(nodo_attuale_drone)
        #print_graph_for_debug(solution)
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
    #print("indici visitati:",len_lista)
 


print("Scaricando l'istanza, creando il grafo")
#aggiungo l'arco finale
graph_truck.add_edge(nodo_attuale_truck,starting_node,color='r')
solution[0].append(starting_node)

with open('2_OPT_input.txt', 'w') as Two_opt_input:
    Two_opt_input.writelines(str(starting_node)+"\n")
    Two_opt_input.writelines(str(Autonomia_drone)+"\n")
    Two_opt_input.writelines(str(Capacita)+"\n")
    json.dump(solution, Two_opt_input)

visited_list_truck=solution[0]
cost=compute_solution_cost(visited_list_truck)
print("Nodo di partenza: "+str(starting_node))
print("Costo: ",cost) #costo Truck
print("La soluzione del problema con la Nearest Neighbour è: ", solution)


print_graph_for_debug(solution)