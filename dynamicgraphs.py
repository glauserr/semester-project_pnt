#!/bin/python3

import matplotlib.pyplot as plt
import numpy as np

from time import sleep

from staticgraphs import Executor
from plotter import Plotter


class DynamicTree(Executor, Plotter):
    # { 'node left-node right': {node1: [], node1: []},  ... }
    statetables = []

    def __init__(self, simulate=False):
        print("creating dynamic tree topology...")
        super().__init__(simulate)
        # self.create()

    def executetxs(self, txs):
        self.statetables = {}
        self.ntxs = 0

        for node in self.nodes:
            self.network[node]['routetable'] = []

        totaltxs = len(txs)

        while len(txs) > 0:
            self.ntxs += 1
            # print(len(txs))

            maxtxs = max(txs, key=lambda x: x[2])
            si, ri, ai = maxtxs
            si = "n{}".format(si)
            ri = "n{}".format(ri)
            ai = int(ai)
            position = txs.index(maxtxs)
            txs.remove(maxtxs)

            routetable = self.network[si]['routetable']

            hi = next(
                (item["sendto"] for item in routetable if item["dest"] == ri), None)

            # print(hi)
            if hi == None:
                # sender, receiver, capital, maxcapital, open channels
                self.channels.append([si, ri, 0, 0, 0])
                self.channels.append([ri, si, 0, 0, 0])

                name = "{}-{}".format(si, ri)
                self.statetables[name] = {si: [0]*totaltxs, ri: [0]*totaltxs}
                table = self.gettable(si, ri)
                self.updatetable(table, position, (si, ri, ai))
                self.createroutetable()
            else:
                ci = si
                Ct = 0
                tablemap = list()
                while ci != ri:
                    routetable = self.network[ci]['routetable']
                    hi = next(
                        (item["sendto"] for item in routetable if item["dest"] == ri), None)
                    table = self.gettable(ci, hi)
                    temptable = table.copy()
                    tablemap.append([table, temptable])

                    Cn = self.getneededcapital(temptable)
                    self.updatetable(temptable, position, (ci, hi, ai))
                    Cntmp = self.getneededcapital(temptable)

                    Ct += Cntmp - Cn
                    ci = hi

                if True:  # Ct <= ai:
                    for t in tablemap:
                        t[0] = t[1]
                else:  # Connect -> generates cycles
                    # print("update")
                    # sender, receiver, capital, maxcapital, open channels
                    self.channels.append([si, ri, 0, 0, 0])
                    self.channels.append([ri, si, 0, 0, 0])

                    name = "{}-{}".format(si, ri)
                    self.statetables[name] = {
                        si: [0]*totaltxs, ri: [0]*totaltxs}
                    table = self.gettable(si, ri)
                    # print("updatetable")
                    self.updatetable(table, position, (si, ri, ai))
                    # print("createroutetables")
                    self.createroutetable()
                    # print("update done")

        for key in self.statetables:
            table = self.statetables[key]
            nodes = [node for node in table]

            index1 = next(
                (i for i, x in enumerate(self.channels) if x[0] == nodes[0] and x[1] == nodes[1]), None)
            index2 = next(
                (i for i, x in enumerate(self.channels) if x[1] == nodes[0] and x[0] == nodes[1]), None)

            self.channels[index1][3] = (-1) * \
                min(table[nodes[0]], key=lambda x: x)
            self.channels[index2][3] = (-1) * \
                min(table[nodes[1]], key=lambda x: x)

            self.channels[index1][4] = 1
            self.channels[index2][4] = 1

        self.createtopologyplot("dynamicTree.png", show=False)

    def getneededcapital(self, table):
        C1 = 0
        C2 = 0

        nodes = [node for node in table]
        list1 = table[nodes[0]]
        list2 = table[nodes[1]]

        C1 = min(list1, key=lambda x: x)
        C2 = min(list2, key=lambda x: x)

        return (-1) * (C1 + C2)

    def gettable(self, node1, node2):
        name = "{}-{}".format(node1, node2)
        st = self.statetables
        table = next(
            (st[e] for e in self.statetables if e == name), None)
        if table == None:
            name = "{}-{}".format(node2, node1)
            table = next(
                (st[e] for e in self.statetables if e == name), None)

        return table

    def updatetable(self, table, position, transaction):
        si, ri, ai = transaction

        if table == None:
            print("Fatal Error. Table does not exists")
            print("exit")
            exit()

        for i in range(position, len(table[si])):
            table[si][i] -= ai
            table[ri][i] += ai


class CapitalVisualization(Executor, Plotter):
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


if __name__ == "__main__":

    costs = 1
    fees = 1
    tnxfile = "randomtxs1000.data"


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
