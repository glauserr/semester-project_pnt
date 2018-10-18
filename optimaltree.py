#!/bin/python3

# This a randomized algorithm returning the optimal tree with 
# a probabilty p for a transaction set

import sys, copy
from time import time
from random import SystemRandom

import plotter as plotter
import topologies as topo
from capital import getcapitalontxs
from filefunctions import readfile as readtxsdata
from graphfunctions import getsubgraphs
from graphfunctions import getnodes

class Base():
    def __init__(self):
        self.E = []
        self.V = []
        self.markededgelist = []
        self.processedtrees = []

    def unmakrededgeexists(self):
        return len(self.markededgelist) != len(self.E)

    def getunmarkededges(self):
        return [e for e in self.E if e not in self.markededgelist]

    def markedge(self, edge):
        self.markededgelist.append(edge)

    def unmarkalledges(self):
        self.clearmarkededgelist()

    def getmarkededgelist(self):
        return self.markededgelist

    def clearmarkededgelist(self):
        self.markededgelist = []

    def isinprocessedtrees(self, treestring):
        return treestring in self.processedtrees

    def addtoprocessedtrees(self, treestring):
        self.processedtrees.append(treestring)

    def clearprocessedtrees(self):
        self.processedtrees =  []

    def edgestostring(self, edges):
        tree = [str(x[0]) + str(x[1]) for x in edges]
        tree.sort()
        return str(tree)


class OptimalTree(Base):
    def __init__(self, nnodes):
        super().__init__()
        self.N = nnodes
        self._sysrand = SystemRandom()

    def getoptimaltree(self, txs, iterations=1, start="random"):
        optC = sys.maxsize
        optEW = []
        optV = []
        self.clearprocessedtrees()
        additionals = []
        for i in range(iterations):
            V, EW, C, ads = self.randomizedalg(txs, start)
            additionals.append(ads)
            if C < optC:
                optC = C
                optEW = EW
                optV = V

        optE = [[x[0],x[1]]for x in optEW]
        optW = [[x[2],x[3], x[4], x[5]]for x in optEW]
        return optV, optE, optC, optW, additionals
        
    def randomizedalg(self, txs, starting):
        self.clearmarkededgelist() # list to count how often edges are marked
        if starting == "star":
            self.createstar()
        elif starting == "random":
            self.createrandomtree()
        else:
            print("Warning! OptimalTree: staring with random tree")
            self.createrandomtree()
        treestring = self.edgestostring(self.E)

        self.addtoprocessedtrees(treestring)
        C, EW = getcapitalontxs(self.V, self.E, txs)
        newedge = None

        rounds = 0
        checkedgraphs = 1
        while self.unmakrededgeexists():
            rounds += 1
            unmarkededges = self.getunmarkededges()
            while 1: 
                ir = self._sysrand.randint(0, len(unmarkededges)-1)
                er = unmarkededges[ir]
                if er != newedge:
                    break;   
            self.E.remove(er)
            ((V1,E1), (V2,E2)) = getsubgraphs(er[0], er[1], self.E) 
            newedge = er
            connectingedges = []
            for v1 in V1:
                for v2 in V2:
                    if v1 < v2:
                        connectingedges.append([v1,v2])
                    else:
                        connectingedges.append([v2,v1])

            connectingedges.remove(er)

            for e in connectingedges:
                edges = self.E + [e]
                treestring = self.edgestostring(edges)
                if self.isinprocessedtrees(treestring):
                    continue

                self.addtoprocessedtrees(treestring) 
                capital,weigths = getcapitalontxs(self.V, edges, txs)
                checkedgraphs += 1
                if capital < C:
                    C = capital
                    EW = weigths
                    newedge = e

            self.E += [newedge]

            if newedge == er:
                self.markedge(newedge)
            else:
                self.unmarkalledges()

        return self.V, EW, C, (rounds, checkedgraphs)

    def createrandomtree(self):
        self.V, self.E = topo.getrandomtree(self.N)

    def createstar(self):
        i = self._sysrand.randint(0, self.N - 1)
        self.V, self.E = topo.getstar(self.N, i)


class OptimalTreeOnline(Base):
    def __init__(self, nnodes):
        super().__init__()
        self.N = nnodes
        self._sysrand = SystemRandom()

    def alg1(self, txs):
        ntxs = len(txs)
        opt = OptimalTree(self.N)
        txset1 = txs[:int(ntxs/4)]
        txset2 = txs[int(ntxs/4):]

        self.V, self.E, C0, W, ads = opt.getoptimaltree(txset1, 10)
        self.EW = [e + w for e,w in list(zip(self.E,W))]
        EW0 = copy.deepcopy(self.EW)

        pos = 0
        bs = 50 # basket size
        C = [C0]
        while pos < len(txset2):
            r = pos + bs - len(txset2)
            if r < 1:
                basket = txset2[pos:pos+bs]
            else:
                basket = txset2[pos:pos+r]
            pos += bs

            EW1, C1, ads = self.randomizedalg(basket)

            E0 = [[x[0],x[1]] for x in EW0]
            E1 = [[x[0],x[1]] for x in EW1]
            remain = []
            for e in E0:
                if e in E1:
                    remain += [1]
                else:
                    remain += [0]

            newedges = len(remain) - sum(remain)
            releasedC = [x[4] + x[5] for r,x in list(zip(remain, EW0)) if r == 0]
            releasedC = sum(releasedC)
            print("New edges: {} out of {}".format(newedges,len(EW0)))
            print("ReleasedC: {}, required: {}".format(releasedC, C1))

            C += [C1 - releasedC]
            EW0 = copy.deepcopy(EW1)


        print("Total: {}".format(sum(C)))

    def alg2(self, txs):
        ntxs = len(txs)
        opt = OptimalTree(self.N)
        txset1 = txs[:50]
        txset2 = txs[50:]

        self.V, self.E, C0, W, ads = opt.getoptimaltree(txset1, 10)
        self.EW = [e + w for e,w in list(zip(self.E,W))]
        EW0 = copy.deepcopy(self.EW)

        pos1 = 0
        C = [C0]
        txV = []
        while pos1 < len(txset2):
            pos0 = pos1
            txV = []
            while len(txV) < 9:
                txV += getnodes([txset2[pos1]])
                pos1 += 1
                if pos1 > len(txset2):
                    break

            EW1, C1, ads = self.randomizedalg(txset2[pos0:pos1])

            E0 = [[x[0],x[1]] for x in EW0]
            E1 = [[x[0],x[1]] for x in EW1]
            remain = []
            for e in E0:
                if e in E1:
                    remain += [1]
                else:
                    remain += [0]

            newedges = len(remain) - sum(remain)
            releasedC = [x[4] + x[5] for r,x in list(zip(remain, EW0)) if r == 0]
            releasedC = sum(releasedC)
            print("New edges: {} out of {}".format(newedges,len(EW0)))
            print("ReleasedC: {}, required: {}".format(releasedC, C1))

            C += [C1 - releasedC]
            EW0 = copy.deepcopy(EW1)


        print("Total: {}".format(sum(C)))


    def randomizedalg(self, txs): # modified
        # clean up EW
        def sign(value):
            if value < 0:
                return value
            else:
                return 0

        for item in self.EW:
            item[2:] =  map(sign, [x for x in item[2:]]) 

        self.clearmarkededgelist()
        rounds = 0
        checkedgraphs = 0
        newedge = None
        bestEW = None
        weightededges = copy.deepcopy(self.E)
        weights = copy.deepcopy(self.EW)
        C = sys.maxsize

        while self.unmakrededgeexists():
            rounds += 1
            unmarkededges = self.getunmarkededges()
            while 1: 
                ir = self._sysrand.randint(0, len(unmarkededges)-1)
                er = unmarkededges[ir]
                if er != newedge:
                    break;   

            item = [x for x in self.EW if x[:2] == er][0]
            self.EW.remove(item)
            self.E.remove(er)

            ((V1,E1), (V2,E2)) = getsubgraphs(er[0], er[1], self.E) 

            newedge = er
            newweight = item
            connectingedges = []

            for v1 in V1:
                for v2 in V2:
                    if v1 < v2: 
                        e = [v1, v2]
                    else:
                        e = [v2, v1]

                    if e not in weightededges:
                        connectingedges.append(e + [0,0,0,0])
                    else:
                        i = weightededges.index(e)
                        connectingedges.append(weights[i])

            for e in connectingedges:

                edgeweights = self.EW + [e]
               
                capital, edgeweigths = getcapitalontxs(self.V, 
                    edgeweights, txs, weights=True)
                checkedgraphs += 1
                if capital < C:
                    C = capital
                    bestEW = edgeweigths
                    newedge = [e[0],e[1]]
                    newweight = e

            self.E += [newedge]
            self.EW += [newweight]
            if newedge == er:
                self.markedge(newedge)
            else:
                self.unmarkalledges()

        return bestEW, C, (rounds, checkedgraphs)        


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
        opt = OptimalTree(nnodes)
        optR = OptimalTreeOnline(nnodes)

        for s in range(setstart, setend+1):
            print("## SET {}".format(s))
            spec = "{}n_{}txs_set{}".format(nnodes,ntxs,s)

            nnodes = nnodes
            txfile = TXS_DIR + "randomtxs_"+ spec +".data"

            txs = readtxsdata(txfile)

            # V, E, C, W, ads = opt.getoptimaltree(txs[2:], it)
            optR.alg2(txs[2:])
            # plotter.plotgraph(E,V)
            # plotter.show()
            # print("Optimal capital: {}".format(C))
    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))

if __name__ == '__main__':
    main(sys.argv)

