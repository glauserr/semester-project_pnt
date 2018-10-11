#!/bin/python3

# This a randomized algorithm returning the optimal tree with 
# a probabilty p for a transaction set

import sys
from time import time
from random import SystemRandom

from capital import getcapital

class OptimalTree():
    def __init__(self, nnodes):
        self.nnodes = nnodes
        self._sysrand = SystemRandom()
        self.createrandomtree()

    def createrandomtree(self):
        self.V, E = self.getrandomtree(self.nnodes)
        self.E = [x + [0] for x in E]

    def getrandomtree(self, nnodes):
        V = list(range(nnodes))
        E = []
        treeset = []  # spanning tree set
        nodeset = V.copy()

        while len(nodeset) > 0:
            i = self._sysrand.randint(0, len(nodeset) - 1)
            node = nodeset[i]

            if len(treeset) > 0:
                i = self._sysrand.randint(0, len(treeset) - 1)
                treenode = treeset[i]

                if treenode < node:
                    E.append([treenode, node]) 
                else: 
                    E.append([node, treenode])

            nodeset.remove(node)
            treeset.append(node)

        return V, E
    
    def getneighborhood(self, edges, node):
        neighbors = [e[1] for e in edges if e[0] == node]
        return neighbors + [e[0] for e in edges if e[1] == node]

    def getedges(self, edges, node):
        return [e for e in edges if e[0] == node or e[1] == node]

    def getsubgraphs(self, edges, node1, node2):
        def edgeforwarding(E,V,usededge, passednode):
            v = self.getneighborhood([usededge], passednode)
            es = self.getedges(edges, v[0])
            
            V.append(v[0])
            E.append(usededge)

            if len(es) == 0:
                print("Error at getsubgraphs")
                print("exit")
                exit()
            else:
                es.remove(usededge)
                for e in es:
                    edgeforwarding(E,V, e, v[0])

        E1 = []
        V1 = [node1]
        for edge in self.getedges(edges, node1):
            edgeforwarding(E1, V1, edge, node1)
        E2 = []
        V2 = [node2]
        for edge in self.getedges(edges, node2):
            edgeforwarding(E2, V2, edge, node2)

        return ((V1,E1),(V2,E2))

    def unmakrededgeexists(self):
        return min(self.E, key=lambda x: x[2])[2] == 0

    def getunmarkededges(self):
        return [e for e in self.E if e[2] == 0]

    def markedge(self, edge):
        edge[2] = 1

    def unmarkalledges(self):
        for e in self.E:
            e[2] = 0

    def isinprocessedtrees(self, treestring):
        return treestring in self.processedtrees

    def addtoprocessedtrees(self, treestring):
        self.processedtrees.append(treestring)

    def edgestostring(self, edges):
        tree = [str(x[0]) + str(x[1]) for x in edges]
        tree.sort()
        return str(tree)        

    def getoptimaltree(self, txsfile, iterations=1):
        optC = sys.maxsize
        optE = []
        optV = []
        self.processedtrees =  []
        additionals = []
        for i in range(iterations):
            V, E, C, ads = self.randomizedalg(txsfile)
            additionals.append(ads)
            if C < optC:
                optC = C
                optE = E
                optV = V

        return optV, optE, optC, additionals


    def randomizedalg(self, txsfile):
        # tstart = time()
        # repeat = True
        # while repeat:
        self.createrandomtree()
        treestring = self.edgestostring(self.E)
        # repeat = self.isinprocessedtrees(treestring)

        self.addtoprocessedtrees(treestring)
        C = getcapital(self.V, self.E, txsfile)
        newedge = None

        # _sysrand = SystemRandom()
        rounds = 0
        getcapcals = 1
        # print(self.unmakrededgeexists())
        while self.unmakrededgeexists():
            # print(self.E)
            # print(".", end="")
            rounds += 1
            unmarkededges = self.getunmarkededges()
            while 1: 
                ir = self._sysrand.randint(0, len(unmarkededges)-1)
                # ir = 0 ### REMOVE
                er = unmarkededges[ir]
                if er != newedge:
                    break;   
            self.E.remove(er)
            ((V1,E1), (V2,E2)) = self.getsubgraphs(self.E, er[0], er[1]) 
            # print("e random: {}".format(er))
            # print(V1)
            # print(V2)
            newedge = er
            connectingedges = []
            for v1 in V1:
                for v2 in V2:
                    if v1 < v2:
                        connectingedges.append([v1,v2,0])
                    else:
                        connectingedges.append([v2,v1,0])

            connectingedges.remove(er)
            # print("conn: {}".format(connectingedges))

            for e in connectingedges:
                # print("e: {}".format(e))
                edges = self.E + [e]
                treestring = self.edgestostring(edges)
                if self.isinprocessedtrees(treestring):
                    continue

                self.addtoprocessedtrees(treestring)                
                # print(self.E + [e])
                capital = getcapital(self.V, edges, txsfile)
                getcapcals += 1
                # print(capital)
                if capital < C:
                    C = capital
                    newedge = e

            self.E += [newedge]

            if newedge == er:
                # print("newedge: {}".format(newedge))
                self.markedge(newedge)
            else:
                # print("unmarkall")
                self.unmarkalledges()
        # print("")
        # if rounds > len(self.V)*(len(self.V) - 1) /2:
        # t = time() - tstart           
        # print("Capital: {}, rounds: {}, time: {} s".format(C, rounds, t))
        return self.V, self.E, C, (rounds, getcapcals)
        # print("Capital of the optimal graph: {}".format(C))
        # plotter.plotgraph([[e[0],e[1]] for e in self.E], self.V)


def main(argv):
    def parse(para, opt):
        if len(argv) not in range(len(para)+2, len(para+opt)+3):
            print("Pass parameters: {}, options: {}".format(para,opt))
            print("exit"), exit()

        a1 = int(argv[2])
        a2 = int(argv[3])
        a3 = int(argv[4])
        a4 = int(argv[5])

        try:
            a5 = argv[6]
        except IndexError:
            a5 = 1

        return a1, a2, a3, a4, a5

    args = ["run"]
    if len(argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "transaction_sets/"
    RES_DIR = "results/"
    TRE_DIR = "trees/"

    CMD = argv[1]

    if CMD == "run":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        opt = ["<iterations>"]

        nnodes,ntxs,setstart,setend,it = parse(para, opt)

        it = int(it)

        nodes = range(nnodes)
        rtree = OptimalTree(nnodes)

        for s in range(setstart, setend+1):
            print("## SET {}".format(s))
            spec = "{}n_{}txs_set{}".format(nnodes,ntxs,s)

            nnodes = nnodes
            tnxfile = TXS_DIR + "randomtxs_"+ spec +".data"
            # treedata = TRE_DIR + "trees_{}n.data".format(nnodes)
            # resultdata = RES_DIR + "result_"+ spec +".data"
            # resultgraph = RES_DIR + "result_"+ spec +"_graph_{}.png"


            V, E, C, ads = rtree.getoptimaltree(tnxfile, it)

            print("Optimal capital: {}".format(C))
    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))

if __name__ == '__main__':
    main(sys.argv)

