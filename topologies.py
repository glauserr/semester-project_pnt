#!/bin/python3

from random import SystemRandom

def getrandomtree(N):
    V = list(range(N))
    E = []
    treeset = []  # spanning tree set
    nodeset = V.copy()
    _sysrand = SystemRandom()

    while len(nodeset) > 0:
        i = _sysrand.randint(0, len(nodeset) - 1)
        node = nodeset[i]

        if len(treeset) > 0:
            i = _sysrand.randint(0, len(treeset) - 1)
            treenode = treeset[i]

            if treenode < node:
                E.append([treenode, node]) 
            else: 
                E.append([node, treenode])

        nodeset.remove(node)
        treeset.append(node)

    return V, E

def getstar(N, centernode):
    V = list(range(N))
    E = []
    for v in V:
        if v != centernode:
            if v < centernode:
                E.append([v,centernode])
            else:
                E.append([centernode,v])

    return V, E