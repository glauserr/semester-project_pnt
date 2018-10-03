#!/bin/python3

import math

# import matplotlib.pyplot as plt
# import numpy as np

from network import Network
from genrandomtxs import readfile as readtxsdata
from genrandomtxs import writefile
from genrandomtxs import readfile


class Executor(Network):
    N_NODES = 30
    # add rout table to network:
    # {n1: {channels: [{n2:dkkd, id:2943}],
    #       routetable: [{dest:dkjf, sendto:kdjlf}]}

    def __init__(self, simulate=True, nnodes=None):
        self.simulate = simulate
        # [[src, target, capital, max capital, open channels], [], ..]
        self.channels = list()
        # [n1, n4, etc]
        self.passednodes = list()
        self.nodes = []
        self.network = {}

        if nnodes!= None:
            self.N_NODES = nnodes

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
        self.executetxs(txs[2:])
        # print(txs)

        # for src, dest, amount in txs[2:]:
        #     src = "n{}".format(src)
        #     dest = "n{}".format(dest)
        #     # TODO: write to file
        #     # print("From {} to dest: {}".format(src, dest))
        #     # print(src, end="")
        #     self.calccapital(src, dest, amount)
        #     self.ntxs += 1

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

    def executetxs(self, txs):
        self.ntxs = 0
        # avg = 0
        for src, dest, amount in txs:
            src = "n{}".format(src)
            dest = "n{}".format(dest)
            # TODO: write to file
            # print("From {} to dest: {}".format(src, dest))
            # print(src, end="")
            # avg += int(amount)
            self.calccapital(src, dest, amount)
            self.ntxs += 1

        # print(avg/self.ntxs)        

    def calccapital(self, node, dest, amount):
        if node == dest:
            # TODO: write to file
            # print("")
            return 0
        routetable = self.network[node]['routetable']
        sendto = next(
            (item["sendto"] for item in routetable if item["dest"] == dest), None)

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

        # print(self.network)
        # exit()

    def getneighbors(self, node):
        return [channel[1] for channel in self.channels if channel[0] == node]

    def forward(self, sender, receiver, sourcenode, hops):
        if sourcenode == receiver:
            return 0

        routetable = self.network[receiver]['routetable']
        olditem = next((item for item in routetable if item['dest']
                        == sourcenode), None)
        
        if olditem == None:
            routetable.append(
                {'dest': sourcenode, 'sendto': sender, 'hops': hops})
        elif olditem['hops'] > hops:              
            routetable.remove(olditem)
            routetable.append(
                {'dest': sourcenode, 'sendto': sender, 'hops': hops})
        else:
            return 0
        hops += 1

        forwardto = self.getneighbors(receiver)
        forwardto.remove(sender)
        for neighbor in forwardto:
            self.forward(receiver, neighbor, sourcenode, hops)


