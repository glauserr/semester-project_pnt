#!/bin/python3

from filefunctions import readfile as readtxsdata
from graphfunctions import getroutetables

def getcapital(V, E, txfile):
    # [[<left node>, <right node>, <Cl>, <Cr>, <max Cl>, <max Cr>], [], ..]
    channels = [[e[0], e[1], 0, 0, 0, 0] for e in E]
    nodes = V

    routetables = getroutetables(nodes, channels)

    txs = readtxsdata(txfile)
    ntxs = processtxs(routetables, channels, txs[2:])

    C = 0
    for nl, nr, Cl, Cr, maxCl, maxCr in channels:
        C += maxCl + maxCr

    return C

def getcapitalontxs(V, E, txs):
    channels = [[e[0], e[1], 0, 0, 0, 0] for e in E]
    nodes = V

    routetables = getroutetables(nodes, channels)
    ntxs = processtxs(routetables, channels, txs)

    C = 0
    for nl, nr, Cl, Cr, maxCl, maxCr in channels:
        C += maxCl + maxCr

    return C

def processtxs(routetables, channels, txs):
    def updatecapital(leftnode, rightnode, amount):
        channel = [c for c in channels if c[0] == leftnode and c[1] == rightnode]
        if len(channel) == 1:
            channel = channel[0]
            # [[<left node>, <right node>, <Cl>, <Cr>, <max Cl>, <max Cr>], [], ..]
            channel[2] += amount
            channel[3] -= amount

            if channel[2] > channel[4]:
                channel[4] = channel[2]

            if channel[3] > channel[5]:
                channel[5] = channel[3]

        else:
            print("Fatal error: channel missing")
            print("channel: {}-{}".format(leftnode, rightnode))
            print("channel variable: {}".format(channel))
            print("exit")
            exit()

    def route(node, dest, amount):
        if node == dest:
            return 0
        rt = routetables[node]
        try:
            i = [r[0] for r in rt].index(dest)
        except ValueError:
            print("Fatal error: lookup error. node: {}, dest: {}, amount: {}".format(
                node, dest, amount))
            print("exit")
            exit()

        nextnode = rt[i][1]

        if nextnode < node:
            updatecapital(nextnode, node, -amount)
        else:
            updatecapital(node, nextnode, amount)

        return route(nextnode, dest, amount)

    ntxs = 0
    for si, ri, ai in txs:
        route(int(si), int(ri), int(ai))
        ntxs += 1

    return ntxs




