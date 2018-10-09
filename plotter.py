#!/bin/python3

import matplotlib.pyplot as plt
import networkx as nx
import random


def plotgraph(edges, nodes, savefilename=None):
    G_1 = nx.Graph()
    G_1.add_edges_from(edges)
    pos = {i:(random.randint(0,50),
              random.randint(0,100)) for i in nodes}

    import warnings
    import matplotlib.cbook
    warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
    
    plt.figure()
    nx.draw_networkx(G_1, pos, edge_labels=True)
    
    if savefilename != None:
        plt.savefig(savefilename)
    else:
        plt.show()
