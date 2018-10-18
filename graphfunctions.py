#!/bin/python3

from collections import Counter

def getshorteslongestpath(V, E):
    def forward(sender, receiver):
        neighbors = getneighborhood(receiver, E)
        neighbors.remove(sender)
        if neighbors == []:
            return 1
        else:
            hops = [1 + forward(receiver, n) for n in neighbors]
            return max(hops)

    longestpath = []
    for v in V:
        neighborhood = getneighborhood(v, E)
        hops = [forward(v, n) for n in neighborhood]
        longestpath += [max(hops)]

    return min(longestpath)

def getdegreedistribution(V, E):
    c = Counter()
    for v in V:
        neighbors = getneighborhood(v, E)
        c.update([len(neighbors)])

    c = dict(c)
    return list(c.keys()), list(c.values())

def getneighborhood(v, E):
    neighbors = [e[1] for e in E if e[0] == v]
    return neighbors + [e[0] for e in E if e[1] == v]   


def getroutetables(V, E):
    def forward(sender, receiver, token, hops):
        if token == receiver:
            return 0

        rt = routetables[receiver] # [[token, nextnode, hops], []]
        try:
            i = [r[0] for r in rt].index(token)
        except ValueError:
            i = -1

        if i < 0:
            rt.append([token, sender, hops])
        elif rt[i][2] > hops:              
            rt.remove(rt[i])
            rt.append([token, sender, hops])
        else:
            return 0

        hops += 1
        forwardto = getneighborhood(receiver, E)
        forwardto.remove(sender)
        for f in forwardto:
            forward(receiver, f, token, hops)

    routetables = {}
    for v in V:
        routetables[v] = []

    for v in V:
        neighbors = getneighborhood(v, E)
        for neighbor in neighbors:
            forward(v, neighbor, v, 1)

    return routetables

def pathexists(sender, receiver, routetables):
    if sender in routetables:
        rt = routetables[sender]

        entry = [x for x in rt if x[0] == receiver]

        if entry != []:
            return True

    return False

def getcycles(v, E):
    paths = []
    pathsorted = []
    def forward(sender, receiver, path):
        path = path.copy()
        if receiver in path:
            index = path.index(receiver)
            p = path[index:]
            if sorted(p) not in pathsorted:
                pathsorted.append(sorted(p))
                paths.append(p + [receiver])
            return 0 # we have a cycle
                    
        path += [receiver]

        forwardto = getneighborhood(receiver, E)
        forwardto.remove(sender)
        for f in forwardto:
            forward(receiver, f, path)    

    for n in getneighborhood(v, E):
        forward(v, n, [])

    return paths


def getedges(v, E):
    return [e for e in E if e[0] == v or e[1] == v]

def getnodes(E):
    V = []
    for e in E:
        if e[0] not in V:
            V += [e[0]]
        if e[1] not in V:
            V += [e[1]]

    return V

def getsubgraphs(v1, v2, E):
    def edgeforwarding(fV, passednode, fE, usededge):
        v = getneighborhood(passednode, [usededge])
        es = getedges(v[0], E)
        fV.append(v[0])
        fE.append(usededge)

        if len(es) == 0:
            print("Error at getsubgraphs")
            print("exit")
            exit()
        else:
            es.remove(usededge)
            for e in es:
                edgeforwarding(fV, v[0], fE, e)

    E1 = []
    V1 = [v1]
    for edge in getedges(v1, E):
        edgeforwarding(V1, v1, E1, edge)
    E2 = []
    V2 = [v2]
    for edge in getedges(v2, E):
        edgeforwarding(V2, v2, E2, edge)

    return ((V1,E1),(V2,E2))


    
if __name__ == '__main__':
    E = [[0, 1],[9,4],[4,7],[4,2],[4,3],[2,8],[1,9],[5,9], [6,0]]
    V = list(range(10))
    X, Y = getdegreedistribution(V,E)

    xmax = max(X)
    bins = range(1, xmax + 2)

    bins = [b-0.5 for b in bins]

    data = []
    for x,y in list(zip(X,Y)):
        data += [x] * y 

    xylabels = ("Degree [1]", "Occurrence [1]")
    title = "Degree distribution"
    # plotter.plotdist(data, bins, xylabel, title)
    plt.figure()
    plt.hist(data, bins=bins,edgecolor='black', linewidth=1, rwidth=0.5)
    plt.title(title)
    plt.xlabel(xylabels[0])
    plt.ylabel(xylabels[1])
    plt.show()
