#!/bin/python3

import sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.append('../')

from time import sleep
from time import time
from random import SystemRandom

from staticgraphs import Executor
from plotter import plotgraph


class DynamicTree(Executor):
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

                if True:  # Ct <= ai:
                    for t in tablemap:
                        t[0] = t[1]
                else:  # Connect -> generates cycles
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


        edges = [[int(x[0].replace('n','')),int(x[1].replace('n',''))] \
            for x in self.channels]

        edges = [x for i,x in enumerate(edges,0) if i % 2 == 0 ]


        # self.createtopologyplot("dynamicTree.png", show=False)
        plotgraph(edges, self.nodes, "dynamicTree.png")


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


class CapitalVisualization(Executor):
    def __init__(self, simulate=False, nnodes=None):
        super().__init__(simulate,nnodes)
        # self.create()

    def executetxs(self, txs):
        self.edgestates = {}
        self.ntxs = 0

        for i, node in enumerate(self.nodes, 0):
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

            edge = "n{}-n{}".format(si, ri)

            try:
                #[[index, state sender, state receiver, payment at this state,],[],..]
                states = self.edgestates[edge]['states']
            except KeyError:
                self.edgestates[edge] = {'states': [], 'maxcapital': [0, 0],
                                         'maxTx': [0, 0], 'nleft':-1,'nright':-1}
                states = self.edgestates[edge]['states']
                states.append([-1, 0, 0, 0, 0])

            self.edgestates[edge]['nleft'] = si
            self.edgestates[edge]['nright'] = ri

            last = len(states) - 1
            state1 = states[last][1] - ai
            state2 = states[last][2] + ai
            state = [self.ntxs, state1, state2, ai]
            states.append(state)

            maxcap = self.edgestates[edge]['maxcapital']
            maxtx = self.edgestates[edge]['maxTx']

            # update the maximal needed capital
            if state1 < (-1) * maxcap[0]:
                maxcap[0] = (-1) * state1

            if state2 < (-1) * maxcap[1]:
                maxcap[1] = (-1) * state2

            # maximum tx on both direction
            if ai > 0 and maxtx[0] < ai:
                maxtx[0] = ai

            elif maxtx[1] < (-1) * ai:
                maxtx[0] = (-1) * ai

            self.ntxs += 1

        derivation = 0
        capital = 0
        print(self.edgestates)

        for key in self.edgestates:
            edge = self.edgestates[key]

            maxtx = max(edge['maxTx'])
            maxcap = sum(edge['maxcapital'])

            capital += maxcap

            if maxtx < maxcap:
                derivation += maxcap - maxtx

        print("derivation. total: {}, per tx: {}".format(
            derivation, derivation/self.ntxs))
        print("Needed capital: {}".format(capital))

        self.plotcapital()


    def plotcapital(self):
        plt.clf()
        plt.title("Needed capital during execution")
        plt.xlabel("Executed transactions")
        plt.ylabel("Needed capital")

        states = [self.edgestates[edge]['states'] for edge in self.edgestates]
        captialstate = [[0, 0] for x in states]
        capital = [[] for x in states]
        for i in range(self.ntxs):
            for j, state in enumerate(states, 0):
                s = next(((x[1], x[2]) for x in state if x[0] == i), None)

                if s != None:
                    pos, s = [(pos, s)
                              for pos, s in enumerate(s, 0) if s <= 0][0]
                    captialstate[j][pos] = (-1) * s

                capital[j].append(captialstate[j].copy())

        txrange = range(self.ntxs)
        edges = [edge for edge in self.edgestates]
        nodechannelcap = [[[]] * len(self.nodes) for x in self.nodes]

        for i, cap in enumerate(capital, 0):
            # tcap = [x[0] + x[1] for x in cap]
            nleft = int(self.edgestates[edges[i]]['nleft'])
            nright = int(self.edgestates[edges[i]]['nright'])   

            # need capital for payments from left to right or in the opposite way 
            cleft = [x[0] for x in cap]
            cright = [x[1] for x in cap]

            nodechannelcap[nleft][nright] = cleft
            nodechannelcap[nright][nleft] = cright

            plt.plot(txrange, cleft, label=edges[i] + " left")
            plt.plot(txrange, cright, label=edges[i] + " right")

        plt.legend()
        plt.show()


class TreeReduction(Executor):
    def __init__(self, nnodes, forbiddentrees=[]):
        # self.Tfb = forbiddentrees #[[<edges of tree>]]
        self.nnodes = nnodes
        self._sysrand = SystemRandom()
        self.createrandomtree()
        # self.E = [[0, 1, 0], [0, 3, 0], [2, 3, 0]] ### REMOVE
        super().__init__(simulate=False, nodes=[str(x) for x in self.V])

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

    def getcapital(self, edges, txsfile):
        # sender, receiver, capital, maxcapital, open channels

        self.channels = [[str(x[0]), str(x[1]), 0, 0 ,0] for x in edges]
        self.channels += [[str(x[1]), str(x[0]), 0, 0 ,0] for x in edges]
        self.createroutetable()
        C, ch, txs = self.run(txsfile)
        return C

    def isinprocessedtrees(self, treestring):
        return treestring in self.processedtrees

    def addtoprocessedtrees(self, treestring):
        self.processedtrees.append(treestring)

    def edgestostring(self, edges):
        tree = [str(x[0]) + str(x[1]) for x in edges]
        tree.sort()
        return str(tree)        

    def getoptimalgraph(self, txsfile, iterations=1):
        optC = sys.maxsize
        optE = []
        optV = []
        self.processedtrees =  []
        for i in range(iterations):
            V, E, C = self.optimalgraph(txsfile)
            if C < optC:
                optC = C
                optE = E
                optV = V

        return optV, optE, optC


    def optimalgraph(self, txsfile):
        tstart = time()
        repeat = True
        # while repeat:
        self.createrandomtree()
        treestring = self.edgestostring(self.E)
        repeat = self.isinprocessedtrees(treestring)

        self.addtoprocessedtrees(treestring)
        C = self.getcapital(self.E, txsfile)
        newedge = None

        _sysrand = SystemRandom()
        rounds = 0
        # print(self.unmakrededgeexists())
        while self.unmakrededgeexists():
            # print(self.E)
            print(".", end="")
            rounds += 1
            unmarkededges = self.getunmarkededges()
            while 1: 
                ir = _sysrand.randint(0, len(unmarkededges)-1)
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
                capital = self.getcapital(edges, txsfile)
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
        print("")
        # if rounds > len(self.V)*(len(self.V) - 1) /2:
        t = time() - tstart           
        print("Capital: {}, rounds: {}, time: {} s".format(C, rounds, t))
        return self.V, self.E, C
        # print("Capital of the optimal graph: {}".format(C))
        # plotter.plotgraph([[e[0],e[1]] for e in self.E], self.V)

    def executetxs(self, txs):
        self.ntxs = 0
        for src, dest, amount in txs:
            self.calccapital(src, dest, amount)
            self.ntxs += 1

def parse(para, opt):
    if len(sys.argv) not in range(len(para)+2, len(para+opt)+3):
        print("Pass parameters: {}, options: {}".format(para,opt))
        print("exit"), exit()

    a1 = int(sys.argv[2])
    a2 = int(sys.argv[3])
    a3 = int(sys.argv[4])
    a4 = int(sys.argv[5])

    try:
        a5 = sys.argv[6]
    except IndexError:
        a5 = 0

    return a1, a2, a3, a4, a5


if __name__ == "__main__":
    args = ["dtree", "rtree"]
    if len(sys.argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "../transaction_sets/"
    RES_DIR = "../results/"
    TRE_DIR = "../trees/"

    CMD = sys.argv[1]

    if CMD == "dtree":
        TXS_DIR = "transaction_sets/"
        N_NODES = 30
        N_TXS = 1000
        SET = 1

        fees = 1 # fees for transaction
        costs = 1 # cost to set up a channel
        tnxfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(
            N_NODES,N_TXS,SET)

        def output(msg, capital, channels, txs):
            profit = (txs * fees - channels * costs) / txs
            capital = capital / txs
            print("[{}]: profit per Txs: {}, capital per Txs: {}, (channels: {}, txs: {})".format(
                msg, profit, capital, channels, txs))
            return profit

        def scatter(capital, channels, txs, name, namepos, c='b'):
            profit = (txs * fees - channels * costs) / txs
            capital = capital / txs
            x, y = namepos
            plt.scatter(capital, profit, c=c, zorder=1000)
            plt.annotate(name, (capital+x, profit+y), zorder=1001)

        topology = DynamicTree()
        cap, chan, txs = topology.run(tnxfile)

        plt.clf()
        plt.xlabel("Needed capital / transactions")
        plt.ylabel("Profit / transactions")
        plt.axis([180, 500, 0.92, 1])
        plt.grid(True)

        scatter(cap, chan, txs, "max payment based", (1, 0.01))
        output("offline", cap, chan, txs)
        plt.title("Max payment based topology design")
        plt.show()

        # topology = CapitalVisualization(nnodes=3)
        # cap, chan, txs = topology.run("3node.data")
    
    elif CMD == "rtree":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        opt = ["<iterations>"]

        nnodes,ntxs,setstart,setend,it = parse(para, opt)

        specadd = ""
        it = int(it)
            # rmd = re.findall(r'\d+', rmd)
            # rmd = [int(x) for x in rmd]   
            # specadd = "_rmd{}".format(rmd)
            # nodes = [n for n in range(nnodes) if n not in rmd]
            # mapping = getmapping(nodes)

        nodes = range(nnodes)
        rtree = TreeReduction(nnodes)

        for s in range(setstart, setend+1):
            print("## SET {}".format(s))
            spec = "{}n_{}txs_set{}".format(nnodes,ntxs,s)
            spec += specadd

            nnodes = nnodes
            tnxfile = TXS_DIR + "randomtxs_"+ spec +".data"
            # treedata = TRE_DIR + "trees_{}n.data".format(nnodes)
            # resultdata = RES_DIR + "result_"+ spec +".data"
            # resultgraph = RES_DIR + "result_"+ spec +"_graph_{}.png"


            V, E, C = rtree.getoptimalgraph(tnxfile, it)

            print("Optimal capital: {}".format(C))
            # plotter.plotgraph([[e[0],e[1]] for e in optE], optV)
            # plt.figure()


    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))