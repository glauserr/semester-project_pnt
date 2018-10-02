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

                if Ct <= ai:
                    for t in tablemap:
                        t[0] = t[1]
                else:
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


if __name__ == "__main__":

    fees = 1
    tnxfile = "randomtxs1000.data"

    def output(msg, tcapital, numberofchannels, txs):
        print("[{}]: capital/txs: {} (channels: {}, txs: {})".format(
            msg, tcapital/txs, numberofchannels, txs))

    topology = DynamicTree()
    (cap, chan, txs) = topology.run(tnxfile)
    output("offline", cap, chan, txs)
