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

                if True: #Ct <= ai:
                    for t in tablemap:
                        t[0] = t[1]
                else: # Connect -> generates cycles
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

        # self.createtopologyplot("dynamicTree.png", show=True)

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


class EdgeReductionAlg(Executor, Plotter):
    def __init__(self, simulate=False):
        super().__init__(simulate)
        # self.create()

    def executetxs(self, txs):
        self.edgestates = {}
        self.ntxs = 0

        for i,node in enumerate(self.nodes,0):
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

            edge = "n{}-n{}".format(si,ri)

            try:
                #[[index, s, r, a,],[],..]
                states = self.edgestates[edge]['states']
            except KeyError:
                self.edgestates[edge] = {'states':[], 'maxcapital': [0,0],
                    'maxTx': [0,0]}
                states = self.edgestates[edge]['states']
                states.append([-1, 0, 0, 0, 0])

            last = len(states) - 1
            state1 = states[last][1] - ai
            state2 = states[last][2] + ai
            state = [self.ntxs, state1, state2, ai]
            states.append(state) 

            maxcap = self.edgestates[edge]['maxcapital']
            maxtx = self.edgestates[edge]['maxTx']
            if state1 < maxcap[0]:
                maxcap[0] = state1
                maxtx[0] = ai                

            if state2 < maxcap[1]:
                maxcap[1] = state2
                maxtx[1] = ai                

            self.ntxs += 1

        error = 0
        for key in self.edgestates:
            edge = self.edgestates[key]

            maxtx = max(edge['maxTx'])
            maxcap = sum(edge['maxcapital'])

            if maxtx < maxcap:
                error += maxcap - maxtx

        print("error: {}, per tx: {}".format(error, error/self.ntxs))
        print("exit")
        exit()


if __name__ == "__main__":

    costs = 1
    fees = 1
    tnxfile = "randomtxs1000.data"

    plt.clf()
    plt.xlabel("Needed capital / transactions")
    plt.ylabel("Profit / transactions")
    plt.axis([180, 500, 0.92, 1])
    plt.grid(True)


    def output(msg, capital, channels, txs):
        profit = (txs * fees - channels * costs) / txs
        capital = capital / txs
        print("[{}]: profit per Txs: {}, capital per Txs: {}, (channels: {}, txs: {})".format(
            msg, profit, capital, channels, txs))
        return profit

    def scatter(capital, channels, txs, name, namepos, c='b'):
        profit = (txs * fees - channels * costs) / txs
        capital = capital / txs
        x,y = namepos
        plt.scatter(capital, profit, c=c, zorder=1000)
        plt.annotate(name, (capital+x,profit+y), zorder=1001)
    
    # topology = DynamicTree()
    # cap, chan, txs = topology.run(tnxfile)
    # scatter(cap, chan, txs, "maxTx", (1, 0.01))
    # output("offline", cap, chan, txs)

    # plt.show()

    topology = EdgeReductionAlg()
    cap, chan, txs = topology.run("3node.data")
