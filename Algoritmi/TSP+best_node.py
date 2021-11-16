#IMPORTAZIONE LIBRERIE
from os import path
import copy
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.algorithms.centrality.eigenvector import eigenvector_centrality_numpy
from networkx.classes.function import neighbors 
import numpy as np 
import random
from tqdm import tqdm
from statistics import mean
import json

alpha=100
beta=-10000
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
graph_truck_clear = Custom_Graph()  
graph_drone_clear = Custom_Graph()    

#----------Inizio lettura coordinate e inserimento nel grafo e distanze drone-------------
#region
filename = 'Posizioni_clienti.txt'      #nome file puntatore
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
        graph_truck_clear.add_node(index, pos=(coord_x, coord_y))
client_number=index
client_number_range=client_number+1  
istance.close()

graph_truck=graph_truck_clear.copy()
graph_drone=graph_drone_clear.copy()

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
    
            if (node == starting_node): 
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

def create_graph(solution):

    graph_truck=graph_truck_clear.copy()
    graph_drone=graph_drone_clear.copy()
    graphs_couple=[]
    i=0
    truck_path=solution[0]
    while i < len(truck_path)-1:
        node1=truck_path[i]
        node2=truck_path[i+1]
        graph_truck.add_edge(node1,node2,length=round(dist_truck[node1][node2],2),color='r')
        i+=1
    node1=truck_path[-1]
    node2=truck_path[0]
    graph_truck.add_edge(node1,node2,length=round(dist_truck[node1][node2],2),color='r')

    p=1
    while p < len(solution):
        drone_path=solution[p]
        drone_color=paths_colors[p]
        if len(drone_path)>1:
            i=0
            while i < len(drone_path)-1:
                node1=drone_path[i]
                node2=drone_path[i+1]
                graph_drone.add_edge(node1,node2,length=round(dist_drone[node1][node2],2),color=drone_color)
                i+=1
            
        p+=1

    graphs_couple.append(graph_truck)
    graphs_couple.append(graph_drone)
    
    return graphs_couple
    # for path in solution:
    #     while len(path)>1:
    #         node1=path.pop(0)
    #         node2=path.pop(0)


def print_graph_for_debug_NEW(solution):
    graphs_couple=create_graph(solution)
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total = nx.compose(graph_truck,graph_drone)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    visited_list_truck=solution[0]
    visited_list_drone=[]
    
    drone_paths=[path for path in solution if path!=solution[0] and len(path)>0]
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

def nearest_node(node_1):
    neighbors_distance = [0]
    for node_2 in range(1, client_number_range): 
        neighbors_distance.append(dist_drone[node_1][node_2])

    min_value=10000000
    for i in range(1,len(neighbors_distance)):  
        #se il nodo é diverso dal nodo di cui cerco i vicini
        if i != node_1:
            actual_value=neighbors_distance[i]
            actual_index=i
            if(actual_value<min_value):
                min_value=actual_value
                min_index=actual_index
    return min_index

#Funzione che controlla che i due nodi non siano nello stesso tour del drone
def edge_free(solution,node1,node2):

    #entrambi i nodi sicuramente sono un arco, dato che li ho presi da graph_total.edges
    #se entrambi sono nel truck
    if (node1 in solution[0] and node2 in solution[0]):
        #controllo che non siano entrambi in un path del drone
        drone_paths=[path for path in solution if solution.index(path)!=0]
        for path in drone_paths:
            if (node1 in path and node2 in path):
                return False
        #ho controllato tutti i path e in nessuno sono presenti contemporanemante node1 e node2
        return True
    #non erano entrambi nel truck
    return False

#Funzione che aggiunge il nodo del truck in un ciclo del drone nella posizione tale per cui il nuovo Detour si minimo
def add_node_shortest_detour(solution, node_input):

    illegal_output_paths_index=[0]
    drone_paths_counter=len(solution)-1-solution.count([])
    #se ho tanti path del drone quanti nodi del truck, non posso scegliere un path vuoto come output
    if len(solution[0])==drone_paths_counter:                       
        empty_paths_index=[path_index for path_index in range(0,len(solution)) if path_index!=0 and len(solution[path_index])==0]
        illegal_output_paths_index+=empty_paths_index
    else:                      
        pass
    min_path_index=-1
    diff_min=100000000000
    #cerco il posto migliore per inserire il nodo, tale che il detour sia minimo

    legal_output_paths_index=[i for i in range(0,len(solution)) if i not in illegal_output_paths_index]
    for path_output_index in legal_output_paths_index:
        path=solution[path_output_index]
        #se len(path)==0 allora è un nuovo path
        if len(path)==0:
            truck_edges=compute_path_edges(solution,0)
            for edge in truck_edges:
                node1=edge[0]
                node2=edge[1]
                if edge_free(solution,node1,node2):
                    #and node_degree(solution,node1)<4 and node_degree(solution,node2)<4:
                    edge=[node1,node2,"New"]
                    new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2]) 
                    #penalizzo la creazione di nuovi path
                    actual_diff=new_edges_cost+100
                    actual_cost=new_edges_cost
                    actual_weight=weights_dict[node_input]
                    if actual_weight>drone_capacity:
                        #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                        #sono nel caso inn cui sarebbe l"unico nodo del path, quindi il peso del singolo nodo é maggiore della capacità
                        break
                    if (actual_diff<diff_min and actual_cost<=drone_autonomy):                     
                        diff_min=actual_diff
                        min_path_index=path_output_index
                        min_edge=edge  

        path_edges=compute_path_edges(solution,path_output_index)
        #scorro gli archi
        for edge in path_edges:
            node1=edge[0]
            node2=edge[1]
            #calcolo il costo di questa prova, 
            #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
            #e tolgo l arco rimosso
            
            #controllo che i 2 nodi non siamo partenza e arrivo.....MMM? 
            if((node1 in solution[0] and node2 in solution[0])==False ):
                new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2])
                old_edge_cost=dist_drone[node1][node2]
                actual_diff=new_edges_cost-old_edge_cost
                actual_cost=compute_path_drone_cost(path)-old_edge_cost+new_edges_cost
                actual_weight=compute_drone_weight(path)+weights_dict[node_input]
                if  actual_weight>drone_capacity:
                    #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                    break
                if (actual_diff<diff_min and actual_cost<=drone_autonomy):
                    diff_min=actual_diff
                    min_path_index=path_output_index
                    min_edge=edge

            
    
    #se non ho trovato un modo per aggiungere il nodo
    if min_path_index==-1:
        return False

    path_output=solution[min_path_index]
    
    #se é un novo path
    if len(min_edge)>2:
        path_output+=[min_edge[0],node_input,min_edge[1]]



    else:
        node_o_1_index=path_output.index(min_edge[0])
        node_o_2_index=path_output.index(min_edge[1])
        first_and_last=[path_output[0],path_output[-1]]
        if min_edge[0] in first_and_last and min_edge[1] in first_and_last:
            path_output.append(node_input)
        else:
            node_o_min_index=min(node_o_1_index,node_o_2_index)
            path_output.insert(node_o_min_index+1,node_input)

    return True

def check_node_shortest_detour(solution, node_input):
    solution_clear=copy.deepcopy(solution)
    solution_clear[0].remove(node_input)
    illegal_output_paths_index=[0]
    drone_paths_counter=len(solution_clear)-1-solution_clear.count([])
    #se ho tanti path del drone quanti nodi del truck, non posso scegliere un path vuoto come output
    if len(solution_clear[0])==drone_paths_counter:                       
        empty_paths_index=[path_index for path_index in range(0,len(solution_clear)) if path_index!=0 and len(solution_clear[path_index])==0]
        illegal_output_paths_index+=empty_paths_index
    else:                      
        pass
    min_path_index=-1
    diff_min=100000000000
    #cerco il posto migliore per inserire il nodo, tale che il detour sia minimo

    legal_output_paths_index=[i for i in range(0,len(solution_clear)) if i not in illegal_output_paths_index]
    for path_output_index in legal_output_paths_index:
        path=solution_clear[path_output_index]
        #se len(path)==0 allora è un nuovo path
        if len(path)==0:
            truck_edges=compute_path_edges(solution_clear,0)
            for edge in truck_edges:
                node1=edge[0]
                node2=edge[1]
                if edge_free(solution_clear,node1,node2):
                    #and node_degree(solution_clear,node1)<4 and node_degree(solution_clear,node2)<4:
                    edge=[node1,node2,"New"]
                    new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2]) 
                    #penalizzo la creazione di nuovi path
                    actual_diff=new_edges_cost+100
                    actual_cost=new_edges_cost
                    actual_weight=weights_dict[node_input]
                    if actual_weight>drone_capacity:
                        #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                        #sono nel caso inn cui sarebbe l"unico nodo del path, quindi il peso del singolo nodo é maggiore della capacità
                        break
                    if (actual_diff<diff_min and actual_cost<=drone_autonomy):  
                        return True                     

        path_edges=compute_path_edges(solution_clear,path_output_index)
        #scorro gli archi
        for edge in path_edges:
            node1=edge[0]
            node2=edge[1]
            #calcolo il costo di questa prova, 
            #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
            #e tolgo l arco rimosso
            
            #controllo che i 2 nodi non siamo partenza e arrivo.....MMM? 
            if((node1 in solution_clear[0] and node2 in solution_clear[0])==False ):
                new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2])
                old_edge_cost=dist_drone[node1][node2]
                actual_diff=new_edges_cost-old_edge_cost
                actual_cost=compute_path_drone_cost(path)-old_edge_cost+new_edges_cost
                actual_weight=compute_drone_weight(path)+weights_dict[node_input]
                if  actual_weight>drone_capacity:
                    #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                    break
                if (actual_diff<diff_min and (path_output_index==0 or actual_cost<=drone_autonomy)):
                    return True  
            
    
    #se non ho trovato un modo per aggiungere il nodo
    if min_path_index==-1:
        #print_graph_for_debug_NEW(solution_clear)
        return False
    else:
        return True    

def compute_path_edges(solution,path_index):
    edges=[]
    path=solution[path_index]
    i=0
    while i < len(path)-1:
        node1=path[i]
        node2=path[i+1]
        edges.append([node1,node2])
        i+=1  

    #se il path é del truck aggiungo anche l arco finale
    if path_index==0:
        node1=path[-1]
        node2=path[0]
        edges.append([node1,node2])

    return edges


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

def compute_possible_reunion_nodes(solution,old_reunion_nodes):
    
    truck_path=solution[0]
    reunion0_index=truck_path.index(old_reunion_nodes[0])
    reunion1_index=truck_path.index(old_reunion_nodes[1])
    possible_reunion_nodes=[]

    if (reunion0_index==0 and reunion1_index==1) or (reunion0_index==1 and reunion1_index==0):
        if edge_free(solution,truck_path[-1],truck_path[0]):
            possible_reunion_nodes.append(truck_path[-1])
        if edge_free(solution,truck_path[1],truck_path[2]):
            possible_reunion_nodes.append(truck_path[2])

    elif (reunion0_index==len(truck_path)-1 and reunion1_index==0) or (reunion0_index==0 and reunion1_index==len(truck_path)-1):
        if edge_free(solution,truck_path[-1],truck_path[-2]):
            possible_reunion_nodes.append(truck_path[-2])
        if edge_free(solution,truck_path[0],truck_path[1]):
            possible_reunion_nodes.append(truck_path[1])
       
    elif (reunion0_index==len(truck_path)-2 and reunion1_index==len(truck_path)-1) or (reunion0_index==len(truck_path)-1 and reunion1_index==len(truck_path)-2):
        if edge_free(solution,truck_path[-3],truck_path[-2]):
            possible_reunion_nodes.append(truck_path[-3])
        if edge_free(solution,truck_path[-1],truck_path[0]):
            possible_reunion_nodes.append(truck_path[0])

    elif reunion0_index < reunion1_index: 
        if edge_free(solution,truck_path[reunion0_index-1],truck_path[reunion0_index]):
            possible_reunion_nodes.append(truck_path[reunion0_index-1])
        if edge_free(solution,truck_path[reunion1_index],truck_path[reunion1_index+1]):
            possible_reunion_nodes.append(truck_path[reunion1_index+1])
    
    elif reunion1_index < reunion0_index:
        if edge_free(solution,truck_path[reunion0_index],truck_path[reunion0_index+1]):
            possible_reunion_nodes.append(truck_path[reunion0_index+1])
            if edge_free(solution,truck_path[reunion1_index-1],truck_path[reunion1_index]):
                possible_reunion_nodes.append(truck_path[reunion1_index-1])
        
    for node in possible_reunion_nodes:
        if node_degree(solution, node)>3:
            possible_reunion_nodes.remove(node)

    return possible_reunion_nodes

def compute_best_reunion(node_start,node_possible,alpha,beta):
    return (dist_drone[node_start][node_possible]*alpha)+(weights_dict[node_possible]*beta)

def concat_drone_paths(solution,node):
    concatenate_paths=-1
    drone_paths=[path for path in solution if path!=solution[0] and len(path)>0]

    paths_to_concat=[path for path in drone_paths if path[0]==node or path[-1]==node]
    #se len==1 significa che provo a togliere uno dei 2 nodi di arrivo/partenza di UN SOLO path del drone
    if len(paths_to_concat)==1:
        path_to_concat_index_1=solution.index(paths_to_concat[0])
        path_to_concat_index_2=-1
        path_to_extend=paths_to_concat[0]
        truck_path=solution[0]
        
        possible_reunion_nodes=[]
        old_reunion_nodes=[path_to_extend[0],path_to_extend[-1]]
        #se sto testando la possibilità di concatenare
        if node_degree(solution,old_reunion_nodes[0])>1 and node_degree(solution,old_reunion_nodes[1])>1:

            #controllo quale viene prima cosi so quali nodi prendere
            possible_reunion_nodes=compute_possible_reunion_nodes(solution,old_reunion_nodes)
            if len(possible_reunion_nodes)>0:
                best_reunion=min(possible_reunion_nodes,key=lambda x:dist_drone[x][node])
        #se voglio effetivamente effettuare l estensione
        else:
            if node==path_to_extend[0]:
                reunion_node=path_to_extend[-1]
                reunion_node_index=truck_path.index(reunion_node)
                #concatenate_paths = [new_start_node] + path_to_extend
            elif node==path_to_extend[-1]:
                reunion_node=path_to_extend[0]
                reunion_node_index=truck_path.index(reunion_node)
                #concatenate_paths = path_to_extend + [new_start_node]

            if reunion_node_index==0:
                next_node=truck_path[reunion_node_index+1]
                prev_node=truck_path[-1]
            elif reunion_node_index==len(truck_path)-1:
                next_node=truck_path[0]
                prev_node=truck_path[reunion_node_index-1]
            else:
                next_node=truck_path[reunion_node_index+1]
                prev_node=truck_path[reunion_node_index-1]
            
            if node_degree(solution, next_node)<4 and edge_free(solution,reunion_node,next_node):
                possible_reunion_nodes.append(next_node)
            if node_degree(solution, prev_node)<4 and edge_free(solution,reunion_node,prev_node):
                possible_reunion_nodes.append(prev_node)
            if len(possible_reunion_nodes)>0:
                best_reunion=min(possible_reunion_nodes,key=lambda x:dist_drone[x][node])

        if len(possible_reunion_nodes)>0:
            if node==path_to_extend[0]:
                concatenate_paths = [best_reunion] + path_to_extend
            elif node==path_to_extend[-1]:
                concatenate_paths = path_to_extend + [best_reunion]
        elif len(possible_reunion_nodes)==0:
            return False,False

    #se len==2 significa che provo a togliere uno dei 2 nodi di arrivo/partenza di DUE path del drone
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
    
    if(cost>drone_autonomy or weight>drone_capacity):
        return False,False
    else:
        output=[concatenate_paths,path_to_concat_index_1,path_to_concat_index_2]
        return True,output

def compute_legal_inputs_nodes(solution,path_index):
    illegal_inputs_nodes=[starting_node]
    
    path=solution[path_index]

    if path_index==0:
        for node in path:
            #il nodod de truck é illegale se ha grado >2 e non posso fondere i 2 cicli che gli arrivano
            if node_degree(solution,node)>2:
                concat_res,out=concat_drone_paths(solution,node)
                if concat_res==False:
                    illegal_inputs_nodes.append(node)
            if check_node_shortest_detour(solution,node)==False:
                illegal_inputs_nodes.append(node)
    
    legal_inputs_nodes=[node for node in path if node not in illegal_inputs_nodes]
    return legal_inputs_nodes

#Funzione che trova i nodi migliori nel ciclo del truck     
def find_best_node(solution):
    best_node=-1
    best_prev_node=-1
    best_next_node=-1
    best_value=-100000000000
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
       
        value=(dist_truck[prev_node][node] + dist_truck[next_node][node] - dist_truck[prev_node][next_node])*alpha + weights_dict[node]*beta
        #controllare se posso aggiungerlo a qualche percorso del drone

        if value>best_value:
            best_value=value
            best_node=node
            best_prev_node=prev_node
            best_next_node=next_node

    return best_prev_node, best_node, best_next_node

#Funzione che trova la coppia di nodi tali per cui l'arco sia di costo minimo
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

def compute_solution_cost_by_sol(solution):    
    cost=0
    
    for i in range (len(solution[0])-1):
        cost+=dist_truck[solution[0][i]][solution[0][i+1]]
    cost+=dist_truck[solution[0][i+1]][solution[0][0]]

    return cost

#VARIABILI DRONE
drone_autonomy = 25
drone_capacity = 300

#Dichiaro la lista dei nodi visitati durante l'algoritmo
visited_list_indexes = []
#Dichiaro la lista dei nodi visitati dal truck durante l'algoritmo
#visited_list_truck_indexes = [starting_node]
starting_node=29
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
best_edge_cost=10000
best_edge=[-1,-1]
for node_start in range(1, client_number_range):
    #Inserisco in nearest_index il nodo più vicino al truck
    nearest_index = nearest_node(node_start)
    edge_cost=dist_truck[node_start][nearest_index]
    if edge_cost<best_edge_cost:
        best_edge=[node_start,nearest_index]
        best_edge_cost=edge_cost
best_edge_1=best_edge[0]
best_edge_2=best_edge[1]
graph_truck.add_edge(best_edge_1,best_edge_2,length=round(dist_truck[best_edge_1][best_edge_2],2),color='r')
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
visited_list_truck_indexes=compute_visited_list_truck()
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
print("Costo del TSP=",cost)
solution_clear=copy.deepcopy(solution)

inputs=inputs=[w/10 for w in range(-50,-10,5)]+\
        [w/10 for w in range(-10,-5,2)]+\
        [w/10 for w in range(-5,5,1)]+\
        [w/10 for w in range(5,10,2)]+\
        [w/10 for w in range(10,50,5)]
ab_list=[]
for alpha in inputs:
    for beta in inputs:
        key1=[alpha,beta]
        ab_list.append(key1)


results_dic={}
population=[]

desc="Trying different values... alpha="+str(inputs[0])+" beta="+str(inputs[0])+"   "
desc_len=len(desc)
pbar=tqdm (ab_list, desc=desc,leave=True,bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}')
for key in pbar:
    alpha=key[0]
    beta=key[1]
    desc="Trying different values... alpha="+str(alpha)+" beta="+str(beta)+"  "
    while len(desc)!=desc_len:
        if len(desc)<desc_len:
            desc+=" "
        if len(desc)>desc_len:
            desc=desc[:-1]
    pbar.set_description(desc)
    solution=copy.deepcopy(solution_clear)
    truck_path=solution[0]


    best_node="starting"
    while best_node!=-1: 
        prev_node, best_node, next_node = find_best_node(solution)
        
        if best_node!=-1:   
            node_concat=False
            truck_path.remove(best_node)

            # #guardo se il nodo era usato dal drone equindi devo fondere i path, se no non devo farlo
            # graph_total = nx.compose(graph_truck,graph_drone)
            if(node_degree(solution,best_node)>0):
                
                node_concat=True
                #sistemo i path del drone
                res,concat_output=concat_drone_paths(solution,best_node)

                first_path_index=concat_output[1]
                second_path_index=concat_output[2]
                total_path=concat_output[0]

                solution[first_path_index]=total_path
                
                # se l indice é -1 signifche cge non ho concatenato 2 path, ma un path(first path) con un nuvo arco
                if second_path_index!=-1:
                    solution[second_path_index].clear()
                
            
            #se aggiungessi nel miglior modo il nodo ed avevo concatenato, lo troverei visitato 2 volte
            if(node_concat==False):                      
                add_node_shortest_detour(solution, best_node)



        
    cost=compute_solution_cost_by_sol(solution)
    #print("Costo=",cost)
    key=str(alpha)+" & "+str(beta)
    results_dic[key]=cost    
    
    #print_graph_for_debug_NEW(solution)   
    population.append(solution)

key_migliore=min(results_dic, key = lambda k: results_dic[k])
migliore_valore=results_dic[key_migliore]
print(key_migliore,"ha dato un costo di",migliore_valore)
print("Nodo iniziale=",starting_node)
print("Autonomia drone", drone_autonomy)
print("Capacita", drone_capacity)       
with open('aaaaa.txt', 'w') as aaa:
    for key, value in results_dic.items():
        aaa.write(str(key)+ " : "+str( value)+"\n")
                
i=0
for key, value in results_dic.items():
    if key==key_migliore:
        k=i
        break     
    i+=1  

sol=population[i]
#print_graph_for_debug_NEW(solution)


with open('2_OPT_input.txt', 'w') as Two_opt_input:
    Two_opt_input.writelines(str(starting_node)+"\n")
    Two_opt_input.writelines(str(drone_autonomy)+"\n")
    Two_opt_input.writelines(str(drone_capacity)+"\n")
    json.dump(sol, Two_opt_input)

sol_to_print = []
for element in sol:
    if element != []:
        sol_to_print.append(element)

print("L'algoritmo TSP + Best Drone ha trovato la soluzione --> ", sol_to_print, "\n")
for path in sol:
    if path == sol[0]:
        print("Dove il Truck percorre la route --> ", path)
    elif path == sol[1]:
        print("Mentre il Drone percorre le seguenti routes:", "\n", path)
    elif path != []:
        print(path)
    else:
        continue

print_graph_for_debug_NEW(sol)