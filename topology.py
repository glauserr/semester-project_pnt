#!/bin/python3

import os, sys, re
import math
from time import sleep
from random import SystemRandom
import matplotlib.pyplot as plt
import numpy as np

from network import Network
from genrandomtxs import readfile as readtxsdata
from genrandomtxs import writefile
from genrandomtxs import readfile


class Executor(Network):
    N_NODES = 30
    fees = 100  # 100 satoshi
    # add rout table to network:
    # {n1: {channels: [{n2:dkkd, id:2943}],
    #       routetable: [{dest:dkjf, sendto:kdjlf}]}

    def __init__(self, simulate=True):
        self.simulate = simulate
        # [[src, target, capital, max capital, open channels], [], ..]
        self.channels = list()
        # [n1, n4, etc]
        self.passednodes = list()

        self.nodes = []
        self.network = {}
        if self.simulate:
            super().__init__(self.N_NODES)
        else:
            for n in range(self.N_NODES):
                name = "n{}".format(n)
                self.nodes.append(name)
                self.network[name] = {'channels': []}

    def run(self, filename, online=False):
        self.online = online 
        if not self.online:
            for chan in self.channels:
                chan[4] = 1
        txs = readtxsdata(filename)
        self.ntxs = 0
        # print(txs)

        for src, dest, amount in txs[2:]:
            src = "n{}".format(src)
            dest = "n{}".format(dest)
            # TODO: write to file
            # print("From {} to dest: {}".format(src, dest))
            # print(src, end="")
            self.calccapital(src, dest, amount)
            self.ntxs += 1
            if self.simulate:
                # TODO: Connect and open channels. Send txs
                # self.connectnodes([(c[0], c[1]) for c in new_channels])
                # print("opening channels to master...")
                # self.openchannels(new_channels)
                # print("send payment to nodes...")
                pass

        # calc total capital.
        tcapital = 0
        nchannels = 0
        for src, target, currentstate, capital, created in self.channels:
            tcapital += capital
            nchannels += created

        bidirectchannels = nchannels / 2

        return (tcapital, bidirectchannels, self.ntxs)

    def calccapital(self, node, dest, amount):
        if node == dest:
            # TODO: write to file
            # print("")
            return 0
        routetable = self.network[node]['routetable']
        sendto = next(
            (item["sendto"] for item in routetable if item["dest"] == 'ALL' or item["dest"] == dest), None)

        if sendto == None:
            print("Fatal error: lookup error. node: {}, dest: {}, amount: {}".format(
                node, dest, amount))
            print(self.channels)
            print("exit")
            exit()

        nodeindex = next(
            (i for i, item in enumerate(self.channels, 0) if item[0] == node and item[1] == sendto), None)
        sendtoindex = next(
            (i for i, item in enumerate(self.channels, 0) if item[0] == sendto and item[1] == node), None)

        self.updatechannels(nodeindex, sendtoindex, int(amount))
        # TODO: write to file
        # print(" -> {}".format(sendto), end="")
        return self.calccapital(sendto, dest, amount)

    def updatechannels(self, senderindex, receiverindex, amount):
        # make sure that the channel is allowed
        if senderindex != None and receiverindex != None:
            # [src, target, capital, max capital, open channels]
            senderchannel = self.channels[senderindex]
            receiverchannel = self.channels[receiverindex]

            # online:
            if self.online:
                if senderchannel[2] < int(amount):
                    # TODO: open new channel in case of simulating!
                    senderchannel[4] += 1
                    receiverchannel[4] += 1
                    senderchannel[2] += 2 * int(amount)
                    senderchannel[3] += 2 * int(amount)

            senderchannel[2] -= int(amount)
            receiverchannel[2] += int(amount)

            if not self.online:
                if senderchannel[2] < 0 and senderchannel[2] < -1 * senderchannel[3]:
                    senderchannel[3] = -1 * senderchannel[2]

        else:
            print("Fatal error: connection missing")
            print("nextnode: {}".format(sendto))
            print(self.channels)
            print("exit")
            exit()

    def createroutetable(self):

        for node in self.nodes:
            self.network[node]['routetable'] = []

        for node in self.nodes:
            neighbors = self.getneighbors(node)
            for n in neighbors:
                self.forward(node, n, node, 1)

    def getneighbors(self, node):
        return [channel[1] for channel in self.channels if channel[0] == node]

    def forward(self, sender, receiver, sourcenode, hops):
        routetable = self.network[receiver]['routetable']
        oldhops = next(
            (item['hops'] for item in routetable if item['dest']
             == sourcenode and item['sendto'] == sender),
            None)
        if oldhops == None or oldhops > hops:
            self.network[receiver]['routetable'].append(
                {'dest': sourcenode, 'sendto': sender, 'hops': hops})
        else:
            return 0
        hops += 1

        forwardto = self.getneighbors(receiver)
        forwardto.remove(sender)
        for neighbor in forwardto:
            self.forward(receiver, neighbor, sourcenode, hops)

    def createtopologyplot(self, plotname):
        coordinates = (len(self.nodes),) * 2 + (0,)
        plt.clf()
        self.plotforwardnode(self.nodes[0], coordinates, self.nodes[0], 0)
        plt.savefig(plotname)

    def plotforwardnode(self, sender, coordinates, receiver, count):
        xzero, yzero, anglesender = coordinates
        neighbors = self.getneighbors(receiver)

        if sender in neighbors:  # sender != receiver
            neighbors.remove(sender)
        else:
            self.passednodes = [receiver]
            plt.scatter(xzero, yzero)
            plt.annotate(sender, (xzero, yzero))
            plt.axis('equal')

        if len(neighbors) < 20:
            angledelta = math.pi / 10
        else:
            angledelta = 2 * math.pi / len(neighbors)
        sign = math.pow((-1), count)
        count += 1

        for i, n in enumerate(neighbors, 1):
            angle = anglesender + sign * i*angledelta

            x = xzero + math.cos(angle)
            y = yzero + math.sin(angle)
            xline = np.linspace(xzero, x, num=20)
            yline = np.linspace(yzero, y, num=20)
            plt.plot(xline, yline, c='g')
            plt.scatter(x, y, c='b', zorder=1000)
            plt.annotate(n, (x, y), zorder=1001)

            if n in self.passednodes:
                return

            self.plotforwardnode(receiver, (x, y, angle), n, count)
            self.passednodes.append(n)


class Star(Executor):

    def __init__(self, simulate=True):
        print("creating star topology...")
        super().__init__(simulate)
        self.create()

    def create(self):
        hub = self.nodes[0]

        self.network[hub]['routetable'] = []

        for i, node in enumerate(self.nodes[1:], 1):
            # sender, receiver, capital, maxcapital, open channels
            self.channels.append([hub, node, 0, 0, 0])
            # sender, receiver, capital, maxcapital, open channels
            self.channels.append([node, hub, 0, 0, 0])

            self.network[node]['routetable'] = []
            entry = {}
            entry['dest'] = "ALL"
            entry['sendto'] = hub
            self.network[node]['routetable'].append(entry)
            self.network[hub]['routetable'].append(
                {'dest': node, 'sendto': node})


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

    def calccapital(self, node, dest, amount):

        if dest == node:
            # TODO: write to file
            # print("")
            return 0

        nodeindex = self.nodes.index(node) + 1
        destindex = self.nodes.index(dest) + 1

        nextnode = None

        if destindex < nodeindex:
            # send to parent
            nextnode = int(nodeindex / 2)

        # is in subtree of current node? else send to parent
        depth = 0
        while depth < 5:
            depth += 1
            numofchildren = int(pow(2, depth))
            childlowindex = nodeindex * numofchildren
            childhighindex = childlowindex + numofchildren - 1

            if destindex < childlowindex:
                # send to parent
                nextnode = int(nodeindex / 2)
                break

            elif destindex in range(childlowindex, childlowindex + int(numofchildren/2)):
                # send to left child
                nextnode = nodeindex * 2
                break

            elif destindex in range(childlowindex + int(numofchildren/2), childhighindex + 1):
                # send to right child
                nextnode = nodeindex * 2 + 1
                break
            else:
                # repeat
                pass

        nextnode = self.nodes[int(nextnode) - 1]

        indexnode = next(
            (i for i, item in enumerate(self.channels, 0) if item[0] == node and item[1] == nextnode), None)
        indexnextnode = next(
            (i for i, item in enumerate(self.channels, 0) if item[0] == nextnode and item[1] == node), None)

        self.updatechannels(indexnode, indexnextnode, int(amount))

        # TODO: write to file
        # print(" -> {}".format(nextnode), end="")
        return self.calccapital(nextnode, dest, amount)


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

    def calccapital(self, node, dest, amount):

        if node == dest:
            # TODO: write to file
            # print("")
            return 0

        nodeindex = self.nodes.index(node)
        destindex = self.nodes.index(dest)

        if nodeindex < destindex:
            path1 = destindex - nodeindex
            path2 = nodeindex + len(self.nodes) - destindex
        else:
            path1 = destindex + len(self.nodes) - nodeindex
            path2 = nodeindex - destindex

        if path1 < path2:
            # send to left child
            nextnode = (nodeindex + 1) % len(self.nodes)
        else:
            # send to right child
            if nodeindex == 0:
                nextnode = len(self.nodes) - 1
            else:
                nextnode = (nodeindex - 1) % len(self.nodes)

        nextnode = self.nodes[int(nextnode)]

        indexnode = next(
            (i for i, item in enumerate(self.channels, 0) if item[0] == node and item[1] == nextnode), None)
        indexnextnode = next(
            (i for i, item in enumerate(self.channels, 0) if item[0] == nextnode and item[1] == node), None)

        self.updatechannels(indexnode, indexnextnode, int(amount))

        # sleep(2)
        # TODO: write to file
        # print(" -> {}".format(nextnode), end="")
        return self.calccapital(nextnode, dest, amount)


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


if __name__ == "__main__":
    # Network(3)
    fees = 1
    # tnxfile = "orderedtxs.data"
    tnxfile = "randomtxs.data"
    # header = readfile(tnxfile)[0]
    # found = re.findall('N_TXS: (.+?);', str(header))
    # if len(found) == 0:
    #     print("Error. {} could not be read".format(tnxfile))
    #     print("exit")
    #     exit()

    # numoftxs = int(found[0])

    fmdrw = "topology_fullmesh.png"
    stardrw = "topology_star.png"
    binarytreedrw = "topology_binarytree.png"
    ringdrw = "topology_ring.png"
    randomsptdrw = "topology_randomspanningtree.png"
    

    def output(msg, tcapital, tfees, numberofchannels, txs):
        print("[{}]: avg capital: {}, avg fees (open): {} (channels: {}, txs: {})".format(
            msg, tcapital, tfees, numberofchannels, txs))

    def run(topology, name):
        (cap, chan, txs) = topology.run(tnxfile)
        capptxs = cap/txs
        feestxs = chan * fees/txs
        output("offline", capptxs, feestxs, chan, txs)

        (capON, chanON, txs) = topology.run(tnxfile, online=True)
        capptxsON = capON/txs
        feestxsON = chanON * fees/txs
        output("online", capptxsON, feestxsON, chanON, txs)

        plt.scatter(feestxs, capptxs, c='b', zorder=1000)
        plt.scatter(feestxsON, capptxsON, c='g', zorder=1000)

        plt.annotate(name, (feestxs, capptxs), zorder=1001)
        plt.annotate(name, (feestxsON, capptxsON), zorder=1001)


    plt.clf()
    plt.xlabel("Fees / Transactions")
    plt.ylabel("Capital / Transactions")
    plt.axis([0, 2 * fees, 0, 4200])
    plt.grid(True)

    fullmesh = FullMesh(simulate=False)
    (fmcap, fmchan,optimaltxs) = fullmesh.run(tnxfile)
    optimalcap = fmcap / optimaltxs

    topology = Star(simulate=False)
    # topology.createtopologyplot(stardrw)
    run(topology, "star")

    topology = BinaryTree(simulate=False)
    # topology.createtopologyplot(binarytreedrw)
    run(topology, "binarytree")

    topology = Ring(simulate=False)
    # topology.createtopologyplot(ringdrw)
    run(topology, "ring")

    # search for a better random spanning tree
    randomspt = RandomSpanningTree(simulate=False)

    randomsptdata = "spanningtree.data"
    exists = os.path.isfile(randomsptdata)
    if exists:
        header = randomspt.load(randomsptdata)
        bestcapital = float(header[0])
        bestcapitalfees = float(header[1])
        bestcapitalchan = float(header[2])
        bestcapitaltxs = float(header[3])
        bestcapitalON = float(header[4])
        bestcapitalfeesON = float(header[5])
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
            bestcapital = rstcap/txs
            bestcapitalfees = rstchan * fees/txs
            bestcapitalchan = rstchan
            bestcapitaltxs = txs
            (rstcapON, rstchanON, txsON) = randomspt.run(tnxfile, online=True)
            bestcapitalON = rstcapON/txsON
            bestcapitalfeesON = rstchanON * fees/txsON
            bestcapitalchanON = rstchanON
            bestcapitaltxsON = txsON
            randomspt.save(randomsptdata, [bestcapital, bestcapitalfees, bestcapitalchan, bestcapitaltxs,
                bestcapitalON, bestcapitalfeesON, bestcapitalchanON, bestcapitaltxsON])
            # randomspt.createtopologyplot(randomsptdrw)

    output("offline", bestcapital, bestcapitalfees, bestcapitalchan, bestcapitaltxs)
    output("online", bestcapitalON, bestcapitalfeesON, bestcapitalchanON, bestcapitaltxsON)
    plt.scatter(bestcapitalfees, bestcapital, c='b', zorder=1000)
    plt.scatter(bestcapitalfeesON, bestcapitalON, c='g', zorder=1000)
    plt.annotate("randomspt", (bestcapitalfees, bestcapital), zorder=1001)
    plt.annotate("randomspt", (bestcapitalfeesON, bestcapitalON), zorder=1001)

    print("Optimal level: {}, transactions: {}".format(optimalcap, optimaltxs))
    plt.plot(np.linspace(0, 100, num=20), [optimalcap] * 20, c='r', zorder=1000)
    plt.annotate("optimal", (0, optimalcap), color='r', zorder=1001)

    plt.show()
