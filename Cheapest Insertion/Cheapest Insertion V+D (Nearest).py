#IMPORTAZIONE LIBRERIE
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes.function import neighbors 
import numpy as np     
from typing import Any, List

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

class Custom_Graph(nx.Graph):
    def custom_remove_edge(self,node1,node2):
        if self.has_edge(node1,node2):
            self.remove_edge(node1,node2)
        elif self.has_edge(node2,node1):
            self.remove_edge(node2,node1)
        else:
            raise CustomError_noedges(str(node1)+" "+str(node2))
        
def print_graph_for_debug():
    graph_total = nx.compose(graph_drone, graph_truck)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    
    #creo i colori dei nodi
    color_map=[]
    for node in graph_total:
    
            if (node == truck_node_index): 
                color_map.append('red')
            elif (node in visited_list_truck_indexes): 
                color_map.append('white')
            else: 
                color_map.append('green') 
    #colori degli archi aggiunti ogni volta vh faccio add edge

    plt.clf()   #clearo il grafico precedente
    nx.draw(graph_total,points,font_size=10, node_size=200,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
    #per stampare le distanze nx.draw_networkx_edge_labels(Grafo, pos)
    
    plt.show()         # display it interactively   

#classe per salvare i sotto cicli del drone
class Visited_node_drone:
    def __init__(self, index, trip_number):
        self.index = index
        self.trip_number = trip_number

#Ricerca del nodo più vicino 
def nearest_node(neighbors_distance,visited_list_indexes):
    first_time=1
    for i in range(1,len(neighbors_distance)):  
        #se la distanza non è zero e il nodo non è nella lista dei visitati
        if(not(i in visited_list_indexes)):
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

def find_best_edge(graph, dist, trip_number):
    #per ogni coppia di nodi cerco il nodo con costo minore tale che la
    #somma dei nuovi archi sia minima

    #scorro gli archi
    first_time=1
    for node1,node2,attributes in graph.edges(data=True):

        # controllo se entrambi i 2 nodi sono stati visitati in questo ciclo
        if ((any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):
            #scorro i nodi
            for i in range(1,client_number_range):  
                #se il nodo non è nella lista dei visitati
                if(not(i in visited_list_indexes)):
                    #calcolo il costo di questo nodo, 
                    #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
                    new_edge_cost=(dist[i][node1]) + (dist[i][node2])
                    actual_index=i
                    old_edge_cost=dist[node1][node2]
                    actual_cost=compute_solution_cost(dist)-old_edge_cost+new_edge_cost

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

def compute_solution_cost(dist):    
    cost=0
    for node1,node2,attributes in graph_truck.edges(data=True):
        cost+=dist[node1][node2]
    return cost

def compute_drone_cost(trip_number):
    cost=0
    possible_truck_movements=[]
    
    #nodi visitati in questo viaggio
    # per ogni nodo negli archi del drone
    for node1,node2,attributes in graph_drone.edges(data=True):
        # controllo se entrambi i 2 nodi sono stati visitati in questo ciclo
        if ((any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):  
            cost+=dist_drone[node1][node2]
            #print(node1,node2,dist_drone[node1][node2],cost)

    possible_truck_movements_1=[nodeB for nodeA,nodeB,attributes in graph_drone.edges(data=True) if nodeA==truck_node_index]
    possible_truck_movements_2=[nodeA for nodeA,nodeB,attributes in graph_drone.edges(data=True) if nodeB==truck_node_index]
    possible_truck_movements_all=possible_truck_movements_1+possible_truck_movements_2
    for node in possible_truck_movements_all:
        if (any(x.index == node and x.trip_number==trip_number for x in visited_list_drone)):
            possible_truck_movements.append(node)
        
    #print(possible_truck_movements)
    #mi salvo in una lista il costo della strada e il realtivo tratto che verra effettuato dal truck
    cost_routes=[]
    for i in range(len(possible_truck_movements)):
        #route avra (costo se il truck va a quel nodo, nodo)
        route=[(cost-dist_drone[truck_node_index][possible_truck_movements[i]]),possible_truck_movements[i]]
        cost_routes.append(route)
    return cost_routes

def find_best_drone_route(cost_routes):
    #spiegare come vengono calcolati i 2 costi possibli, scelgo quello maggiore
    if len(cost_routes)<2:  
        return cost_routes[0]

    if(cost_routes[0][0]>=cost_routes[1][0]):
        return cost_routes[0]
    else:
        return cost_routes[1]

#Creazione grafi
graph_truck = nx.Graph()  
graph_drone = Custom_Graph()    

#----------Inizio lettura coordinate e inserimento nel grafo e distanze drone-------------
#region
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
coord_section = False
points = {}


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
        graph_truck.add_node(index, pos=(coord_x, coord_y))
client_number=index
client_number_range=client_number+1  
istance.close()

#Inizializzo la matrice delle distanze del drone
dist_drone = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice del drone
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist_drone[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)

#endregion

#----------Inizio Lettura file distanze truck----------------
#region
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
#endregion

#Decido il nodo di partenza, ovvero il nostro deposito. 
starting_node = 17
truck_node_index = starting_node

#Dichiaro la lista dei nodi visitati durante l'algoritmo
visited_list_indexes = [starting_node]
#Dichiaro la lista dei nodi visitati dal truck durante l'algoritmo
visited_list_truck_indexes = [starting_node]

cost = 0    #costo iniziale del veicolo
drone_on_truck=1
drone_autonomy=35
capacity=100

visited_list_drone=[]

# conto quanti viaggi fa il drone
drone_trip_counter=0
# conto quanti clienti fa il drone
drone_clients_counter=0

#-------FINE INIZIALIZZAZIONE-------



#ciclo esterno del truck
first_time=1
last_node=0
while((len(visited_list_indexes)<client_number)):
    drone_trip_counter+=1
    sub_clients_counter=0
    drone_autonomy_temp=drone_autonomy
    drone_returned=False

    #Creo la lista con le distanze dei vicini
    neighbors_distance = [0]
    for i in range(1, client_number_range): 
        neighbors_distance.append(dist_drone[truck_node_index][i])
    #Inserisco in nearest_index il nodo più vicino al truck
    nearest_index = nearest_node(neighbors_distance, visited_list_indexes)

    #ciclo interno del drone
    while((len(visited_list_indexes)<client_number) and (drone_returned==False)):
        # conto quanti clienti sta servendo il drone in questo viaggio
        visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==drone_trip_counter]
        sub_clients_counter=len(visited_list_drone_this_trip)
        drone_clients_counter=len(visited_list_drone)
        #clienti serviti dal drone e relativo ciclo


        #1 caso: il drone non si è mosso , se non riesce a farne neanche 1 mando il truck
        if(sub_clients_counter==0 ):
            #Aggiungo il primo arco, dal nodo di partenza al nodo piu vicino
            graph_drone.add_edge(truck_node_index,nearest_index,length=round(dist_truck[truck_node_index][nearest_index],2),color='b')
            #mi salvo i 2 nodi  e il relativo ciclo
            #(dato che e il primo passo devo aggiungere sia il nodo di partenza che di arrivo)
            visited_list_indexes.append(nearest_index)
            visited_list_drone.append(Visited_node_drone(truck_node_index,drone_trip_counter))
            visited_list_drone.append(Visited_node_drone(nearest_index,drone_trip_counter))
            drone_clients_counter=len(visited_list_drone)
            #print("il drone sta provando il "+str(sub_clients_counter+1)+" nodo del "+str(drone_trip_counter)+" viaggio: "+str(visited_list_drone[drone_clients_counter-1].index))

            #se non riesce a fare neanche un movimento(o sarebbe l' ultimo nodo) elimino l arco e mando il truck, uscendo dal ciclo
            if(drone_autonomy<dist_drone[truck_node_index][nearest_index] or last_node): 
                graph_drone.custom_remove_edge(truck_node_index,nearest_index)
                visited_list_drone = [node for node in visited_list_drone if node.index!=truck_node_index]
                visited_list_drone = [node for node in visited_list_drone if node.index!=nearest_index]
                graph_truck.add_edge(truck_node_index,nearest_index,length=round(dist_truck[truck_node_index][nearest_index],2),color='r')
                visited_list_truck_indexes.append(nearest_index)
                drone_clients_counter=len(visited_list_drone)
                #print("FALLITO MANDO IL TRUCK AL NODO"+str(nearest_index))               
                truck_node_index=nearest_index
                drone_returned=True
                #esco dal ciclo del drone
            else:
                #altrimenti se riesce af are il primo movimento procedo
                #print("RIUSCITO")
                #skippo il resto del ciclo VALUTARE SE LASCIARE O NO
                #continue
                pass

            
        #2 caso, il drone si è spostato gia una volta, questa sarebbe la 2 almeno
        if(sub_clients_counter>=1):
            
            #controllo se il drone può fare solo un nodo: sono gia a 1 nodo, quindi provo ad aggiungerenbe un altro e vedo se riesco a completare il percorso
            #aggiungo l arco piu conveniente    
            best_node_index,node1_best,node2_best=find_best_edge(graph_drone,dist_drone,drone_trip_counter)
            #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
            #quindi lo aggiungo e rimuovo l edge corrispondente
            graph_drone.add_edge(best_node_index,node1_best,length=round(dist_truck[best_node_index][node1_best],2),color='b')
            graph_drone.add_edge(best_node_index,node2_best,length=round(dist_truck[best_node_index][node2_best],2),color='b')
            visited_list_indexes.append(best_node_index)
            visited_list_drone.append(Visited_node_drone(best_node_index,drone_trip_counter))

            #rimuovo solo se non sono al 2 ciclo, senno per la storia del undirected eliminerei il primo arco
            if(sub_clients_counter!=2):
                graph_drone.custom_remove_edge(node1_best,node2_best)

            #trovo le 2 strade senzxa arco rimosso
            cost_routes=compute_drone_cost(drone_trip_counter)
            #trovo il costo e il nodo da rimuovere della strada migliore
               
            if(not last_node):
                drone_clients_counter=len(visited_list_drone)
                #print("il drone sta provando il "+str(sub_clients_counter)+" nodo del "+str(drone_trip_counter)+" viaggio: "+str(visited_list_drone[drone_clients_counter-1].index))
                best_drone_route_cost=find_best_drone_route(cost_routes)
                
            else:
                #print("ULTIMO NODO: "+str(starting_node))
                if(cost_routes[0][1]==starting_node):
                    best_drone_route_cost = cost_routes[0]
                    best_drone_route_cost_2 = cost_routes[1]
                else:
                    best_drone_route_cost = cost_routes[1]
                    best_drone_route_cost_2 = cost_routes[0]

                #if((drone_autonomy<best_drone_route_cost[0]) or (best_drone_route_cost[0]<dist_truck[truck_node_index][best_drone_route_cost[1]])):
                    #significa che non riesco ad aggiungere l' ultimo nodo come ultimo visitato dal drone, quindi lo rimuovo 
                

            #se il costo è maggiore della autonomia, o il drone arriverebbe prima del truck, rimuovo i due archi fatti, ripristinando quello precedente e mando il truck al nodo migliore,
            #altrimenti proseguo
            if((drone_autonomy<best_drone_route_cost[0]) or (best_drone_route_cost[0]<dist_truck[truck_node_index][best_drone_route_cost[1]])):                  
                
                fail_cause=""
                if(drone_autonomy<best_drone_route_cost[0]):
                    fail_cause+=" Autonomia insufficiente "
                if(best_drone_route_cost[0]<dist_truck[truck_node_index][best_drone_route_cost[1]]):
                    fail_cause+=" Arriverebbe prima il drone "
                
                #rimuovo i due archi che mi hganno portato a superare l ' autonomia e ripristino il precedente 
                graph_drone.custom_remove_edge(best_node_index,node1_best)
                graph_drone.custom_remove_edge(best_node_index,node2_best)
                graph_drone.add_edge(node1_best,node2_best,length=round(dist_truck[node1_best][node2_best],2),color='b')
                
                #se sono all'utlim ociclo ed entro qua significa che non riesco a raggiungere il nodo finale con il truck mentre il drone fa il giro, devo ricalcolare la srtada migliore, ho gia escluso lo starting node
                if(last_node):
                    cost_routes=compute_drone_cost(drone_trip_counter)
                    best_drone_route_cost=find_best_drone_route(cost_routes)

                #print("FALLITO, MANDO IL TRUCK AL NODO "+str(best_drone_route_cost[1])+"("+str(fail_cause)+")") 

                #aggiungo l 'arco che fara il truck e lo rimuovo dal grafo del drone
                graph_truck.add_edge(truck_node_index,best_drone_route_cost[1],length=round(dist_truck[truck_node_index][best_drone_route_cost[1]],2),color='r')
                #lo rimuovo solo se dove andra il truck non e l ultimo nodo aggiunto, dat oche  e gia stato eliminato l' arco relativo
                if(best_node_index!=best_drone_route_cost[1]):
                    graph_drone.custom_remove_edge(truck_node_index,best_drone_route_cost[1])
                    visited_list_indexes.remove(best_node_index)

                visited_list_truck_indexes.append(best_drone_route_cost[1])
                truck_node_index=best_drone_route_cost[1]
                # rimuovo il nodo non visitato dalle liste
                
                visited_list_drone = [node for node in visited_list_drone if node.index!=best_node_index]

                if(last_node):  
                    graph_truck.add_edge(best_drone_route_cost[1],starting_node,length=round(dist_truck[best_drone_route_cost[1]][starting_node],2),color='r')
                    visited_list_truck_indexes.append(starting_node)
                    visited_list_indexes.append(starting_node)
                    #print("AGGIUNGO L'ULTIMO ARCO: DA "+str(best_drone_route_cost[1])+" A "+str(starting_node)) 
                    truck_node_index=starting_node

                #esco dal ciclo del drone
                drone_returned=True
            else:
                #print("RIUSCITO")
                if(last_node):
                    graph_drone.custom_remove_edge(truck_node_index,starting_node)
                    graph_truck.add_edge(truck_node_index,starting_node,length=round(dist_truck[truck_node_index][starting_node],2),color='r')
                    truck_node_index=starting_node


        #se ho fatto tutti i nodi 
        if(not last_node and len(visited_list_indexes)==client_number):
            if(drone_returned==False):
                visited_list_drone.remove(visited_list_drone[0])           
                drone_clients_counter=len(visited_list_drone)
            visited_list_indexes.remove(starting_node)
            last_node=1
        

        visited_list_drone_indexes=[node.index for node in visited_list_drone]
        
        #print_graph_for_debug()


    
    cost=compute_solution_cost(dist_truck)
    #print_graph_for_debug()
    

# # a questo punto ho finito, non mi basta che aggiungere l'ultimo arco del truck

#per stampare le distanze nx.draw_networkx_edge_labels(Grafo, pos)
cost=compute_solution_cost(dist_truck)
print("Costo=",cost)
print("Nodo iniziale=",starting_node)
print("Autonomia drone", drone_autonomy)
print_graph_for_debug()




