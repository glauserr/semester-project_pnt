#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random

class Plotter():

    def createtopologyplot(self, plotname, show=False):
        plt.clf()
        self.passednodes = []
        self.edges = []
        x,y = (-1, 1)
        for i, n in enumerate(self.nodes, 0):
            xline = np.linspace(i, i, num=20)
            yline = np.linspace(1, 3 * len(self.nodes), num=20)
            plt.plot(xline, yline, c='grey')

            xr,yr = self.plotforwardnode(n, (x,y), n, 0, init=True)
            if (xr,yr) != (x,y): 
                x, y = xr, yr + 2
                xline = np.linspace(0, len(self.nodes), num=20)
                yline = np.linspace(y, y, num=20)
                plt.plot(xline, yline, c='grey')
            else:   
                x, y = xr, yr
        if show:
            plt.show()
        else:
            plt.savefig(plotname)

    def plotforwardnode(self, sender, coordinates, receiver, count, init=False):
        # in case node already used
        if init == True and receiver in self.passednodes:
            return coordinates

        edge1 = "{}-{}".format(sender, receiver)
        edge2 = "{}-{}".format(receiver, sender)

        if edge1 in self.edges or edge2 in self.edges:
            return coordinates
        
        self.passednodes.append(receiver)
        self.edges.append(edge1)
        self.edges.append(edge2)

        senderpos = self.nodes.index(sender)
        receiverpos = self.nodes.index(receiver)
        
        x, y = coordinates
        x, y = (receiverpos, y + 1)

        if senderpos < receiverpos:
            xline = np.linspace(senderpos, receiverpos, num=20)
        else: 
            xline = np.linspace(receiverpos, senderpos, num=20)

        yline = np.linspace(y, y, num=20)
        plt.plot(xline, yline, c='g')
        plt.scatter(senderpos, y, c='brown', zorder=1000)
        plt.scatter(x, y, c='b', zorder=1000)
        plt.annotate(receiver, (x+0.1, y+0.1))
        plt.axis('equal')

        neighbors = self.getneighbors(receiver)

        if sender in neighbors:  # sender != receiver
            neighbors.remove(sender)

        count += 1
        for i, n in enumerate(neighbors, 1):
            (x, y) = self.plotforwardnode(receiver, (x, y), n, count)

        return (x, y)


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
