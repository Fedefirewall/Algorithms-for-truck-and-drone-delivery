#IMPORTAZIONE LIBRERIE
from os import path
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.algorithms.centrality.eigenvector import eigenvector_centrality_numpy
from networkx.classes.function import neighbors 
import numpy as np 
import random

#Creazione grafi
Graph_truck_CC = nx.Graph()     #Grafo completamente connesso
Graph_truck_MST = nx.Graph()    #Grafo dell'MST
Graph_truck_OV = nx.Graph()     #Grafo con i nodi dispari dopo MST
Graph_truck_MWM = nx.Graph()    #Grafo Minimum weight matching dei nodi dispari.
Graph_truck_ET = nx.Graph()     #Grafo Eulerian Tour dove i nodi dispari sono diventati pari
Graph_truck_Final = nx.Graph() #Grafo finale

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

paths_colors=['red','#F7AE5D','#5B998D','#DDD900','#928017','#A1B1F8','#9DFD83','#408446',\
'#C7DA88','#0040FE','#A520A5','#A36CB1 ','#687044','#B391CB','#46822D']
figure=plt.figure(figsize=(9.5,9.5))

#Creazione grafi
graph_truck = Custom_Graph()  
graph_drone = Custom_Graph()    

#----------Inizio lettura coordinate e inserimento nel grafo e distanze drone-------------
#region
filename = 'Posizione_nodi_DRONE.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
coord_section = False
points = {}
weights_dict = {}

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
        weight= float(coord[3])
        weights_dict[index]=weight
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
#endregion

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
    labels = nx.get_edge_attributes(graph_total, 'length') 
    #nx.draw_networkx_edge_labels(graph_total,points, edge_labels=labels)
    
    plt.show()         # display it interactively   

def print_graph_for_debug_NEW(solution):
    
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
    #colori degli archi aggiunti ogni volta vh faccio add edge
    
    figure.canvas.manager.window.wm_geometry("+%d+%d" % (-10, 00))
    plt.clf()   #clearo il grafico precedente
    nx.draw(graph_total,points,font_size=8, node_size=120,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
    labels = nx.get_edge_attributes(graph_total, 'length') 
    #per stampare le distanze
    nx.draw_networkx_edge_labels(graph_total,points, edge_labels=labels, font_size=7)
     
    
    plt.show()         # display it interactively 

def compute_visited_list_truck():
    visited_list_truck_indexes_1=[node1 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_2=[node2 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes=visited_list_truck_indexes_1+visited_list_truck_indexes_2
    visited_list_truck_indexes=list(set(visited_list_truck_indexes))
    return visited_list_truck_indexes

def compute_visited_list():
    visited_list_truck_indexes_1=[node1 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_2=[node2 for node1,node2 in graph_truck.edges]
    visited_list_truck_indexes_3=[node1 for node1,node2 in graph_drone.edges]
    visited_list_truck_indexes_4=[node2 for node1,node2 in graph_drone.edges]
    visited_list_truck_indexes=visited_list_truck_indexes_1+visited_list_truck_indexes_2+visited_list_truck_indexes_3+visited_list_truck_indexes_4
    visited_list_truck_indexes=list(set(visited_list_truck_indexes))
    return visited_list_truck_indexes
#Ricerca del nodo più vicino 

def nearest_node(neighbors_distance,visited_list_indexes):
    min_value=10000000
    for i in range(1,len(neighbors_distance)):  
        #se la distanza non è zero e il nodo non è nella lista dei visitati
        if(not(i in visited_list_indexes)):
            actual_value=neighbors_distance[i]
            actual_index=i
            if(actual_value<min_value):
                min_value=actual_value
                min_index=actual_index
    return min_index

def add_node_shortest_detour(solution, edges_full, node_input):
    min_path_index=-1
    
    #cerco il posto migliore per inserire il nodo, tale che il detour sia minimo
    if edges_full=="full":
        pass
    if edges_full=="free":
        pass
    diff_min=100000000000
    for path_output in legal_output_paths:

        truck_path=solution
        #scorro gli archi
        for edge in path_edges:
            node1=edge[0]
            node2=edge[1]
            #calcolo il costo di questa prova, 
            #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
            #e tolgo l arco rimosso
            
            #se il path output é del truck ed é un arco libero(da un estremo all altro non ce un percorso del drone)
            
            if path_output_index==0 and edge_free(solution,node1,node2):
                new_edges_cost=(dist_truck[node_input][node1]) + (dist_truck[node_input][node2])
                old_edge_cost=dist_truck[node1][node2]
                #penalizzo la scelta di aggiugere al truck il nodo
                actual_diff=new_edges_cost-old_edge_cost+10000
                actual_cost=0
                actual_weight=0
            #se il path_output é del drone e l'arco non é del truck(perché un arco del truck ha i nodi visitati dal path del drone) 
            elif((node1 in solution[0] and node2 in solution[0])==False ):
                new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2])
                old_edge_cost=dist_drone[node1][node2]
                actual_diff=new_edges_cost-old_edge_cost
                actual_cost=compute_path_drone_cost(path)-old_edge_cost+new_edges_cost
                actual_weight=compute_drone_weight(path)+weights_dict[node_input]
            else:
                # se non considero questi nodi provo i successivi
                continue

            if  actual_weight>drone_capacity:
                #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                break
            if (actual_diff<diff_min and (path_output_index==0 or actual_cost<=drone_autonomy)):
                diff_min=actual_diff
                min_path_index=path_output_index
                min_edge=edge

            #se invece il path é nuovo controllo se l"arco é libero e se i nodi non sono pieni
            if len(path)==0 and edge_free(solution,node1,node2) and node_degree(solution,node1)<4 and node_degree(solution,node2)<4:
                edge=[node1,node2,"New"]
                new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2]) 
                actual_diff=new_edges_cost+100
                actual_cost=new_edges_cost
                actual_weight=weights_dict[node_input]
                if actual_weight>drone_capacity:
                    #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                    #sono nel caso inn cui sarebbe l"unico nodo del path, quindi il peso del singolo nodo é maggiore della capacità
                    break
                if (actual_diff<diff_min and actual_cost<=drone_autonomy):
                    #penalizzo la creazione di nuovi path
                    diff_min=actual_diff
                    min_path_index=path_output_index
                    min_edge=edge

def node_degree(solution,node):
    degree=0
    for path in solution:
        if path==solution[0]:
            if node in path:
                degree+=2
        else:
            if node in path:
                if node == path[0] or node == path[-1]:
                    degree+=1
                else:
                    degree+=2
    return degree

def compute_path_drone_cost(path):    
    cost=0
    for i in range(len(path)-1):
        cost+=dist_drone[path[i]][path[i+1]]
    return cost

def compute_drone_weight(path):
    weight=0
    #per ogni nodo che non sia il primo o l'ultimo
    for node in path:
       if node!=path[0] and node !=path[-1]:
            weight+=weights_dict[node]
    return weight

def concat_drone_paths(solution,node):
    
    drone_paths=[path for path in solution if solution.index(path)!=0 and len(path)>0]

    paths_to_concat=[path for path in drone_paths if path[0]==node or path[-1]==node]
    print_graph_for_debug(solution)
    # if len(paths_to_concat)==1:
    #     pass
    if len(paths_to_concat)==2:
        path_to_concat_index_1=solution.index(paths_to_concat[0])
        path_to_concat_index_2=solution.index(paths_to_concat[1])
        if paths_to_concat[0][-1]==paths_to_concat[1][-1]:
            paths_to_concat[1].reverse()
        if paths_to_concat[0][0]==paths_to_concat[1][0]:
            paths_to_concat[0].reverse()
        if paths_to_concat[0][0]==paths_to_concat[1][-1]:
            paths_to_concat[0].reverse()
            paths_to_concat[1].reverse()

        concatenate_paths=paths_to_concat[0]+paths_to_concat[1]
        #rimuovo il nodo , che sarà presente 2 volte
        concatenate_paths.remove(node)
    cost=compute_path_drone_cost(concatenate_paths)
    weight=compute_drone_weight(concatenate_paths)
    
    for node in concatenate_paths:
        if concatenate_paths.count(node)>1:
            print_graph_for_debug(solution)
    if(cost>drone_autonomy or weight>drone_capacity):
        return False,False
    else:
        output=[concatenate_paths,path_to_concat_index_1,path_to_concat_index_2]
        return True,output

def compute_legal_inputs_nodes(solution,path_index):
    illegal_inputs_nodes=[]
    
    path=solution[path_index]

    #se e un path del dronbe

    if path_index!=0 and len(path)>2:
        illegal_inputs_nodes.append(path[0])
        illegal_inputs_nodes.append(path[-1])
    if path_index==0:
        for node in path:
            #il nodod de truck é illegale se ha grado >2 e non posso fondere i 2 cicli che gli arrivano
            if node_degree(solution,node)==3:
                illegal_inputs_nodes.append(node)
                concat_res,out=concat_drone_paths(solution,node)
                if concat_res==False:
                    illegal_inputs_nodes.append(node)
            if node_degree(solution,node)==4:
                concat_res,out=concat_drone_paths(solution,node)
                if concat_res==False:
                    illegal_inputs_nodes.append(node)
    
    legal_inputs_nodes=[node for node in path if node not in illegal_inputs_nodes]
    return legal_inputs_nodes
    
def find_best_node(solution):

    best_value=0
    #scorro i nodi nel truck path
    truck_path=solution[0]
    legal_inputs_nodes=compute_legal_inputs_nodes(solution,0)
    for node in legal_inputs_nodes:

        if node==truck_path[0]:
            next_node=truck_path[1]
            prev_node=truck_path[-1]
        elif node==truck_path[-1]:
            next_node=truck_path[0]
            prev_node=truck_path[-2]
        else:
            node_index=truck_path.index(node)
            next_node=truck_path[node_index+1]
            prev_node=truck_path[node_index-1]
        #
        ##
        ###
        ####
        #####CAMBIARE IN DIST TRUCK
        ####
        ###
        ##
        #
        value=dist[prev_node][node] + dist[next_node][node] - dist[prev_node][next_node]
        drone_cost=dist[prev_node][node] + dist[next_node][node]
        if value>best_value and drone_cost<=drone_autonomy:
            best_value=value
            best_node=node
    print(best_value)
    return prev_node, best_node, next_node

def find_best_edge(graph, dist, trip_number):
    #per ogni coppia di nodi cercoil nodo con costo minore tale che la
    #somma dei nuovi archi sia minima

    #scorro gli archi
    min_index=0
    cost_min=10000

    for node1,node2,attributes in graph.edges(data=True):

        if ([node1,node2] not in truck_locked_edges and trip_number==-1) \
            or (trip_number!=-1 and (any(x.index == node1 and x.trip_number==trip_number for x in visited_list_drone)) \
            and (any(y.index == node2  and y.trip_number==trip_number for y in visited_list_drone))):


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
#if len(truck_path)>2


#VARIABILI DRONE
starting_node = 29
drone_autonomy = 35
drone_capacity = 300

#Decido il nodo di partenza, ovvero il nostro deposito. 
truck_node_index = starting_node

#Dichiaro la lista dei nodi visitati durante l'algoritmo
visited_list_indexes = [starting_node]
#Dichiaro la lista dei nodi visitati dal truck durante l'algoritmo
visited_list_truck_indexes = [starting_node]
drone_cycle_number=0
cost = 0    #costo iniziale del veicolo
drone_on_truck=1


visited_list_drone=[]
truck_locked_edges=[]

# counter per i viaggi dell drone, anche quelli che poi annullo
drone_trip_counter=0


# conto quanti clienti fa il drone
drone_clients_counter=0

#-------FINE INIZIALIZZAZIONE-------


#INIZIO CODICE
#Creo la lista con le distanze dei vicini
neighbors_distance = [0]
for i in range(1, client_number_range): 
    neighbors_distance.append(dist_drone[truck_node_index][i])
#Inserisco in nearest_index il nodo più vicino al truck
nearest_index = nearest_node(neighbors_distance, visited_list_indexes)
graph_truck.add_edge(truck_node_index,nearest_index,length=round(dist_truck[truck_node_index][nearest_index],2),color='r')
visited_list_truck_indexes=compute_visited_list_truck()
visited_list_indexes=compute_visited_list()

#ciclo esterno del truck
first_time=1
last_node=0

while(len(visited_list_indexes)<client_number):
    sub_clients_counter=0
    drone_returned=False
    #CHEAPEST INSERTION TRUCK
    #controllo se il truck può fare solo un nodo: sono gia ad almeno un nodo, quindi aggiungo l arco piu conveniente    
    best_node_index,node1_best,node2_best=find_best_edge(graph_truck,dist_truck,-1)
    #print_graph_for_debug()
    #Ora ho trovato il nodo con detour di costo minimo, e i 2 nodi a cui collegarlo
    #quindi lo aggiungo e rimuovo l edge corrispondente
    graph_truck.add_edge(best_node_index,node1_best,length=round(dist_truck[best_node_index][node1_best],2),color='r')
    graph_truck.add_edge(best_node_index,node2_best,length=round(dist_truck[best_node_index][node2_best],2),color='r')
    visited_list_indexes.append(best_node_index)
    visited_list_truck_indexes=compute_visited_list_truck()
    #rimuovo solo se non sono al 2 ciclo, senno per la storia del undirected eliminerei il primo arco
    if(len(visited_list_truck_indexes)>3):
        graph_truck.custom_remove_edge(node1_best,node2_best)

    cost=compute_solution_cost(dist_truck)


#creo la soluzione in forma di lista
#region
solution=[]
#Aggiungo alla lista per GA
truck_path=[]
nodeA=visited_list_truck_indexes.pop(0)
truck_path.append(nodeA)
while(len(visited_list_truck_indexes)>0):
    nodeA_neighbours=[node2 for node1,node2 in graph_truck.edges() if node1==nodeA and node2 not in truck_path]+[node1 for node1,node2 in graph_truck.edges() if node2==nodeA and node1 not in truck_path]
    next_node=nodeA_neighbours[0]
    visited_list_truck_indexes.remove(next_node)
    truck_path.append(next_node)
    nodeA=next_node

solution.append(truck_path)

trip_counters=[node.trip_number for node  in visited_list_drone]
trip_counters=list(set(trip_counters))


for trip in trip_counters:
    drone_path=[]
    visited_list_drone_this_trip=[node.index for node in visited_list_drone if node.trip_number==trip]
    nodeA=visited_list_drone_this_trip.pop(0)
    drone_path.append(nodeA)
    while(len(visited_list_drone_this_trip)>0):
        nodeA_neighbours=[node2 for node1,node2 in graph_drone.edges() if node1==nodeA and node2 in visited_list_drone_this_trip and node2 not in drone_path]+\
            [node1 for node1,node2 in graph_drone.edges() if node2==nodeA and node1 in visited_list_drone_this_trip and node1 not in drone_path]

        next_node=nodeA_neighbours[0]
        visited_list_drone_this_trip.remove(next_node)
        drone_path.append(next_node)
        nodeA=next_node
    solution.append(drone_path)

#riempio di spazi vuoti
while(len(solution)<15):
    solution.append([])
#endregion
cost=compute_solution_cost(dist_truck)
print("Costo=",cost)




print_graph_for_debug()
prev_node, best_node, next_node = find_best_node(solution)    
node_concat=False
#recupero i valori

#print_graph_for_debug(solution)
truck_path.remove(best_node)


# #guardo se il nodo era usato dal drone equindi devo fondere i path, se no non devo farlo
# graph_total = nx.compose(graph_truck,graph_drone)
if(node_degree(solution,best_node)>0):
    node_concat=True
    #sistemo i path del drone
    #print_graph_for_debug(solution)
    res,concat_output=concat_drone_paths(solution,node_input)
    first_path_index=concat_output[1]
    second_path_index=concat_output[2]
    total_path=concat_output[0]
    solution[first_path_index]=total_path
    solution[second_path_index].clear()
        

#se aggiungessi nel miglior modo il nodo ed avevo concatenato, lo troverei visitato 2 volte
if(node_concat==False):
    drone_paths_counter=len(solution)-1-solution.count([])
    #se ho tanti path del drone quanti nodi del truck, non posso scegliere un path vuoto come output
    if len(solution[0])==drone_paths_counter:
        add_node_shortest_detour(solution, "full", best_node)
    else:
        add_node_shortest_detour(solution, "free", best_node)
    print (prev_node, best_node, next_node)
    

    





        
    




        








