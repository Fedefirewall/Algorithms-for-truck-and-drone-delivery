    #region
#IMPORTAZIONE LIBRERIE
from random import seed
import re                                    #Libreria per leggere i file dati in input
import networkx as nx                        #Libreria per costruire grafo
from matplotlib import pyplot as plt
import math
from networkx.classes.function import neighbors
from networkx.drawing.layout import rescale_layout 
import numpy as np     
from typing import Any, List
import time
import json
from multiprocessing import Pool
from itertools import repeat
#creo probabilita


print(time.time()-start)