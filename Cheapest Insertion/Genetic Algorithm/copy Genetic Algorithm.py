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
import itertools
import random

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
    def custom_remove_edge(self,node1,node2,solution_index):
        if self.has_edge(node1,node2):
            self.remove_edge(node1,node2)
        elif self.has_edge(node2,node1):
            self.remove_edge(node2,node1)
        else:
            print(population[solution_index])
            print_graph_for_debug(solution_index)
            raise CustomError_noedges(str(node1)+" "+str(node2))

def contains(small, big):
    for i in range(len(big)-len(small)+1):
        for j in range(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return True
    return False

def print_graph_for_debug(solution_index):
    solution=population[solution_index]
    graphs_couple=population_graphs[solution_index]
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total = nx.compose(graph_truck,graph_drone)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    visited_list_truck=population[solution_index][0]
    visited_list_drone=[]
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
                color_map.append('#669cd1')
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
    
def solution_duplicated(population,solution_input):

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

def create_graph(solution):
    graph_truck_list.append(graph_truck_clear.copy())
    graph_drone_list.append(graph_drone_clear.copy())
    graph_truck=graph_truck_list[-1]
    graph_drone=graph_drone_list[-1]
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
        drone_color=drone_colors[p]
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

def concat_drone_paths(solution_index,node):
    solution=population[solution_index]
    drone_paths=[path for path in solution if solution.index(path)!=0 and len(path)>0]

    paths_to_concat=[path for path in drone_paths if path[0]==node or path[-1]==node]
    if len(paths_to_concat)<2:
        print_graph_for_debug(solution_index)
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
            print_graph_for_debug(solution_index)
    if(cost>drone_autonomy or weight>drone_capacity):
        return False,False
    else:
        output=[concatenate_paths,path_to_concat_index_1,path_to_concat_index_2]
        return True,output

def compute_legal_inputs_nodes(solution_index,path_index):
    illegal_inputs_nodes=[]
    graphs_couple=population_graphs[solution_index]
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total = nx.compose(graph_truck,graph_drone)
    solution=population[solution_index]
    path=solution[path_index]

    #se e un path del dronbe

    if path_index!=0 and len(path)>2:
        illegal_inputs_nodes.append(path[0])
        illegal_inputs_nodes.append(path[-1])
    if path_index==0:
        for node in path:
            #il nodod de truck é illegale se ha grado >2 e non posso fondere i 2 cicli che gli arrivano
            if graph_total.degree(node)==3:
                illegal_inputs_nodes.append(node)
            if graph_total.degree(node)==4:
                concat_res,out=concat_drone_paths(solution_index,node)
                if concat_res==False:
                    illegal_inputs_nodes.append(node)
    
    legal_inputs_nodes=[node for node in path if node not in illegal_inputs_nodes]
    return legal_inputs_nodes

def add_node_shortest_detour(solution_index, legal_output_paths_index, node_input):
    min_path_index=-1
    solution=population[solution_index]
    graphs_couple=population_graphs[solution_index]
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total = nx.compose(graph_truck,graph_drone)
    #cerco il posto migliore per inserire il nodo, tale che il detour sia minimo
    solution=population[solution_index]
    diff_min=100000000000
    for path_output_index in legal_output_paths_index:
        path=population[solution_index][path_output_index]
        #print("path:",path)

        #scorro gli archi
        for node1,node2,attributes in graph_total.edges(data=True):
            # controllo se entrambi i 2 nodi sono in path
            #controllo per ilt ruck?????
            if (node1 in path and node2 in path):
                #calcolo il costo di questa prova, 
                #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
                #e tolgo l arco rimosso
                edge=[node1,node2]
                #se il path output é del truck ed é un arco libero(da un estremo all altro non ce un percorso del drone)
                
                if path_output_index==0 and edge_free(population[solution_index],node1,node2):
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
                # print("actual_cost:",actual_cost)
                # print("actual_weight:",actual_weight)
                if  actual_weight>drone_capacity:
                    #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                    break
                if (actual_diff<diff_min and (path_output_index==0 or actual_cost<=drone_autonomy)):
                    diff_min=actual_diff
                    min_path_index=path_output_index
                    min_edge=edge
                    #print("min_path:",min_path_index)
                    #print("min_edge:",min_edge)
            #se invece il path é nuovo controllo se l"arco é libero e se i nodi non sono pieni
            if len(path)==0 and edge_free(population[solution_index],node1,node2) and graph_total.degree(node1)<4 and graph_total.degree(node2)<4:
                edge=[node1,node2,"New"]
                new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2]) 
                actual_diff=new_edges_cost+100
                actual_cost=new_edges_cost
                actual_weight=weights_dict[node_input]
                # print("actual_cost:",actual_cost)
                # print("actual_weight:",actual_weight)
                if  actual_weight>drone_capacity:
                    #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
                    #sono nel caso inn cui sarebbe l"unico nodo del path, quindi il peso del singolo nodo é maggiore della capacità
                    break
                if (actual_diff<diff_min and actual_cost<=drone_autonomy):
                    #penalizzo la creazione di nuovi path
                    diff_min=actual_diff
                    min_path_index=path_output_index
                    min_edge=edge
                    #print("min_path:",min_path_index)
                   # print("min_edge:",min_edge)
    graphs_couple=population_graphs[solution_index]
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]

    #se non ho trovato un modo per aggiungere il nodo
    if min_path_index==-1:
        #per debug  fino a return False
        #region
        # print_graph_for_debug(solution_index)
        # for path_output_index in legal_output_paths_index:
        #     path=population[solution_index][path_output_index]
        #     #print("path:",path)

        #     #scorro gli archi
        #     for node1,node2,attributes in graph_total.edges(data=True):
        #         # controllo se entrambi i 2 nodi sono in path
        #         #controllo per ilt ruck?????
        #         if (node1 in path and node2 in path):
        #             #calcolo il costo di questa prova, 
        #             #somma dell'arco tra nodo1 nodoX e somma dell' arco tra nodo2 e nodoX
        #             #e tolgo l arco rimosso
        #             edge=[node1,node2]
        #             #se il path output é del truck ed é un arco libero(da un estremo all altro non ce un percorso del drone)
                    
        #             if path_output_index==0 and edge_free(population[solution_index],node1,node2):
        #                 new_edges_cost=(dist_truck[node_input][node1]) + (dist_truck[node_input][node2])
        #                 old_edge_cost=dist_truck[node1][node2]
        #                 #penalizzo la scelta di aggiugere al truck il nodo
        #                 actual_diff=new_edges_cost-old_edge_cost+10000
        #                 actual_cost=0
        #                 actual_weight=0
        #             #se il path_output é del drone e l'arco non é del truck(perché un arco del truck ha i nodi visitati dal path del drone) 
        #             elif((node1 in solution[0] and node2 in solution[0])==False ):
        #                 new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2])
        #                 old_edge_cost=dist_drone[node1][node2]
        #                 actual_diff=new_edges_cost-old_edge_cost
        #                 actual_cost=compute_path_drone_cost(path)-old_edge_cost+new_edges_cost
        #                 actual_weight=compute_drone_weight(path)+weights_dict[node_input]
        #             else:
        #                 # se non considero questi nodi provo i successivi
        #                 continue
        #             # print("actual_cost:",actual_cost)
        #             # print("actual_weight:",actual_weight)
        #             if  actual_weight>drone_capacity:
        #                 #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
        #                 break
        #             if (actual_diff<diff_min and (path_output_index==0 or actual_cost<=drone_autonomy)):
        #                 diff_min=actual_diff
        #                 min_path_index=path_output_index
        #                 min_edge=edge
        #                 #print("min_path:",min_path_index)
        #                 #print("min_edge:",min_edge)
        #         #se invece il path é nuovo controllo se l"arco é libero e se i nodi non sono pieni
        #         if len(path)==0 and edge_free(population[solution_index],node1,node2) and graph_total.degree(node1)<4 and graph_total.degree(node2)<4:
        #             edge=[node1,node2,"New"]
        #             new_edges_cost=(dist_drone[node_input][node1]) + (dist_drone[node_input][node2]) 
        #             actual_diff=new_edges_cost+100
        #             actual_cost=new_edges_cost
        #             actual_weight=weights_dict[node_input]
        #             # print("actual_cost:",actual_cost)
        #             # print("actual_weight:",actual_weight)
        #             if  actual_weight>drone_capacity:
        #                 #se aggiungom questo nodo al path , indipendentemente da quale punto lo andrò ad aggiungre, supero la capacità
        #                 #sono nel caso inn cui sarebbe l"unico nodo del path, quindi il peso del singolo nodo é maggiore della capacità
        #                 break
        #             if (actual_diff<diff_min and actual_cost<=drone_autonomy):
        #                 #penalizzo la creazione di nuovi path
        #                 diff_min=actual_diff
        #                 min_path_index=path_output_index
        #                 min_edge=edge
        #                 #print("min_path:",min_path_index)
        #             # print("min_edge:",min_edge)
        #endregion
        return False

    path_output=solution[min_path_index]
    
    #se é un novo path
    if len(min_edge)>2:
        path_output+=[min_edge[0],node_input,min_edge[1]]
        graph_drone.add_edge(min_edge[0],node_input,length=round(dist_drone[min_edge[0]][node_input],2),color=drone_colors[min_path_index])
        graph_drone.add_edge(min_edge[1],node_input,length=round(dist_drone[min_edge[1]][node_input],2),color=drone_colors[min_path_index])
    else:
        node_o_1_index=path_output.index(min_edge[0])
        node_o_2_index=path_output.index(min_edge[1])
        first_and_last=[path_output[0],path_output[-1]]
        if min_edge[0] in first_and_last and min_edge[1] in first_and_last:
            path_output.append(node_input)
        else:
            node_o_min_index=min(node_o_1_index,node_o_2_index)
            path_output.insert(node_o_min_index+1,node_input)

        if(min_path_index==0):
            graph_truck.custom_remove_edge(min_edge[0],min_edge[1],solution_index)
            graph_truck.add_edge(min_edge[0],node_input,length=round(dist_truck[min_edge[0]][node_input],2),color='r')
            graph_truck.add_edge(min_edge[1],node_input,length=round(dist_truck[min_edge[1]][node_input],2),color='r')
        else:        
            graph_drone.custom_remove_edge(min_edge[0],min_edge[1],solution_index)
            graph_drone.add_edge(min_edge[0],node_input,length=round(dist_drone[min_edge[0]][node_input],2),color=drone_colors[min_path_index])
            graph_drone.add_edge(min_edge[1],node_input,length=round(dist_drone[min_edge[1]][node_input],2),color=drone_colors[min_path_index])
    return True
    
def mutation_1(solution_index,path_input_index,node_input_index,legal_output_paths_index):
    check_graph(solution_index)
    node_concat=False
    #recupero il grafo
    graphs_couple=population_graphs[solution_index]
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total = nx.compose(graph_truck,graph_drone)
    
    #recupero i valori
    solution=population[solution_index]
    path_input=solution[path_input_index]
    node_input=path_input[node_input_index]
    print("ss=",solution)
    
    print("tolgo il nodo",node_input)
    #rimuovo il nodo dal grafo, e se il percorso ha solo due nodi allora lo elimino
    #print_graph_for_debug(solution_index)
    path_input.pop(node_input_index)
    if len(path_input)<3:
        path_input.clear()
    #rimuovo gli archi di quel nodo e riunisco gli archi adiacenti
    #caso truck
    if path_input_index==0:
        neighbors=[node for node in graph_truck.neighbors(node_input)]
        #print(neighbors)
        edges_to_be_removed=list(graph_truck.edges(node_input))
        graph_truck.remove_edges_from(edges_to_be_removed)
        graph_truck.add_edge(neighbors[0],neighbors[1],length=round(dist_truck[neighbors[0]][neighbors[1]],2),color='r')

        #guardo se il nodo era usato dal drone equindi devo fondere i path, se no non devo farlo
        graph_total = nx.compose(graph_truck,graph_drone)
        if(graph_total.degree(node_input)>0):
            node_concat=True
            #sistemo i path del drone
            #print_graph_for_debug(solution_index)
            res,concat_output=concat_drone_paths(solution_index,node_input)
            print("concatenated path= ",concat_output[0])
            first_path_index=concat_output[1]
            second_path_index=concat_output[2]
            total_path=concat_output[0]
            solution[first_path_index]=total_path
            solution[second_path_index].clear()
            #sistemo il grafo del drone
            neighbors_drone=[node for node in graph_drone.neighbors(node_input)]
            if len(neighbors_drone)<2:
                print_graph_for_debug(solution_index)
            #print_graph_for_debug(solution_index)
            edges_to_be_removed=list(graph_drone.edges(node_input))
            graph_drone.remove_edges_from(edges_to_be_removed)
            if len(path_input)>2:
                graph_drone.add_edge(neighbors_drone[0],neighbors_drone[1],length=round(dist_drone[neighbors_drone[0]][neighbors_drone[1]],2),color=drone_colors[path_input_index])
            for solutiontest in population:
                sol_ind=population.index(solutiontest)
                for path in solutiontest:
                    if len(path)<3 and len(path)!=0:
                        solution_index=population.index(solutiontest)
                        print_graph_for_debug(solution_index)
                    for node in path:
                        if path.count(node)>1:
                            print_graph_for_debug(solution_index)
                two_nodes=return_double_visited_nodes(sol_ind)
                if len(two_nodes)>0:
                    print_graph_for_debug(solution_index)
            
    #caso drone
    else:
        neighbors=[node for node in graph_drone.neighbors(node_input)]
        if len(neighbors)<2:
            print_graph_for_debug(solution_index)
            check_graph(solution_index)
        #print(neighbors)
        edges_to_be_removed=list(graph_drone.edges(node_input))
        graph_drone.remove_edges_from(edges_to_be_removed)
        #dovrebbe essere gia sempre >2 ?????
        if len(path_input)>2:
            #print_graph_for_debug(solution_index)
            graph_drone.add_edge(neighbors[0],neighbors[1],length=round(dist_drone[neighbors[0]][neighbors[1]],2),color=drone_colors[path_input_index])
        #aggiungo il nodo in path_ouput nel modo migliore
        for solutiontest in population:
            sol_ind=population.index(solutiontest)
            for path in solutiontest:
                if len(path)<3 and len(path)!=0:
                    solution_index=population.index(solutiontest)
                    print_graph_for_debug(solution_index)
                for node in path:
                    if path.count(node)>1:
                        print_graph_for_debug(solution_index)
            two_nodes=return_double_visited_nodes(sol_ind)
            if len(two_nodes)>0:
                print_graph_for_debug(solution_index)
    #print_graph_for_debug(solution_index)
    print("sa=",solution)
    #se aggiungo nel miglior modo il nodo ed avevo concatenato, lo trovo visitato 2 volte
    if(node_concat==False):
        add_node_shortest_detour(solution_index, legal_output_paths_index, node_input)
    print("sb=",solution)

    
                
    #print_graph_for_debug(solution_index)
    #print("min_path_FINALE:",min_path_index)
    #print("min_edge_FINALE:",min_edge)

def population_mutation():
    all_solution_probabilities=[]
    start=time.time()
    SEEDS=list(range(0,100*15))
    for i in range(0,100):
        paths_probabilities=[]
        for j in range(0,15):
            np.random.seed(SEEDS[i+j])
            nodes_probabilities=np.random.rand(30)
            paths_probabilities.append(nodes_probabilities)
        all_solution_probabilities.append(paths_probabilities)
    to_be_mutated_list=[]
    all_mutated_list=[]
    for solution in population:
        solution_index=population.index(solution)
        if solution!=population[solution_index]:
            print("526")
            print(solution)
            print(population[solution_index])
            print_graph_for_debug(solution_index)
        #print("\n\n\nsoluzione numero",solution_index)
        #print_graph_for_debug(solution_index)
        #mutation_solution=random.random()   
        for path in solution:
            #se sono nel path del truck e ho 2 nodi non faccio la mutazione,rimarrei con un nodo
            if solution.index(path)!=0 or len(path)>2:             
                path_index=solution.index(path)
                for node in path:
                    #scelgo quali nodi mutare
                    if node not in path:
                        print_graph_for_debug(solution_index)
                    node_index=path.index(node)
                    #probability_node=all_solution_probabilities[solution_index][path_index][node_index]
                    probability_node=random.random() 
                    if(probability_node>0.975):
                        value=[path_index,node_index]
                        to_be_mutated_list.append(value)
                       
                        #print("mutation_population sol:",solution_index," path:",path_index," nodo:",node_index, "tobemutatelist=",to_be_mutated_list)
                
        

        while(len(to_be_mutated_list)>0):
            value_index=to_be_mutated_list.pop()
            path_input_index=value_index[0]
            node_input_index=value_index[1]
            path=solution[path_input_index]
            #se il path del nodo da mutare esiste ancora
            if len(path)>0:
                node_input=path[node_input_index]
                #calcolo i nodi che possono essere rimossi dal path senza problemi 
            
                #print_graph_for_debug(solution_index)
                #print("s=",solution)
                legal_inputs_nodes=compute_legal_inputs_nodes(solution_index,path_input_index)
                #print("legal_inputs_nodes_indexes:",solution_index,path_input_index,legal_inputs_nodes)
                #se il nodo la cui probabilità mi dice di rimoverlo é nella lista dei nodi legali
                if node_input in legal_inputs_nodes:
                    all_mutated_list.append(node_input_index)
                    #print("path input=",path_input_index)
                    illegal_output_paths_index=[]
                    if path_input_index!=0:
                        #se rendo illegale il riaggiungimento al path del truck rischio che il nodo non sia aggiungibile a nessun path
                        illegal_output_paths_index=[path_input_index]
                    not_empty_paths_index=[path_index for path_index in range(0,len(solution)) if path_index!=0 and len(solution[path_index])>0 ]
                    #se ho tanti path del drone quanti nodi del truck, non posso scegliere un path vuoto come output
                    if len(solution[0])==len(not_empty_paths_index):
                        print("AAAAAAAAAA")
                        empty_paths_index=[path_index for path_index in range(0,len(solution)) if path_index!=0 and len(solution[path_index])==0 ]
                        illegal_output_paths_index+=empty_paths_index
                    legal_output_paths_index=[i for i in range(0,len(solution)) if i not in illegal_output_paths_index]
            
                    solution_index=population.index(solution)
                    graphs_couple=population_graphs[solution_index]
                    graph_truck=graphs_couple[0]
                    graph_drone=graphs_couple[1]
                    graph_total=nx.compose(graph_truck,graph_drone)
                    for node in graph_total:
                        if graph_total.degree(node)>4:
                            for i in range(0,10):
                                print("IL NODO HA GRADO MAGGIORE DI 4: ",node)
                                print_graph_for_debug(solution_index)
                            raise error
                    #soluzione, path input,nodo da spostare, possibili path di destinazione
                    mutation_1(solution_index,path_input_index,node_input_index,legal_output_paths_index)
                    check_graph(solution_index)
                    graphs_couple=population_graphs[solution_index]
                    graph_truck=graphs_couple[0]
                    graph_drone=graphs_couple[1]
                    graph_total=nx.compose(graph_truck,graph_drone)
                    for node in graph_total:
                        if graph_total.degree(node)>4:
                            for i in range(0,10):
                                print("IL NODO HA GRADO MAGGIORE DI 4: ",node)
                                print_graph_for_debug(solution_index)
                            raise error
            
        
    print("fatte ",len(all_mutated_list)," mutazioni")
    print(time.time()-start," secs per mutare")     
 
def compute_fitness_wheel():
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

def starting_drone_point(solution_index,node):
    solution=population[solution_index]
    starting_paths=[]
    for path in solution:
        if len(path)>0:
            if node==path[0] or node==path[-1]:
                starting_paths.append(solution.index(path))
    if len(starting_paths)>0:
        return starting_paths
    else:
        return -1

def remove_double_visited_nodes(solution_index):
    solution=population[solution_index]
    drone_nodes=solution.copy()
    #rimuovo il truck
    drone_nodes.pop(0)
    to_be_checked_nodes=solution.copy()
    # graphs_couple=population_graphs[solution_index]
    # graph_truck=graphs_couple[0]
    # graph_drone=graphs_couple[1]
   
    for path in solution:
        to_be_removed=[]
        if path==solution[0]:
            for node in path:
                #per ogni nodo in questo path , lo rimuovo se e presente in altri percorsi
                #ma non e un nodo di inzio o di fine in quaslisasi percorso
                if any(node in path_i for path_i in drone_nodes) and starting_drone_point(solution_index,node)==-1:
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
        # print_graph_for_debug(solution_index)

def check_graph(solution_index):
    solution=population[solution_index]
    graphs_couple1=population_graphs[solution_index]
    graph_truck1=graphs_couple1[0]
    graph_drone1=graphs_couple1[1]
    graph_total1 = nx.compose(graph_truck1,graph_drone1)


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
        drone_color=drone_colors[p]
        if len(drone_path)>1:
            i=0
            while i < len(drone_path)-1:
                node1=drone_path[i]
                node2=drone_path[i+1]
                graph_drone.add_edge(node1,node2,length=round(dist_drone[node1][node2],2),color=drone_color)
                i+=1
            
        p+=1
    graphs_couple2=[graph_truck,graph_drone]
    graph_truck2=graphs_couple2[0]
    graph_drone2=graphs_couple2[1]
    graph_total = nx.compose(graph_truck2,graph_drone2)
    edges1=graph_total1.edges()
    edges2=graph_total.edges()
    edges1=list(edges1)
    edges2=list(edges2)
    edges1.sort()
    edges2.sort()
    print("\n")
    print(solution_index)
    print(edges1)
    print(edges2)
    if edges1!=edges2:
        print_graph_for_debug(solution_index)
        graph_total = nx.compose(graph_truck,graph_drone)
        edges = graph_total.edges()
        colors = [graph_total[u][v]['color'] for u,v in edges]
        visited_list_truck=population[solution_index][0]
        visited_list_drone=[]
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
                    color_map.append('#669cd1')
                else: 
                    color_map.append('green') 
        #colori degli archi aggiunti ogni volta vh faccio add edge
        
        figure.canvas.manager.window.wm_geometry("+%d+%d" % (-10, 00))
        plt.clf()   #clearo il grafico precedente
        nx.draw(graph_total,points,font_size=8, node_size=120,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
        labels = nx.get_edge_attributes(graph_total, 'length') 
        #per stampare le distanze
        nx.draw_networkx_edge_labels(graph_total,points, edge_labels=labels, font_size=7)
     
    
        plt.show()       
def return_double_visited_nodes(solution_index):
    solution=population[solution_index]
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
                if any(node in path_i for path_i in drone_nodes) and starting_drone_point(solution_index,node)==-1:
                    to_be_removed.append([path_ixxx,node])

        else:    
            to_be_checked_nodes.remove(path)
            for node in path:
                #per ogni nodo in questo path , lo rimuovo se e presente in altri percorsi, ma non e un nodo di inzio o di fine di questo path
                #non sara inizio o fine di altri percorsi per come ho costruito i path del drone: per igni coppia di nodi hi un path che parte da quelli
                if any(node in path_i for path_i in to_be_checked_nodes) and node!=path[0] and node!=path[-1]:
                    to_be_removed.append([path_ixxx,node])
                    
    return to_be_removed
        

def remove_paths_over_degree(solution_index):       
    solution=population[solution_index]
    graphs_couple=population_graphs[solution_index]
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total=nx.compose(graph_truck,graph_drone)

    #print_graph_for_debug(solution_index)

    for node in graph_total:
        if graph_total.degree(node)>4:
            paths_degreee_indexes=starting_drone_point(solution_index,node)
            paths_degreee=[solution[index] for index in paths_degreee_indexes]
            paths_degreee.sort(key=len)
            solution.remove(paths_degreee[0])
      
def solutions_crossover(parent_1_index,parent_2_index):
    parent_1=population[parent_1_index].copy()
    parent_2=population[parent_2_index].copy()

    children_1=[]
    #costruisco il percorso del truck del figlio1
    truck_path_children_1=[]
    truck_path_parent_1=parent_1[0]
    truck_path_parent_2=parent_2[0]
    cuts_points=random.choices(range(0,len(truck_path_parent_1)),k=2)
    #cuts_points=[4,3]
    print("crossover di")
    print("p1: ",parent_1)
    print("p2: ",parent_2)
    print("cuts: ",cuts_points)

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
    children_1_index=population.index(children_1)
    
    remove_double_visited_nodes(children_1_index)

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

    #creo il grafo
    
    population_graphs.append(create_graph(children_1))

    #aggiungo i nodi non visitati
    #print_graph_for_debug(children_1_index)
    not_visited_nodes=[node for node in graph_truck_clear.nodes if node not in visited_list_drone and node not in visited_list_truck]
    for node in not_visited_nodes:
        #print(node)
        add_node_shortest_detour(children_1_index,legal_output_paths_index,node) 
        #print_graph_for_debug(children_1_index)
    
    graphs_couple=population_graphs[children_1_index]
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total=nx.compose(graph_truck,graph_drone)
    check_graph(children_1_index)
    #print_graph_for_debug(children_1_index)
    for node in graph_total:
        if graph_total.degree(node)>4:
            for i in range(0,10):
                print("IL NODO HA GRADO MAGGIORE DI 4: ",node)
                print_graph_for_debug(children_1_index)
            raise error
                   
def population_crossover():
    fitness_wheel=compute_fitness_wheel()
    parents=random.choices(population,weights=fitness_wheel,k=2)
    parents_index=[population.index(parent) for parent in parents]
    #parents_index=[4,8]
    
    
    #print("scelti i genitori:",parents_index)
    #print("crossover di ",parents_index[0]," e ",parents_index[1])
    #print(population[parents_index[0]],population[parents_index[1]])
    solutions_crossover(parents_index[0],parents_index[1])
    
    
def eliminate_worst():
    costs=[]
    for solution in population:
        costs.append(compute_solution_cost(solution))
    worst_cost=max(costs)
    worst_cost_index=costs.index(worst_cost)

    worst_solution=population[worst_cost_index]
    population.remove(worst_solution)

    worst_graph=population_graphs[worst_cost_index]
    population_graphs.remove(worst_graph)
    

if __name__ == '__main__':
    drone_colors=['red','#3F00FF','#00EB2D','#DDD900','#3C350A','#A1B1F8','#9DFD83','#8CFF00',\
    '#C6FF00','#0040FE','#5B998D','#A36CB1 ','#687044','#B391CB','#27670C']
    figure=plt.figure(figsize=(9.5,9.5))
    start=time.time()
    #Creazione grafi e lettura files dei grafi
    #region
    graph_truck_clear = Custom_Graph()  
    graph_drone_clear = Custom_Graph()    

    #----------Inizio lettura coordinate e inserimento nel grafo e distanze drone-------------

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
    print("starting node = ",starting_node)
    print("drone autonomy = ",drone_autonomy)
    print("drone capacity = ",drone_capacity)
    print("lunghezza popolazione di input = ",len(population_dup))
    
    #elimino i duplicati
    population=[]
    for solution in population_dup:
        if not solution_duplicated(population,solution):
            
            population.append(solution)
            #print(compute_solution_cost(solution))
        
    print("la popolazione prima di mutazioni è ",len(population))      
    #print(time.time()-start," secs")
    
    #ricostruisco i grafi dalla popolazione
    population_graphs=[]
    #soluz non concorrente
    graph_truck_list=[]
    graph_drone_list=[]
    
    for solution in population:
        population_graphs.append(create_graph(solution))

   # soluz concorrente, piu lenta con 32 grafi 
    # with Pool() as pool:
    #     population_graphs=pool.starmap(create_graph,zip(population, graph_truck_list,graph_drone_list))

 #   for graphs_couple in population_graphs:
 #        print(population_graphs.index(graphs_couple))
 #        print_graph_for_debug(population_graphs.index(graphs_couple))
 #        print(population[population_graphs.index(graphs_couple)])
 #       
    print("creati",len(population_graphs),"grafi")
    print(time.time()-start," secs per creare e rimuovre i duplicati di soluzioni") 
    
    #endregion
   # print_graph_for_debug(5)
    #print(compute_solution_cost(population[5]))
    #prima creo una poploazione di 200
    while len(population)<50:
        #CROSSOVER
        population_crossover()

        
    costs=[]
   #poi faccio partire
    i=0
    while i<2000:
        #CROSSOVER
        population_crossover()
        for solution in population:
            solution_index=population.index(solution)
            check_graph(solution_index)
        #MUTAZIONE
        population_mutation()
        for solution in population:
            solution_index=population.index(solution)
            check_graph(solution_index)

        eliminate_worst()
        for solution in population:
            solution_index=population.index(solution)
            check_graph(solution_index)

        for solution in population:
            costs.append(compute_solution_cost(solution))
        minim=min(costs)
        print("TROVATP",costs.index(minim),minim)
        i+=1
    print(time.time()-start," generate 2000 sol")
    costs=[]
    for solution in population:
        costs.append(compute_solution_cost(solution))
    minim=min(costs)
    print("TROVATP",costs.index(minim),minim)
