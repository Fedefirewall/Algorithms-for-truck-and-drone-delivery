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
import multiprocessing, logging
import copy
import sys


def create_graph(solution):

    graph_truck=graph_truck_clear.copy()
    graph_drone=graph_drone_clear.copy()
    graphs_couple=[]
    i=0
    #dato che ho il nodo viistato 2 volte come codifica
    truck_path=copy.deepcopy(solution[0])
    truck_path.pop(-1)
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

def print_graph_for_debug(solution):
    
    graphs_couple=create_graph(solution)
    graph_truck=graphs_couple[0]
    graph_drone=graphs_couple[1]
    graph_total = nx.compose(graph_truck,graph_drone)
    edges = graph_total.edges()
    colors = [graph_total[u][v]['color'] for u,v in edges]
    visited_list_truck=solution[0]
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
    
    #figure.canvas.manager.window.wm_geometry("+%d+%d" % (-10, 00))
    plt.clf()   #clearo il grafico precedente
    nx.draw(graph_total,points,font_size=8, node_size=120,with_labels=True, arrowsize=20,edge_color=colors,node_color=color_map)  # create a graph with the tour
    labels = nx.get_edge_attributes(graph_total, 'length') 
    #per stampare le distanze
    nx.draw_networkx_edge_labels(graph_total,points, edge_labels=labels, font_size=7)
     
    
    plt.show()         # display it interactively 

def compute_solution_cost_by_sol(solution):    
    cost=0
    
    for i in range (len(solution[0])-1):
        cost+=dist_truck[solution[0][i]][solution[0][i+1]]
    cost+=dist_truck[solution[0][i+1]][solution[0][0]]

    return cost

def two_opt_drone(node1, node2, node3, node4, d_p, t_p, d_d):
    #Devo controllare i nodi, se nodo1 > nodo3 li devo invertire
    drone_path_new = copy.deepcopy(d_p)
    #INIZIO DELLO SCAMBIO ARCHI E METTO APOSTO I PERCORSI DEL DRONE 
    #SCAMBIO PUNTI INZIALI DEL DRONE
    cost_drone = 0
    drone_weight = 0
    
    for i in range(0, len(drone_path_new)):
        if t_p[node1] == drone_path[i][0] or t_p[node1] == drone_path[i][-1]:
            if t_p[node2] == drone_path[i][0] or t_p[node2] == drone_path[i][-1]:
                cost_drone = 0
                drone_weight = 0
                if not any(t_p[node3] in sl for sl in drone_path):
                    if any(t_p[node4] in sl for sl in drone_path):
                        if t_p[node2] == drone_path[i][0]:
                            drone_path_new[i][0] = t_p[node4]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue
                        else:
                            drone_path_new[i][-1] = t_p[node4]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue          
                if any(t_p[node3] in sl for sl in drone_path):
                    if not any(t_p[node4] in sl for sl in drone_path):
                        if t_p[node2] == drone_path[i][-1]:
                            drone_path_new[i][-1] = t_p[node3]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue
                        else:
                            drone_path_new[i][0] = t_p[node3]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue
                if not any(t_p[node3] in sl for sl in drone_path):
                    if not any(t_p[node4] in sl for sl in drone_path):
                        print("Impossibile effettuare scambio del percorso del drone perchè nessuno dei due nodi dell'arco è attraversato dal drone.")
                        break
                if t_p[node2] == drone_path[i][-1]:
                    drone_path_new[i][-1] = t_p[node3]
                    for k in range(0, len(drone_path_new[i])- 1):
                        nodox = drone_path_new[i][k]
                        nodoy = drone_path_new[i][k+1]
                        cost_drone += d_d[nodox][nodoy]
                        drone_weight += weights_dict[nodoy]
                        if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                            #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                            return drone_path_new, cost_drone, drone_weight
                        else:
                            continue
                    continue
                elif t_p[node2] == drone_path[i][0]:
                    drone_path_new[i][0] = t_p[node3]
                    for k in range(0, len(drone_path_new[i])- 1):
                        nodox = drone_path_new[i][k]
                        nodoy = drone_path_new[i][k+1]
                        cost_drone += d_d[nodox][nodoy]
                        drone_weight += weights_dict[nodoy]
                        if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                            #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                            return drone_path_new, cost_drone, drone_weight
                        else:
                            continue
                    continue
        if t_p[node3] == drone_path[i][0] or t_p[node3] == drone_path[i][-1]:
            if t_p[node4] == drone_path[i][0] or t_p[node4] == drone_path[i][-1]:
                cost_drone = 0
                drone_weight = 0
                if not any(t_p[node1] in sl for sl in drone_path):
                    if any(t_p[node2] in sl for sl in drone_path):
                        if t_p[node3] == drone_path[i][0]:
                            drone_path_new[i][0] = t_p[node2]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue
                        else:
                            drone_path_new[i][-1] = t_p[node2]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue
                if any(t_p[node1] in sl for sl in drone_path):
                    if not any(t_p[node2] in sl for sl in drone_path):
                        if t_p[node3] == drone_path[i][-1]:
                            drone_path_new[i][-1] = t_p[node1]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue
                        else:
                            drone_path_new[i][0] = t_p[node1]
                            for k in range(0, len(drone_path_new[i])- 1):
                                nodox = drone_path_new[i][k]
                                nodoy = drone_path_new[i][k+1]
                                cost_drone += d_d[nodox][nodoy]
                                drone_weight += weights_dict[nodoy]
                                if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                                    #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                                    return drone_path_new, cost_drone, drone_weight
                                else:
                                    continue
                            continue
                if not any(t_p[node1] in sl for sl in drone_path):
                    if not any(t_p[node1] in sl for sl in drone_path):
                        print("Impossibile effettuare scambio del percorso del drone perchè nessuno dei due nodi dell'arco è attraversato dal drone.")
                        break
                if t_p[node3] == drone_path[i][-1]:
                    drone_path_new[i][-1] = t_p[node2]
                    for k in range(0, len(drone_path_new[i])- 1):
                        nodox = drone_path_new[i][k]
                        nodoy = drone_path_new[i][k+1]
                        cost_drone += d_d[nodox][nodoy]
                        drone_weight += weights_dict[nodoy]
                        if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                            #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                            return drone_path_new, cost_drone, drone_weight
                        else:
                            continue
                    continue
                elif t_p[node3] == drone_path[i][0]:
                    drone_path_new[i][0] = t_p[node2]
                    for k in range(0, len(drone_path_new[i])- 1):
                        nodox = drone_path_new[i][k]
                        nodoy = drone_path_new[i][k+1]
                        cost_drone += d_d[nodox][nodoy]
                        drone_weight += weights_dict[nodoy]
                        if cost_drone > drone_autonomy or drone_weight > drone_capacity:
                            #print("Il costo del nuovo percorso ", drone_path_new[i], cost_drone, " supera l'autonomia del drone per cui non va bene!!!")
                            return drone_path_new, cost_drone, drone_weight
                        else:
                            continue
                    continue

    return drone_path_new, cost_drone, drone_weight

def two_opt_truck(node1, node2, node3, node4, t_p, d_t):

    cost_truck = 0
    truck_path_new = t_p.copy()  #Nuova path del truck con gli archi scambiati e devo cercare di cambiare anche il percorso del truck 
    
    sequence_to_reverse = t_p[node2:(node3 + 1)]
    
    del truck_path_new[node2:(node3 + 1)]
    for i in sequence_to_reverse:
        truck_path_new.insert(node2, i)
    
    for i in range(0, len(truck_path_new) - 1):
        element1 = truck_path_new[i]
        element2 = truck_path_new[i + 1]
        cost_truck += dist_truck[element1][element2]
    
    return truck_path_new, cost_truck

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

graph_truck_clear = Custom_Graph()  
graph_drone_clear = Custom_Graph()
#Creazione grafi
graph_truck = Custom_Graph()  
graph_drone = Custom_Graph()

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
#endregion

#----------Inizio Lettura file distanze truck----------------
#region
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

drone_colors=['red','#3F00FF','#00EB2D','#DDD900','#3C350A','#A1B1F8','#9DFD83','#8CFF00',\
'#C6FF00','#0040FE','#5B998D','#A36CB1 ','#687044','#B391CB','#27670C']
figure=plt.figure(figsize=(9.5,9.5))
start=time.time()

with open("2_OPT_input.txt", 'r') as Two_OPT_input:
    starting_node=Two_OPT_input.readline()
    drone_autonomy=Two_OPT_input.readline()
    drone_capacity=Two_OPT_input.readline()
    population_dup=json.load(Two_OPT_input)
starting_node=int(starting_node)
drone_autonomy=int(drone_autonomy)
drone_capacity=int(drone_capacity)

#Lista del percorso che fa il truck
truck_path = population_dup[0].copy()

#Liste dei diversi percorsi che fa il drone
#drone_path = copy.deepcopy(population_dup[1:])
drone_path = []
for i in range(1, len(population_dup)):
    if population_dup[i] != []:
        drone_path.append(population_dup[i])
    else:
        continue

if truck_path[-1] != truck_path[0]:
    truck_path.append(truck_path[0])
cost_truck_best = 0
for j in range(0, len(truck_path) -1):
    nodo1 = truck_path[j]
    nodo2 = truck_path[j+1]
    cost_truck_best += dist_truck[nodo1][nodo2]

print("Il truck all'inizio percorre la seguente route migliore: ", truck_path, " \nCon un costo di: ", cost_truck_best)
print("Il drone percorre inizialmente le seguenti route: ", drone_path)

truck_path.pop(-1)
solution = []
solution.append(truck_path)
for element in drone_path:
    solution.append(element)
print_graph_for_debug(solution)


if __name__ == '__main__':
    
    truck_path.append(truck_path[0])
    #SCORRO TUTTI GLI ARCHI E NE FACCIO 2-OPT DOVE è POSSIBILE
    population = []  #Popolazione che darò in pasto all'algoritmo genetico 
    i = 0
    while i < (len(truck_path) - 1):
        for j in range(0, len(truck_path) - 1):
            node1_switch_truck_index = i
            node2_switch_truck_index = i + 1
            if truck_path[i] == truck_path[j]:
                continue #Continuo ciclo senza fare nulla
            elif truck_path[i] != truck_path[j]:
                node3_switch_truck_index = j
                if truck_path[node3_switch_truck_index] == truck_path[node2_switch_truck_index]: 
                    continue #continuo ciclo senza fare nulla
                else:
                    node4_switch_truck_index = node3_switch_truck_index + 1
                    if truck_path[node4_switch_truck_index] == truck_path[node1_switch_truck_index]:
                        continue #continuo ciclo senza fare nulla
                    elif node1_switch_truck_index > node3_switch_truck_index: #Scambio gli archi
                        node1_switch_truck_index = node3_switch_truck_index
                        node2_switch_truck_index = node1_switch_truck_index + 1
                        node3_switch_truck_index = i
                        node4_switch_truck_index = node3_switch_truck_index + 1
                        print("Provo l'algoritmo 2-opt con l'arco: ", truck_path[node3_switch_truck_index], " -- ", truck_path[node4_switch_truck_index], "\nEd l'arco ", truck_path[node1_switch_truck_index], " -- ", truck_path[node2_switch_truck_index])
                        sol_drone, cost_new_drone, drone_weight_new = two_opt_drone(node1_switch_truck_index, node2_switch_truck_index, node3_switch_truck_index, node4_switch_truck_index, drone_path, truck_path, dist_drone)
                        if cost_new_drone < drone_autonomy and drone_weight_new < drone_capacity and drone_weight_new != 0:
                            print("Il nuovo percorso del drone è: ", sol_drone)
                            sol_truck, cost_truck = two_opt_truck(node1_switch_truck_index, node2_switch_truck_index, node3_switch_truck_index, node4_switch_truck_index, truck_path, dist_truck)
                            if cost_truck < cost_truck_best:
                                print("Il primo arco preso in considerazione nel truck è tra i nodi: ", truck_path[node1_switch_truck_index], " -- ", truck_path[node2_switch_truck_index], " ,ed ha costo: ", dist_truck[truck_path[node1_switch_truck_index]][truck_path[node2_switch_truck_index]])
                                print("Il secondo arco preso in considerazione nel truck è tra i nodi", truck_path[node3_switch_truck_index], " -- ", truck_path[node4_switch_truck_index], " ,ed ha costo: ", dist_truck[truck_path[node3_switch_truck_index]][truck_path[node4_switch_truck_index]])
                                print("Il nuovo primo arco preso in considerazione nel truck è tra i nodi: ", truck_path[node1_switch_truck_index], " -- ", truck_path[node3_switch_truck_index], " ,ed ha costo: ", dist_truck[sol_truck[node1_switch_truck_index]][sol_truck[node2_switch_truck_index]])
                                print("Il nuovo secondo arco preso in considerazione nel truck è tra i nodi", truck_path[node2_switch_truck_index], " -- ", truck_path[node4_switch_truck_index], " ,ed ha costo: ", dist_truck[sol_truck[node3_switch_truck_index]][sol_truck[node4_switch_truck_index]])

                                print("il nuovo percorso del truck", sol_truck, " ha costo migliore: ", cost_truck)
                                
                                drone_path = sol_drone
                                truck_path = sol_truck
                                cost_truck_best = cost_truck
                                solution = []
                                solution.append(sol_truck)
                                for element in sol_drone:
                                    solution.append(element)
                                
                                population.append(solution)    #Aggiorno la popolazione con il nuovo miglioramento trovato                           
                                print_graph_for_debug(solution)
                            else:
                                print("Il nuovo percorso del truck non va bene perchè ha costo: ", cost_truck)
                        elif cost_new_drone > drone_autonomy:
                            print("Il nuovo percorso del drone ", sol_drone, " non va bene perché un ciclo supera l'autonomia del drone con costo: ", cost_new_drone)
                        elif drone_weight_new > drone_capacity:
                            print("Il nuovo percorso del drone ", sol_drone, "non va bene perché un ciclo supera la capacità del drone con un peso di: ", drone_weight_new)
                    else:
                        print("Provo l'algoritmo 2-opt con l'arco: ", truck_path[node1_switch_truck_index], " -- ", truck_path[node2_switch_truck_index], "\nEd l'arco ", truck_path[node3_switch_truck_index], " -- ", truck_path[node4_switch_truck_index])
                        sol_drone, cost_new_drone, drone_weight_new = two_opt_drone(node1_switch_truck_index, node2_switch_truck_index, node3_switch_truck_index, node4_switch_truck_index, drone_path, truck_path, dist_drone)
                        if cost_new_drone <= drone_autonomy and drone_weight_new <= drone_capacity and drone_weight_new != 0:
                            sol_truck, cost_truck = two_opt_truck(node1_switch_truck_index, node2_switch_truck_index, node3_switch_truck_index, node4_switch_truck_index, truck_path, dist_truck)
                            print("Il nuovo percorso del drone è: ", sol_drone)
                            if cost_truck < cost_truck_best:
                                print("Il primo arco preso in considerazione nel truck è tra i nodi: ", truck_path[node1_switch_truck_index], " -- ", truck_path[node2_switch_truck_index], " ,ed ha costo: ", dist_truck[truck_path[node1_switch_truck_index]][truck_path[node2_switch_truck_index]])
                                print("Il secondo arco preso in considerazione nel truck è tra i nodi", truck_path[node3_switch_truck_index], " -- ", truck_path[node4_switch_truck_index], " ,ed ha costo: ", dist_truck[truck_path[node3_switch_truck_index]][truck_path[node4_switch_truck_index]])
                                print("Il nuovo primo arco preso in considerazione nel truck è tra i nodi: ", truck_path[node1_switch_truck_index], " -- ", truck_path[node3_switch_truck_index], " ,ed ha costo: ", dist_truck[sol_truck[node1_switch_truck_index]][sol_truck[node2_switch_truck_index]])
                                print("Il nuovo secondo arco preso in considerazione nel truck è tra i nodi", truck_path[node2_switch_truck_index], " -- ", truck_path[node4_switch_truck_index], " ,ed ha costo: ", dist_truck[sol_truck[node3_switch_truck_index]][sol_truck[node4_switch_truck_index]])

                                print("il nuovo percorso del truck", sol_truck, " ha costo migliore: ", cost_truck)

                                drone_path = sol_drone
                                truck_path = sol_truck
                                cost_truck_best = cost_truck
                                solution = []
                                solution.append(sol_truck)
                                for element in sol_drone:
                                    solution.append(element)

                                population.append(solution)    #Aggiorno la popolazione con il nuovo miglioramento trovato
                                print_graph_for_debug(solution)
                            else:
                                print("Il nuovo percorso del truck non va bene perchè ha costo: ", cost_truck)
                        elif cost_new_drone > drone_autonomy:
                            print("Il nuovo percorso del drone ", sol_drone, " non va bene perché un ciclo supera l'autonomia del drone con costo: ", cost_new_drone)
                        elif drone_weight_new > drone_capacity:
                            print("Il nuovo percorso del drone ", sol_drone, "non va bene perché un ciclo supera la capacità del drone con un peso di: ", drone_weight_new)
        i += 1
    #Indice della posizione dei nodi da switchare per truck
    #node1_switch_truck_index = random.randint(0,len(truck_path) - 2)
    #node2_switch_truck_index = node1_switch_truck_index + 1
    #for i in range(1, 15):
    #    node3_switch_truck_index = random.randint(0,len(truck_path) - 2)
    #    if node1_switch_truck_index > node3_switch_truck_index:
    #        node1_switch_truck_index = node3_switch_truck_index
    #        node2_switch_truck_index = node1_switch_truck_index + 1
    #        continue
    #    if node3_switch_truck_index != node2_switch_truck_index and node3_switch_truck_index != node1_switch_truck_index:
    #        node4_switch_truck_index = node3_switch_truck_index + 1
    #        if node4_switch_truck_index != node1_switch_truck_index:
    #            break
    #        else:
    #            continue
    
    #node1_switch_truck_index = 2
    #node2_switch_truck_index = 3
    #node3_switch_truck_index = 7
    #node4_switch_truck_index = 8
    print("La ricerca locale 2-opt ha trovato la soluzione: ", solution, "\ncon costo: ", cost_truck_best)
    
    for path in solution:
        if path == solution[0]:
            print("Dove il truck percorre la seguente route --> ", path, "\n")
        elif path == solution[1]:
            print("Mentre il drone percorre le seguenti routes:\n", path)
        else: 
            print(path)
    #print("L'insieme di tutte le soluzioni migliorative trovate è: ", population)


    #Scrivo sul file GA_input.txt la popolazione che dovrà andare in pasto all'algoritmo genetico. 
    #prima però rimuovo i nodi del truck doppi
    population.append(solution)
    for solution in population:
        while solution[0][-1]==solution[0][0]:
            solution[0].pop(-1)
    with open('GA_input.txt', 'w') as GA_input:
        GA_input.writelines(str(starting_node)+"\n")
        GA_input.writelines(str(drone_autonomy)+"\n")
        GA_input.writelines(str(drone_capacity)+"\n")
        json.dump(population, GA_input)
    print("messo da fogli COSTO= ",compute_solution_cost_by_sol(solution))
    print_graph_for_debug(solution)
