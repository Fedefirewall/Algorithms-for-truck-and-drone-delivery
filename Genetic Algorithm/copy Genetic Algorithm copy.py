#region
#IMPORTAZIONE LIBRERIE
from os import PathLike, error
from random import randint, seed
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
# mpl = multiprocessing.log_to_stderr()
# mpl.setLevel(logging.INFO)
def GA(test):
    r=random.random()
    test.append(r)
    print(test)
    return test
if __name__ == "__main__": 
    test=[1,2,3,4]
    populations_repeated=[test for i in range(3)]
    with Pool() as pool:
        parallel_output=pool.map(GA,populations_repeated)
    print(parallel_output)