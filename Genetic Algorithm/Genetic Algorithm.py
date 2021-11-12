#region
#IMPORTAZIONE LIBRERIE
from os import PathLike, error
from random import seed
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.algorithms import cuts
from networkx.classes.function import neighbors
from networkx.drawing.layout import rescale_layout 
import numpy as np     
from typing import Any, List
import time
import json
from multiprocessing import Pool
from itertools import repeat
from itertools import chain
import itertools
import random
from tqdm import tqdm

import multiprocessing, logging
# mpl = multiprocessing.log_to_stderr()
# mpl.setLevel(logging.INFO)

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
    def custom_remove_edge(self,node1,node2,solution):
        if self.has_edge(node1,node2):
            self.remove_edge(node1,node2)
        elif self.has_edge(node2,node1):
            self.remove_edge(node2,node1)
        else:
            solution
            print_graph_for_debug(solution)
            raise CustomError_noedges(str(node1)+" "+str(node2))

def contains(small, big):
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return True
    return False

def print_graph_for_debug(solution):
    
    graphs_couple=create_graph(solution)
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
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

def compute_solution_cost(solution):    
    cost=0
    
    for i in range (len(solution[0])-1):
        cost+=dist_truck[solution[0][i]][solution[0][i+1]]
    cost+=dist_truck[solution[0][i+1]][solution[0][0]]

    #penalizzo per igno nodo non visitato
    for node in graph_truck_clear.nodes:
        if any(node in path for path in solution):
            pass
        else:         
            cost+=20

    return cost

def compute_path_drone_cost(path):    
    cost=0
    for i in range(len(path)-1):
        cost+=dist_drone[path[i]][path[i+1]]
    return cost

def compute_path_truck_cost(path):    
    cost=0
    for i in range(len(path)-1):
        cost+=dist_truck[path[i]][path[i+1]]
    cost+=dist_truck[path[-1]][path[0]]
    return cost

def compute_drone_weight(path):
    weight=0
    #per ogni nodo che non sia il primo o l'ultimo
    for node in path:
       if node!=path[0] and node !=path[-1]:
            weight+=weights_dict[node]
    return weight

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

def solution_duplicated_OLD(population,solution_input):

    #scorro tutte le soliuzoni
    for solution in population:

        flag=0
        #scorro tutti i percorsi e li duplico(truck, drone1,drone2)
        for path in solution:

            path=path*2
            #scorro tutti i percorsi in questa soluzione
            for path_input in solution_input:
                #controllo se é una sotto lista
                if(contains(path_input,path) and len(path_input)==(len(path)/2) ):
                    flag+=1
                    # se é sottolista posso smettere di ciclare e cambiare path2
                    break
            #se dato path, nessun path_input ha fatto flag su questo path, allora sicuramente questa soluzione é diversa
            else:
                break
        #se flag=15 allora ogni path é in path2, quindi la soluzione é uguale
        if flag==len(solution):
            return True   
    #se sono qua ogni soluzione aveva almeno un path che nopn era contentenuto in nessun path2, flag<15
    return False

def solution_duplicated(population,solution_input):

    #questa funzione rispetto a quella di prima, non tiene conto del fatto che il percorso del truck é ciclico
    #scorro tutte le soliuzoni
    for solution in population:
        if sorted(solution) == sorted(solution_input):
            return True
    return False

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

def concat_drone_paths(solution,node):
    
    drone_paths=[path for path in solution if path!=solution[0] and len(path)>0]

    paths_to_concat=[path for path in drone_paths if path[0]==node or path[-1]==node]
    #se len==1 significa che provo a togliere uno dei 2 nodi di arrivo/partenza di UN SOLO path del drone
    if len(paths_to_concat)>2:
    #print_graph_for_debug(solution)
        print(paths_to_concat)
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
    # if len(possible_reunion_nodes)==0:
    #     print_graph_for_debug_NEW(solution)
    return possible_reunion_nodes

def compute_legal_inputs_nodes(solution,path_index):
    illegal_inputs_nodes=[starting_node]
    
    path=solution[path_index]

    #se e un path del dronbe
    if path_index!=0 and len(path)>2:
        illegal_inputs_nodes.append(path[0])
        illegal_inputs_nodes.append(path[-1])
    if path_index==0:
        for node in path:
            #il nodod de truck é illegale se ha grado >2 e non posso fondere i 2 cicli che gli arrivano
            if node_degree(solution,node)>2:
                concat_res,out=concat_drone_paths(solution,node)
                if concat_res==False:
                    illegal_inputs_nodes.append(node)
    
    legal_inputs_nodes=[node for node in path if node not in illegal_inputs_nodes]
    return legal_inputs_nodes

def add_node_shortest_detour(solution, legal_output_paths_index, node_input):
    min_path_index=-1
    
    #cerco il posto migliore per inserire il nodo, tale che il detour sia minimo
    
    diff_min=100000000000

    #se il path é nuovo controllo se l"arco é libero e se i nodi non sono pieni
    

    for path_output_index in legal_output_paths_index:
        path=solution[path_output_index]

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
    
def mutation_1(solution,path_input_index,node_input_index,legal_output_paths_index):
    node_concat=False
    #recupero i valori
    path_input=solution[path_input_index]
    node_input=path_input[node_input_index]
    #rimuovo il nodo dal grafo, e se il percorso ha solo due nodi allora lo elimino
    path_input.pop(node_input_index)
    if len(path_input)<3:
        path_input.clear()

    # #guardo se il nodo era usato dal drone equindi devo fondere i path, se no non devo farlo
    # graph_total = nx.compose(graph_truck,graph_drone)
    if(node_degree(solution,node_input)>0):
        node_concat=True
        #sistemo i path del drone

        res,concat_output=concat_drone_paths(solution,node_input)
        first_path_index=concat_output[1]
        second_path_index=concat_output[2]
        
        total_path=concat_output[0]
    
        solution[first_path_index]=total_path
        
        if second_path_index!=-1:
            solution[second_path_index].clear()
           

    #se aggiungessi nel miglior modo il nodo ed avevo concatenato, lo troverei visitato 2 volte
    if(node_concat==False):
        add_node_shortest_detour(solution, legal_output_paths_index, node_input)

def population_mutation(population,best_sol):
    to_be_mutated_list=[]
    all_mutated_list=[]

    for solution in population:
        if solution!=best_sol:
            # mutated_ths_sol=0

            for path in solution:
                #se sono nel path del truck e ho 2 nodi non faccio la mutazione,rimarrei con un nodo
                if solution.index(path)!=0 or len(path)>2:             
                    path_index=solution.index(path)
                    for node in path:
                        #scelgo quali nodi mutare
                        if node not in path:
                            print_graph_for_debug(solution)
                        node_index=path.index(node)
                        probability_node=random.random() 
                        if(probability_node>NODE_PROBABILITY_FOR_MUTATION):
                            value=[path_index,node_index]
                            to_be_mutated_list.append(value)


            
            while(len(to_be_mutated_list)>0):

                value_index=to_be_mutated_list.pop()
                path_input_index=value_index[0]
                node_input_index=value_index[1]
                path=solution[path_input_index]
                #se il path del nodo da mutare esiste ancora
                if len(path)>0:
                    node_input=path[node_input_index]
                    #calcolo i nodi che possono essere rimossi dal path senza problemi 
                    legal_inputs_nodes=compute_legal_inputs_nodes(solution,path_input_index)
                    if starting_node in legal_inputs_nodes:
                        print(legal_inputs_nodes)

                    #se il nodo la cui probabilità mi dice di rimoverlo é nella lista dei nodi legali
                    if node_input in legal_inputs_nodes:
                        all_mutated_list.append(node_input_index)

                        illegal_output_paths_index=[]
                        if path_input_index!=0:
                            #se rendo illegale il riaggiungimento al path del truck rischio che il nodo non sia aggiungibile a nessun path
                            illegal_output_paths_index=[path_input_index]
                        not_empty_paths_index=[path_index for path_index in range(0,len(solution)) if path_index!=0 and len(solution[path_index])>0 ]
                        #se ho tanti path del drone quanti nodi del truck, non posso scegliere un path vuoto come output
                        if len(solution[0])==len(not_empty_paths_index):
                            empty_paths_index=[path_index for path_index in range(0,len(solution)) if path_index!=0 and len(solution[path_index])==0 ]
                            illegal_output_paths_index+=empty_paths_index
                        legal_output_paths_index=[i for i in range(0,len(solution)) if i not in illegal_output_paths_index]
                
                        #soluzione, path input,nodo da spostare, possibili path di destinazione
                        # if copied_already==0:
                        #     copied_sol=solution.copy()
                        #     population.append(copied_sol)
                        #     copied_already=1
                        
                        mutation_1(solution,path_input_index,node_input_index,legal_output_paths_index)
                        for path in solution:
                            for node in path:
                                if node_degree(solution,node)>4:
                                    print(solution,path_input_index,node_input_index,legal_output_paths_index)
                                    print(node)
                                    print_graph_for_debug(solution)
                    

            
        
    # print("fatte ",len(all_mutated_list)," mutazioni")
    # print(time.time()-start," secs per mutare")     
 
def compute_fitness_wheel(population):
    #calcolo il costo di ogni sluzione
    rank_wheel=[0 for i in range(0,len(population))]
    solutions_cost=[]
    for solution in population:
        solutions_cost.append(compute_solution_cost(solution))
    sorted_costs=solutions_cost.copy()
    sorted_costs.sort()
    fitness=0
    previous_cost=-1
    while len(sorted_costs)>0:
        sol_cost=sorted_costs.pop(0)
        if sol_cost>previous_cost:
            fitness+=1
        sol_cost_index=solutions_cost.index(sol_cost)
        solutions_cost[sol_cost_index]=-1
        rank_wheel[sol_cost_index]=fitness   
        previous_cost=sol_cost
    
    #formula di gauss
    ranks_sum=sum(rank_wheel)
    fitness_wheel=[sol/ranks_sum for sol in rank_wheel]
    return fitness_wheel

def starting_drone_point(solution,node):
    starting_paths=[]
    for path in solution:
        if len(path)>0:
            if node==path[0] or node==path[-1]:
                starting_paths.append(solution.index(path))
    if len(starting_paths)>0:
        return starting_paths
    else:
        return -1

def remove_double_visited_nodes(solution):
    drone_nodes=solution.copy()
    #rimuovo il truck
    drone_nodes.pop(0)
    to_be_checked_nodes=solution.copy()

   
    for path in solution:
        to_be_removed=[]
        if path==solution[0]:
            for node in path:
                #per ogni nodo in questo path , lo rimuovo se e presente in altri percorsi
                #ma non e un nodo di inzio o di fine in quaslisasi percorso
                if any(node in path_i for path_i in drone_nodes) and starting_drone_point(solution,node)==-1:
                    to_be_removed.append(node)
                    # node_index=path.index(node)
                    # if node_index==0:
                    #     node_left=path[-1]
                    # else:
                    #     node_left=path[node_index-1] 

                    # if node_index==len(path):
                    #     node_right=path[0]
                    # else:
                    #     node_right=path[node_index+1]       
                    # graph_truck.custom_remove_edge(node_left,node)
                    # graph_truck.custom_remove_edge(node_right,node)
                    # graph_truck.add_edge(node_left,node_right)

        else:    
            to_be_checked_nodes.remove(path)
            for node in path:
                #per ogni nodo in questo path , lo rimuovo se e presente in altri percorsi, ma non e un nodo di inzio o di fine di questo path
                #non sara inizio o fine di altri percorsi per come ho costruito i path del drone: per igni coppia di nodi hi un path che parte da quelli
                if any(node in path_i for path_i in to_be_checked_nodes) and node!=path[0] and node!=path[-1]:
                    to_be_removed.append(node)
                    # node_index=path.index(node)
                    # if node_index==0:
                    #     node_left=path[-1]
                    # else:
                    #     node_left=path[node_index-1] 

                    # if node_index==len(path):
                    #     node_right=path[0]
                    # else:
                    #     node_right=path[node_index+1]       
                    # graph_drone.custom_remove_edge(node_left,node)
                    # graph_drone.custom_remove_edge(node_right,node)
                    # graph_drone.add_edge(node_left,node_right)
                    
        
        for node in to_be_removed:
            path.remove(node)


def return_double_visited_nodes(solution):
    drone_nodes=solution.copy()
    #rimuovo il truck
    drone_nodes.pop(0)
    to_be_checked_nodes=solution.copy()

    to_be_removed=[]
    for path in solution:
        path_ixxx=solution.index(path)
        if path==solution[0]:
            for node in path:
                
                #per ogni nodo in questo path , lo rimuovo se e presente in altri percorsi
                #ma non e un nodo di inzio o di fine in quaslisasi percorso
                if any(node in path_i for path_i in drone_nodes) and starting_drone_point(solution,node)==-1:
                    to_be_removed.append([path_ixxx,node])

        else:    
            to_be_checked_nodes.remove(path)
            for node in path:
                #per ogni nodo in questo path , lo rimuovo se e presente in altri percorsi, ma non e un nodo di inzio o di fine di questo path
                #non sara inizio o fine di altri percorsi per come ho costruito i path del drone: per igni coppia di nodi hi un path che parte da quelli
                if any(node in path_i for path_i in to_be_checked_nodes) and node!=path[0] and node!=path[-1]:
                    to_be_removed.append([path_ixxx,node])
                    
    return to_be_removed
        
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

def solution_edges(solution):

    edges=[]
    truck_path=solution[0]
    i=0
    while i < len(truck_path)-1:
        node1=truck_path[i]
        node2=truck_path[i+1]
        edges.append[node1,node2]
        i+=1
    node1=truck_path[-1]
    node2=truck_path[0]
    edges.append[node1,node2]

    p=1
    while p < len(solution):
        drone_path=solution[p]
        if len(drone_path)>1:
            i=0
            while i < len(drone_path)-1:
                node1=drone_path[i]
                node2=drone_path[i+1]
                edges.append[node1,node2]
                i+=1
            
        p+=1
    
    return edges

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

def remove_paths_over_degree(solution):       

    for node in graph_truck_clear:
        if node_degree(solution,node)>4:
            paths_degreee_indexes=starting_drone_point(solution,node)
            paths_degreee=[solution[index] for index in paths_degreee_indexes]
            paths_degreee.sort(key=len)
            solution.remove(paths_degreee[0])
      
def solutions_crossover(population,parent_1_index,parent_2_index):
    parent_1=population[parent_1_index].copy()
    parent_2=population[parent_2_index].copy()
    truck_path_parent_1=parent_1[0]
    truck_path_parent_2=parent_2[0]

    #CHILDREN1
    children_1=[]
    #costruisco il percorso del truck del figlio1
    truck_path_children_1=[]
    cuts_points=random.choices(range(0,len(truck_path_parent_1)),k=2)

    truck_sub_path_parent_1=truck_path_parent_1[cuts_points[0]:cuts_points[1]]
    remaining_truck_path_parent_2=[node for node in truck_path_parent_2 if node not in truck_sub_path_parent_1]
    #aggiungo la parte prima del cut
    while len(truck_path_children_1)<cuts_points[0] and len(remaining_truck_path_parent_2)>0:
        truck_path_children_1.append(remaining_truck_path_parent_2.pop(0))
    #aggiungo la parte tagliata
    truck_path_children_1+=truck_sub_path_parent_1
    #aggiungo la parte dopo il taglio finche la dimensione del figlio  uguale a quella di parent 1, boh potrei provar altre cose
    while len(truck_path_children_1)<len(truck_path_parent_1) and len(remaining_truck_path_parent_2)>0:
        truck_path_children_1.append(remaining_truck_path_parent_2.pop(0))
    children_1.append(truck_path_children_1) 

    #per ogni coppia di nodi, se ne trovo qualcuna nei percorsi dei truck dei genitori ne importo i percorsi relativi che fa il drone
    i=0
    for node in truck_path_children_1:
        if node == truck_path_children_1[-1]:
            next_node=truck_path_children_1[0]
        else:
            next_node=truck_path_children_1[i+1]
        couple=[node,next_node]
        #se la coppia e nel path truck del padre 
        if contains(couple,truck_path_parent_1):
            #cerco se ce un path che contiene entrambi i nodi
            for path in parent_1:
                if all(node in path for node in couple) and parent_1.index(path)!=0:
                    children_new_path=path.copy()    
                    children_1.append(children_new_path)

        elif contains(couple,truck_path_parent_2):
            for path in parent_2:
                if all(node in path for node in couple) and parent_2.index(path)!=0:
                    children_new_path=path.copy()    
                    children_1.append(children_new_path)
        i+=1

    population.append(children_1)
    visited_list_truck=children_1[0]
    visited_list_drone=[]
    for path in children_1:
        if path!=children_1[0]:
            visited_list_drone+=path
    
    remove_double_visited_nodes(children_1)

    #boh nojn dovrebbero essercene mai
    #remove_paths_over_degree(children_1_index)

    two_points_paths=[]
    for path in children_1:
        if len(path)<3:
            two_points_paths.append(path)
    for path in two_points_paths:
        children_1.remove(path)

    while len(children_1)<15:
        children_1.append([])
    
    #paths illegali
    illegal_output_paths_index=[]
    not_empty_paths_index=[path_index for path_index in range(0,len(children_1)) if path_index!=0 and len(children_1[path_index])>0 ]
    #se ho tanti path del drone quanti nodi del truck, non posso scegliere un path vuoto come output
    if len(children_1[0])==len(not_empty_paths_index):
        empty_paths_index=[path_index for path_index in range(0,len(children_1)) if path_index!=0 and len(children_1[path_index])==0 ]
        illegal_output_paths_index+=empty_paths_index
    legal_output_paths_index=[i for i in range(0,len(children_1)) if i not in illegal_output_paths_index]

    #aggiungo i nodi non visitati
    not_visited_nodes=[node for node in graph_truck_clear.nodes if node not in visited_list_drone and node not in visited_list_truck]
    for node in not_visited_nodes:
        add_node_shortest_detour(children_1,legal_output_paths_index,node) 


    #CHILDREN2
    children_2=[]
    #costruisco il percorso del truck del figlio1
    truck_path_children_2=[]
    
    cuts_points=random.choices(range(0,len(truck_path_parent_2)),k=2)

    truck_sub_path_parent_2=truck_path_parent_2[cuts_points[0]:cuts_points[1]]
    remaining_truck_path_parent_1=[node for node in truck_path_parent_1 if node not in truck_sub_path_parent_2]
    #aggiungo la parte prima del cut
    while len(truck_path_children_2)<cuts_points[0] and len(remaining_truck_path_parent_1)>0:
        truck_path_children_2.append(remaining_truck_path_parent_1.pop(0))
    #aggiungo la parte tagliata
    truck_path_children_2+=truck_sub_path_parent_2
    #aggiungo la parte dopo il taglio finche la dimensione del figlio  uguale a quella di parent 1, boh potrei provar altre cose
    while len(truck_path_children_2)<len(truck_path_parent_2) and len(remaining_truck_path_parent_1)>0:
        truck_path_children_2.append(remaining_truck_path_parent_1.pop(0))
    children_2.append(truck_path_children_2) 

    #per ogni coppia di nodi, se ne trovo qualcuna nei percorsi dei truck dei genitori ne importo i percorsi relativi che fa il drone
    i=0
    for node in truck_path_children_2:
        if node == truck_path_children_2[-1]:
            next_node=truck_path_children_2[0]
        else:
            next_node=truck_path_children_2[i+1]
        couple=[node,next_node]
        #se la coppia e nel path truck del padre 
        if contains(couple,truck_path_parent_1):
            #cerco se ce un path che contiene entrambi i nodi
            for path in parent_1:
                if all(node in path for node in couple) and parent_1.index(path)!=0:
                    children_new_path=path.copy()    
                    children_2.append(children_new_path)

        elif contains(couple,truck_path_parent_2):
            for path in parent_2:
                if all(node in path for node in couple) and parent_2.index(path)!=0:
                    children_new_path=path.copy()    
                    children_2.append(children_new_path)
        i+=1

    population.append(children_2)
    visited_list_truck=children_2[0]
    visited_list_drone=[]
    for path in children_2:
        if path!=children_2[0]:
            visited_list_drone+=path

    
    remove_double_visited_nodes(children_2)

    #boh nojn dovrebbero essercene mai
    #remove_paths_over_degree(children_2_index)

    two_points_paths=[]
    for path in children_2:
        if len(path)<3:
            two_points_paths.append(path)
    for path in two_points_paths:
        children_2.remove(path)

    while len(children_2)<15:
        children_2.append([])
    
    #paths illegali
    illegal_output_paths_index=[]
    not_empty_paths_index=[path_index for path_index in range(0,len(children_2)) if path_index!=0 and len(children_2[path_index])>0 ]
    #se ho tanti path del drone quanti nodi del truck, non posso scegliere un path vuoto come output
    if len(children_2[0])==len(not_empty_paths_index):
        empty_paths_index=[path_index for path_index in range(0,len(children_2)) if path_index!=0 and len(children_2[path_index])==0 ]
        illegal_output_paths_index+=empty_paths_index
    legal_output_paths_index=[i for i in range(0,len(children_2)) if i not in illegal_output_paths_index]

    #aggiungo i nodi non visitati
    not_visited_nodes=[node for node in graph_truck_clear.nodes if node not in visited_list_drone and node not in visited_list_truck]
    for node in not_visited_nodes:
        add_node_shortest_detour(children_2,legal_output_paths_index,node) 

                   
def population_crossover(population):
    fitness_wheel=compute_fitness_wheel(population)
    parents=random.choices(population,weights=fitness_wheel,k=2)
    parents_index=[population.index(parent) for parent in parents]
    
    solutions_crossover(population,parents_index[0],parents_index[1])
  
    
    
def eliminate_worst1(population):
    costs=[]
    for solution in population:
        costs.append(compute_solution_cost(solution))
    worst_cost=max(costs)
    worst_cost_index=costs.index(worst_cost)

    worst_solution=population[worst_cost_index]
    population.remove(worst_solution)

def eliminate_worsts(population,length_obj):
    population.sort(key=compute_solution_cost)
    while len(population)>length_obj:
        population.pop(-1)


def GA(population):  
    # trovo la sol con il costo piu bassso
    costs=[]
    for solution in population:
        costs.append(compute_solution_cost(solution))
    best_cost=min(costs)
    best_sol_i=costs.index(best_cost)
    best_sol=population[best_sol_i]
    i=0
    while i<INTERNAL_ITERATIONS:
        
        start=time.time()
 
        population_crossover(population)

        population_mutation(population,best_sol)

        eliminate_worst1(population)
        eliminate_worst1(population)

        test_costs=[]
        for solution in population:
            test_costs.append(compute_solution_cost(solution))
        minim=min(test_costs)
        if minim<best_cost:
            best_sol_i=test_costs.index(minim)
            best_sol=population[best_sol_i]
            best_cost=minim
            # print(multiprocessing.current_process(),"     ",best_sol_i,best_cost," i:",i,"tempo:",time.time()-start)
        i+=1
        # print(multiprocessing.current_process(),"      i:",i,"lunghezza population:",len(population)," tempo:",time.time()-start)
    return population,best_sol,best_cost

paths_colors=['red','#F7AE5D','#5B998D','#DDD900','#928017','#A1B1F8','#9DFD83','#408446',\
'#C7DA88','#0040FE','#A520A5','#A36CB1 ','#687044','#B391CB','#46822D']
figure=plt.figure(figsize=(9.5,9.5))
start=time.time()
#Creazione grafi e lettura files dei grafi
#region
graph_truck_clear = Custom_Graph()  
graph_drone_clear = Custom_Graph()    

#----------Inizio lettura coordinate e inserimento nel grafo e distanze drone-------------

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

    if coord_section:                                                 
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

#Inizializzo la matrice delle distanze del drone
global dist_drone
dist_drone = [ [ 0 for i in range(client_number_range) ] for j in range(client_number_range) ]
#Calcolo le distanze e riempio la matrice del drone
for i in range(1,client_number_range):   
    for j in range(1,client_number_range):
        dist_drone[i][j]=math.sqrt((points[j][0]-points[i][0])**2+(points[j][1]-points[i][1])**2)


#----------Inizio Lettura file distanze truck----------------

filename = 'Distanze_TRUCK.txt'      #nome file puntatore
with open(filename, 'r') as f:
    data = f.read()

istance = open(filename, 'r')  
dist_section = False
i=1
global dist_truck
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

#lettura popolazione e eliminazione duplicati
#region
#leggo il file con la popolazione
with open("GA_input.txt", 'r') as GA_input:
    starting_node=GA_input.readline()
    drone_autonomy=GA_input.readline()
    drone_capacity=GA_input.readline()
    population_dup=json.load(GA_input)
starting_node=int(starting_node)
drone_autonomy=int(drone_autonomy)
drone_capacity=int(drone_capacity)



INTERNAL_ITERATIONS=1000
MAX_POPULATION_SIZE=100
OUTER_ITERATIONS=5
NODE_PROBABILITY_FOR_MUTATION=0.99




if __name__ == '__main__':
    print("starting node = ",starting_node)
    print("drone autonomy = ",drone_autonomy)
    print("drone capacity = ",drone_capacity)
    print("lunghezza popolazione di input = ",len(population_dup))
    #elimino i duplicati
    population=[]
    for solution in population_dup:
        if not solution_duplicated(population,solution):
            population.append(solution)

        
    print("la popolazione prima di mutazioni è ",len(population))    
    costs=[]  
    for solution in population:
        costs.append(compute_solution_cost(solution))
        #print_graph_for_debug(solution)
    minim=min(costs)
    initial_best_index=costs.index(minim)
    initial_best_cost=minim
    print("costo sol prima di local=", initial_best_cost)
    
    #endregion

    
    
    #prima creo una poploazione di 100 sol
    start2=time.time()
    while len(population)<50:
        #CROSSOVER
        population_crossover(population)

    print("inizio il calcolo con ",multiprocessing.cpu_count()," processori\n")
 
    start=time.time()
    num_pop=multiprocessing.cpu_count()-1
    pbar=tqdm (range(OUTER_ITERATIONS), desc=str(num_pop)+" Populations Evolving... best cost = "+str(initial_best_cost)+"  pop size: "+str(len(population)),bar_format='{l_bar}{bar:70}{r_bar}{bar:-10b}')
    for j in pbar:
        #poi faccio partire
        start=time.time()
        populations_repeated=[population for i in range(14)]

        with Pool() as pool:
            populations_output=pool.map(GA,populations_repeated)
        time_for_1_cycle=time.time()-start
        cycles_remaining=OUTER_ITERATIONS-j
        percentagemi=round(j*100/OUTER_ITERATIONS,2)
        #i primi ciclo é sballato come tempisitche
        #if j>1:
            #print(percentagemi,"%, tempo rimanente:",time_for_1_cycle*cycles_remaining," secondi")
        
        new_populations=[]
        new_best_solutions=[]
        new_best_costs=[]
        
        for x in populations_output:
            new_populations.append(x[0])
            new_best_solutions.append(x[1])
            new_best_costs.append(x[2])
        
        new_population_dup=list(chain.from_iterable(new_populations))
        minim=min(new_best_costs)
       
        start1=time.time()
        eliminate_worsts(new_population_dup,MAX_POPULATION_SIZE)
        # print("lunghezza popolazinone dopo aver eliminato i peggiori: ",len(new_population_dup))
        # population=new_population_dup
        population=[]
        for solution in new_population_dup:
            if not solution_duplicated(population,solution):
                population.append(solution)    
        pbar.set_description(str(num_pop)+" Populations Evolving... best cost = "+str(initial_best_cost)+"  pop size: "+str(len(new_population_dup)))
        # print("tra elim e rimoz dup ci ho messo ",time.time()-start1)



    print("\n",time.time()-start2," secondi trascorsi per finire")
    costs=[]
    for solution in population:
        costs.append(compute_solution_cost(solution))
    minim=min(costs)
    print("prima della local avevo come costo migliore: ", initial_best_cost)
    print("TROVATO IL MIGLIORE:",costs.index(minim),minim)
    print("INTERNAL_ITERATIONS:",INTERNAL_ITERATIONS)
    print("MAX_POPULATION_SIZE:",MAX_POPULATION_SIZE)
    print("OUTER_ITERATIONS:",OUTER_ITERATIONS)
    print("NODE_PROBABILITY_FOR_MUTATION:",NODE_PROBABILITY_FOR_MUTATION)
    solution_best=population[costs.index(minim)]
    print_graph_for_debug(solution_best)
