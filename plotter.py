#!/bin/python3

import matplotlib.pyplot as plt
import networkx as nx
import random


def plotgraph(edges, nodes, savefilename=None):
    G_1 = nx.Graph()
    G_1.add_edges_from(edges)
    m = 5 * max(nodes)
    print(m)
    pos = {i:(random.randint(0,m),
              random.randint(0,2*m)) for i in nodes}

    import warnings
    import matplotlib.cbook
    warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
    
    plt.figure()
    nx.draw_networkx(G_1, pos, edge_labels=True)
    
    if savefilename != None:
        plt.savefig(savefilename)
    else:
        plt.show()
