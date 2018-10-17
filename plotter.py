#!/bin/python3

import matplotlib.pyplot as plt
import networkx as nx
import random


def plotgraph(edges, nodes, savefilename=None):
    G_1 = nx.Graph()
    G_1.add_edges_from(edges)
    m = 5 * max(nodes)
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


# class CapitalVisualization(Executor):
#     def __init__(self, simulate=False, nnodes=None):
#         super().__init__(simulate,nnodes)
#         # self.create()

#     def executetxs(self, txs):
#         self.edgestates = {}
#         self.ntxs = 0

#         for i, node in enumerate(self.nodes, 0):
#             self.network[node]['routetable'] = []

#         totaltxs = len(txs)

#         for tx in txs:

#             si, ri, ai = tx
#             ai = int(ai)

#             if ri < si:
#                 t = ri
#                 ri = si
#                 si = t
#                 ai = (-1) * ai

#             edge = "n{}-n{}".format(si, ri)

#             try:
#                 #[[index, state sender, state receiver, payment at this state,],[],..]
#                 states = self.edgestates[edge]['states']
#             except KeyError:
#                 self.edgestates[edge] = {'states': [], 'maxcapital': [0, 0],
#                                          'maxTx': [0, 0], 'nleft':-1,'nright':-1}
#                 states = self.edgestates[edge]['states']
#                 states.append([-1, 0, 0, 0, 0])

#             self.edgestates[edge]['nleft'] = si
#             self.edgestates[edge]['nright'] = ri

#             last = len(states) - 1
#             state1 = states[last][1] - ai
#             state2 = states[last][2] + ai
#             state = [self.ntxs, state1, state2, ai]
#             states.append(state)

#             maxcap = self.edgestates[edge]['maxcapital']
#             maxtx = self.edgestates[edge]['maxTx']

#             # update the maximal needed capital
#             if state1 < (-1) * maxcap[0]:
#                 maxcap[0] = (-1) * state1

#             if state2 < (-1) * maxcap[1]:
#                 maxcap[1] = (-1) * state2

#             # maximum tx on both direction
#             if ai > 0 and maxtx[0] < ai:
#                 maxtx[0] = ai

#             elif maxtx[1] < (-1) * ai:
#                 maxtx[0] = (-1) * ai

#             self.ntxs += 1

#         derivation = 0
#         capital = 0
#         print(self.edgestates)

#         for key in self.edgestates:
#             edge = self.edgestates[key]

#             maxtx = max(edge['maxTx'])
#             maxcap = sum(edge['maxcapital'])

#             capital += maxcap

#             if maxtx < maxcap:
#                 derivation += maxcap - maxtx

#         print("derivation. total: {}, per tx: {}".format(
#             derivation, derivation/self.ntxs))
#         print("Needed capital: {}".format(capital))

#         self.plotcapital()


#     def plotcapital(self):
#         plt.clf()
#         plt.title("Needed capital during execution")
#         plt.xlabel("Executed transactions")
#         plt.ylabel("Needed capital")

#         states = [self.edgestates[edge]['states'] for edge in self.edgestates]
#         captialstate = [[0, 0] for x in states]
#         capital = [[] for x in states]
#         for i in range(self.ntxs):
#             for j, state in enumerate(states, 0):
#                 s = next(((x[1], x[2]) for x in state if x[0] == i), None)

#                 if s != None:
#                     pos, s = [(pos, s)
#                               for pos, s in enumerate(s, 0) if s <= 0][0]
#                     captialstate[j][pos] = (-1) * s

#                 capital[j].append(captialstate[j].copy())

#         txrange = range(self.ntxs)
#         edges = [edge for edge in self.edgestates]
#         nodechannelcap = [[[]] * len(self.nodes) for x in self.nodes]

#         for i, cap in enumerate(capital, 0):
#             # tcap = [x[0] + x[1] for x in cap]
#             nleft = int(self.edgestates[edges[i]]['nleft'])
#             nright = int(self.edgestates[edges[i]]['nright'])   

#             # need capital for payments from left to right or in the opposite way 
#             cleft = [x[0] for x in cap]
#             cright = [x[1] for x in cap]

#             nodechannelcap[nleft][nright] = cleft
#             nodechannelcap[nright][nleft] = cright

#             plt.plot(txrange, cleft, label=edges[i] + " left")
#             plt.plot(txrange, cright, label=edges[i] + " right")

#         plt.legend()
#         plt.show()    