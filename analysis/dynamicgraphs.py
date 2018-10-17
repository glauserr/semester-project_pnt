#!/bin/python3

import sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.append('../')

from time import sleep
from time import time
from random import SystemRandom

from staticgraphs import Executor
from plotter import plotgraph


class CapitalVisualization(Executor):
    def __init__(self, simulate=False, nnodes=None):
        super().__init__(simulate,nnodes)
        # self.create()

    def executetxs(self, txs):
        self.edgestates = {}
        self.ntxs = 0

        for i, node in enumerate(self.nodes, 0):
            self.network[node]['routetable'] = []

        totaltxs = len(txs)

        for tx in txs:

            si, ri, ai = tx
            ai = int(ai)

            if ri < si:
                t = ri
                ri = si
                si = t
                ai = (-1) * ai

            edge = "n{}-n{}".format(si, ri)

            try:
                #[[index, state sender, state receiver, payment at this state,],[],..]
                states = self.edgestates[edge]['states']
            except KeyError:
                self.edgestates[edge] = {'states': [], 'maxcapital': [0, 0],
                                         'maxTx': [0, 0], 'nleft':-1,'nright':-1}
                states = self.edgestates[edge]['states']
                states.append([-1, 0, 0, 0, 0])

            self.edgestates[edge]['nleft'] = si
            self.edgestates[edge]['nright'] = ri

            last = len(states) - 1
            state1 = states[last][1] - ai
            state2 = states[last][2] + ai
            state = [self.ntxs, state1, state2, ai]
            states.append(state)

            maxcap = self.edgestates[edge]['maxcapital']
            maxtx = self.edgestates[edge]['maxTx']

            # update the maximal needed capital
            if state1 < (-1) * maxcap[0]:
                maxcap[0] = (-1) * state1

            if state2 < (-1) * maxcap[1]:
                maxcap[1] = (-1) * state2

            # maximum tx on both direction
            if ai > 0 and maxtx[0] < ai:
                maxtx[0] = ai

            elif maxtx[1] < (-1) * ai:
                maxtx[0] = (-1) * ai

            self.ntxs += 1

        derivation = 0
        capital = 0
        print(self.edgestates)

        for key in self.edgestates:
            edge = self.edgestates[key]

            maxtx = max(edge['maxTx'])
            maxcap = sum(edge['maxcapital'])

            capital += maxcap

            if maxtx < maxcap:
                derivation += maxcap - maxtx

        print("derivation. total: {}, per tx: {}".format(
            derivation, derivation/self.ntxs))
        print("Needed capital: {}".format(capital))

        self.plotcapital()


    def plotcapital(self):
        plt.clf()
        plt.title("Needed capital during execution")
        plt.xlabel("Executed transactions")
        plt.ylabel("Needed capital")

        states = [self.edgestates[edge]['states'] for edge in self.edgestates]
        captialstate = [[0, 0] for x in states]
        capital = [[] for x in states]
        for i in range(self.ntxs):
            for j, state in enumerate(states, 0):
                s = next(((x[1], x[2]) for x in state if x[0] == i), None)

                if s != None:
                    pos, s = [(pos, s)
                              for pos, s in enumerate(s, 0) if s <= 0][0]
                    captialstate[j][pos] = (-1) * s

                capital[j].append(captialstate[j].copy())

        txrange = range(self.ntxs)
        edges = [edge for edge in self.edgestates]
        nodechannelcap = [[[]] * len(self.nodes) for x in self.nodes]

        for i, cap in enumerate(capital, 0):
            # tcap = [x[0] + x[1] for x in cap]
            nleft = int(self.edgestates[edges[i]]['nleft'])
            nright = int(self.edgestates[edges[i]]['nright'])   

            # need capital for payments from left to right or in the opposite way 
            cleft = [x[0] for x in cap]
            cright = [x[1] for x in cap]

            nodechannelcap[nleft][nright] = cleft
            nodechannelcap[nright][nleft] = cright

            plt.plot(txrange, cleft, label=edges[i] + " left")
            plt.plot(txrange, cright, label=edges[i] + " right")

        plt.legend()
        plt.show()


def parse(para, opt):
    if len(sys.argv) not in range(len(para)+2, len(para+opt)+3):
        print("Pass parameters: {}, options: {}".format(para,opt))
        print("exit"), exit()

    a1 = int(sys.argv[2])
    a2 = int(sys.argv[3])
    a3 = int(sys.argv[4])
    a4 = int(sys.argv[5])

    try:
        a5 = sys.argv[6]
    except IndexError:
        a5 = 0

    return a1, a2, a3, a4, a5


if __name__ == "__main__":
    args = ["dtree"]
    if len(sys.argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "../transaction_sets/"
    RES_DIR = "../results/"
    TRE_DIR = "../trees/"

    CMD = sys.argv[1]

    if CMD == "dtree":
        TXS_DIR = "transaction_sets/"
        N_NODES = 30
        N_TXS = 1000
        SET = 1

        fees = 1 # fees for transaction
        costs = 1 # cost to set up a channel
        tnxfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(
            N_NODES,N_TXS,SET)

        def output(msg, capital, channels, txs):
            profit = (txs * fees - channels * costs) / txs
            capital = capital / txs
            print("[{}]: profit per Txs: {}, capital per Txs: {}, (channels: {}, txs: {})".format(
                msg, profit, capital, channels, txs))
            return profit

        def scatter(capital, channels, txs, name, namepos, c='b'):
            profit = (txs * fees - channels * costs) / txs
            capital = capital / txs
            x, y = namepos
            plt.scatter(capital, profit, c=c, zorder=1000)
            plt.annotate(name, (capital+x, profit+y), zorder=1001)

        topology = DynamicTree()
        cap, chan, txs = topology.run(tnxfile)

        plt.clf()
        plt.xlabel("Needed capital / transactions")
        plt.ylabel("Profit / transactions")
        plt.axis([180, 500, 0.92, 1])
        plt.grid(True)

        scatter(cap, chan, txs, "max payment based", (1, 0.01))
        output("offline", cap, chan, txs)
        plt.title("Max payment based topology design")
        plt.show()

        # topology = CapitalVisualization(nnodes=3)
        # cap, chan, txs = topology.run("3node.data")
    
    # elif CMD == "rtree":
    #     para = ["<number of nodes>", "<number of transactions>",
    #             "<starting set>", "<ending set>"]
    #     opt = ["<iterations>"]

    #     nnodes,ntxs,setstart,setend,it = parse(para, opt)

    #     specadd = ""
    #     it = int(it)
    #         # rmd = re.findall(r'\d+', rmd)
    #         # rmd = [int(x) for x in rmd]   
    #         # specadd = "_rmd{}".format(rmd)
    #         # nodes = [n for n in range(nnodes) if n not in rmd]
    #         # mapping = getmapping(nodes)

    #     nodes = range(nnodes)
    #     rtree = TreeReduction(nnodes)

    #     for s in range(setstart, setend+1):
    #         print("## SET {}".format(s))
    #         spec = "{}n_{}txs_set{}".format(nnodes,ntxs,s)
    #         spec += specadd

    #         nnodes = nnodes
    #         tnxfile = TXS_DIR + "randomtxs_"+ spec +".data"
    #         # treedata = TRE_DIR + "trees_{}n.data".format(nnodes)
    #         # resultdata = RES_DIR + "result_"+ spec +".data"
    #         # resultgraph = RES_DIR + "result_"+ spec +"_graph_{}.png"


    #         V, E, C = rtree.getoptimalgraph(tnxfile, it)

    #         print("Optimal capital: {}".format(C))
    #         # plotter.plotgraph([[e[0],e[1]] for e in optE], optV)
    #         # plt.figure()


    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))