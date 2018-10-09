#!/bin/python3

import os, sys, re
import math
from time import sleep
from random import SystemRandom
import matplotlib.pyplot as plt
import numpy as np

from filefunctions import writefile
from filefunctions import readfile

from executor import Executor
import plotter


class Star(Executor):

    def __init__(self, simulate=True, nnodes=None):
        print("creating star topology...")
        self.simulate = simulate
        self.nnodes = nnodes
        self.superinit()
        self.create(self.nodes[0])

    def superinit(self):
        super().__init__(simulate=self.simulate, nnodes=self.nnodes)

    def create(self, hub):
        hub = hub

        self.network[hub]['routetable'] = []

        for node in self.nodes:
            if node == hub:
                continue
            # sender, receiver, capital, maxcapital, open channels
            self.channels.append([hub, node, 0, 0, 0])
            # sender, receiver, capital, maxcapital, open channels
            self.channels.append([node, hub, 0, 0, 0])

        self.createroutetable()

    def runall(self, filename):
        retval = []
        for node in self.nodes:
            self.superinit()
            self.create(node)
            cap, ch, txs = self.run(filename)
            retval.append([node, cap, ch, txs])

        return retval

class BinaryTree(Executor):

    def __init__(self, simulate=True):
        print("creating binary tree topology...")
        super().__init__(simulate)
        self.create()

    def create(self):
        for i in range(len(self.nodes)):
            if i == 0:
                continue
            indexparent = int((i-1)/2)
            # [sender, receiver, capital, maxcapital, open channels]
            self.channels.append(
                [self.nodes[indexparent], self.nodes[i], 0, 0, 0])
            self.channels.append(
                [self.nodes[i], self.nodes[indexparent], 0, 0, 0])

        self.createroutetable()


class Ring(Executor):

    def __init__(self, simulate=True):
        print("creating ring topology...")
        super().__init__(simulate)
        self.create()

    def create(self):
        for i in range(len(self.nodes)):
            childindex = (i + 1) % len(self.nodes)
            # sender, receiver, capital, maxcapital, open channels
            self.channels.append([self.nodes[i], self.nodes[childindex], 0, 0, 0])
            self.channels.append([self.nodes[childindex], self.nodes[i], 0, 0, 0])

        self.createroutetable()


class RandomSpanningTree(Executor):

    def __init__(self, simulate=True):
        print("creating random spanning tree topology...")
        super().__init__(simulate)

    def recreate(self):
        super().__init__(False)
        self.create()

    def create(self):
        sptset = []  # spanning tree set
        nodeset = self.nodes.copy()

        _sysrand = SystemRandom()

        while len(nodeset) > 0:
            indexnodeset = _sysrand.randint(0, len(nodeset) - 1)
            chosennode = nodeset[indexnodeset]

            if len(sptset) > 0:
                indexsptset = _sysrand.randint(0, len(sptset) - 1)
                chosennodespt = sptset[indexsptset]
                # sender, receiver, capital, maxcapital, open channels
                self.channels.append([chosennodespt, chosennode, 0, 0, 0])
                self.channels.append([chosennode, chosennodespt, 0, 0, 0])

            nodeset.remove(chosennode)
            sptset.append(chosennode)

        self.createroutetable()

    def load(self, filename):
        file = readfile(filename)
        header = file[0]
        self.channels = file[1:]
        for c in self.channels:
            c[2] = int(c[2])
            c[3] = int(c[3])
        return header

    def save(self, filename, header):
        header = [header]
        for c in self.channels:
            header.append(c)
        writefile(filename, header)


class FullMesh(Executor):
    def __init__(self, simulate=True):
        print("creating full-mesh topology...")
        super().__init__(simulate)
        self.create()

    def create(self):
        for src in self.nodes:
            self.network[src]['routetable'] = []
            for target in self.nodes:
                if src != target:
                    # sender, receiver, capital, maxcapital, open channels
                    self.channels.append([src, target, 0, 0, 0])

        self.createroutetable()

    def createroutetable(self):

        for node in self.nodes:
            self.network[node]['routetable'] = []

        for node in self.nodes:
            neighbors = self.getneighbors(node)
            for n in neighbors:
                self.network[node]['routetable'].append(
                    {'dest': n, 'sendto': n})


# if __name__ == "__main__":
#     tnxfile = "randomtxs1.data"
    
#     topology = FullMesh(simulate=False)
#     (capON, chanON, txs) = topology.run(tnxfile, online=False)
#     output(capON, capON/txs, chanON, txs)
    # topology.selfchannel()
    # topology.createtopologyplot("test.png", show=True)

if __name__ == "__main__":
    TXS_DIR = "transaction_sets/"
    N_NODES = 30
    N_TXS = 1000
    SET = 1

    fees = 1 # fees for transaction
    costs = 1 # cost to set up a channel

    an = 0.0005

    tnxfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(
        N_NODES,N_TXS,SET)

    fmdrw = "topology_fullmesh.png"
    stardrw = "topology_star.png"
    binarytreedrw = "topology_binarytree.png"
    ringdrw = "topology_ring.png"
    randomsptdrw = "topology_randomspanningtree.png"
    
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


    def run(topology, name):
        (cap, chan, txs) = topology.run(tnxfile)
        output("offline", cap, chan, txs)

        (capON, chanON, txs) = topology.run(tnxfile, online=True)
        output("online", capON, chanON, txs)

        scatter(cap, chan, txs, name, (an, an))
        # scatter(capON, chanON, txs, name, (an, an), c='g')


    plt.clf()
    plt.xlabel("Needed capital / transactions")
    plt.ylabel("Profit / transactions")
    # plt.axis([0, 2.5 * fees, 0, 4200])
    plt.grid(True)

    CMD = sys.argv[1]
    if CMD == "triangle":
        topology = Star(simulate=False, nnodes=3)
        allvariants = topology.runall("3node.data")

        # profit is everywhere equal -> look for min capital
        bestnode, cap, ch, txs = min(allvariants, key=lambda x: x[1])
        print("bestnode: {}, cap: {}, channel: {}, txs: {}".format(bestnode, cap, ch, txs))

        for v in allvariants:
            node, cap, ch, txs = v
            print("node: {}, cap: {}, channel: {}, txs: {}".format(node, cap, ch, txs))
            if node != bestnode:
                node = ""
            scatter(cap, ch, txs, node, (an, an))



    elif CMD == "star":
        topology = Star(simulate=False)
        allvariants = topology.runall(tnxfile)

        # profit is everywhere equal -> look for min capital
        bestnode, cap, ch, txs = min(allvariants, key=lambda x: x[1])
        print("node: {}, cap: {}, channel: {}, txs: {}".format(bestnode, cap, ch, txs))

        for v in allvariants:
            node, cap, ch, txs = v
            if node != bestnode:
                node = ""
            scatter(cap, ch, txs, node, (an, an))

        plt.title("Best star")

    elif CMD == "randomtree":
        bestrandomtree = "bestrandomtree.data"
        topology = RandomSpanningTree(simulate=False)

        bestcapital = sys.maxsize

        exists = os.path.isfile(bestrandomtree)
        if exists:
            header = topology.load(bestrandomtree)
            bestcapital = float(header[0])
            print("Minimum needed capital: {}".format(bestcapital))


        i = 10
        while i > 0:
            topology.recreate()
            cap, ch, txs = topology.run(tnxfile)
            scatter(cap, ch, txs, "", (an, an))
            i -= 1
            if i % 100 == 0:
                print(i)
            if cap <  bestcapital:
                bestcapital = cap
                topology.save(bestrandomtree, [bestcapital])
                print("Minimum needed capital: {}".format(bestcapital))

    elif CMD == "all":

        fullmesh = FullMesh(simulate=False)
        (fmcap, fmchan,optimaltxs) = fullmesh.run(tnxfile, online=False)
        optimalcap = fmcap / optimaltxs

        topology = Star(simulate=False)
        run(topology, "star")

        topology = BinaryTree(simulate=False)
        run(topology, "binarytree")

        topology = Ring(simulate=False)
        run(topology, "ring")

        # search for a better random spanning tree
        randomspt = RandomSpanningTree(simulate=False)

        randomsptdata = "spanningtree.data"
        exists = os.path.isfile(randomsptdata)
        if exists:
            header = randomspt.load(randomsptdata)
            bestcapital = float(header[0])
            bestcapitalprofit = float(header[1])
            bestcapitalchan = float(header[2])
            bestcapitaltxs = float(header[3])
            bestcapitalON = float(header[4])
            bestcapitalprofitON = float(header[5])
            bestcapitalchanON = float(header[6])
            bestcapitaltxsON = float(header[7])
        else:
            bestcapital = sys.maxsize
            bestcapitalON = sys.maxsize

        for i in range(50):
            randomspt.recreate()
            (rstcap, rstchan, txs) = randomspt.run(tnxfile)

            rstchanON = rstchan
            if rstcap/txs < bestcapital:
                bestcapital = rstcap / txs
                bestcapitalprofit = (txs * fees - rstchan * costs) / txs
                bestcapitalchan = rstchan
                bestcapitaltxs = txs
                (rstcapON, rstchanON, txsON) = randomspt.run(tnxfile, online=True)
                bestcapitalON = rstcapON / txsON
                bestcapitalprofitON = (txsON * fees - rstchanON * costs) / txsON
                bestcapitalchanON = rstchanON
                bestcapitaltxsON = txsON
                randomspt.save(randomsptdata, [bestcapital, bestcapitalprofit, bestcapitalchan, bestcapitaltxs,
                    bestcapitalON, bestcapitalprofitON, bestcapitalchanON, bestcapitaltxsON])
                # randomspt.createtopologyplot(randomsptdrw)

        p = output("offline", bestcapital, bestcapitalchan*bestcapitaltxs, bestcapitaltxs)
        pON = output("online", bestcapitalON, bestcapitalchanON*bestcapitaltxsON, bestcapitaltxsON)
        plt.scatter(bestcapital, bestcapitalprofit, c='b', zorder=1000)
        # plt.scatter(bestcapitalON, bestcapitalprofitON, c='g', zorder=1000)
        plt.annotate("randomspt", (bestcapital+an, bestcapitalprofit+an), zorder=1001)
        # plt.annotate("randomspt", (bestcapitalON+an, bestcapitalprofitON+an) , zorder=1001)

        # print("Optimal level: {}, transactions: {}".format(optimalcap, optimaltxs))
        # plt.plot(np.linspace(0, 100, num=20), [optimalcap] * 20, c='r', zorder=1000)
        # plt.annotate("optimal", (0, optimalcap), color='r', zorder=1001)
        plt.title("Topology comparison")
    else:
        print("Not found: {}".format(CMD))
        exit()

    plt.show()
