#!/bin/python3

import sys,re
import csv
import math
from time import time
from random import SystemRandom

import filefunctions as ff
import plotter as plotter

from executor import Executor


def sequencetotree(sequence):
    n = len(sequence)
    nodes = range(n+2)
    degree = [1 for x in nodes]
    T = []

    for v in sequence:
        degree[v] += 1

    for v in sequence:
        for n in nodes:
            if degree[n] == 1:
                sv = "n" + str(v)           
                sn = "n" + str(n)           
                T.append([sv, sn, 0, 0, 0])
                T.append([sn, sv, 0, 0, 0])
                degree[v] -= 1
                degree[n] -= 1
                break

    u = 0
    v = 0

    for n in nodes:
        if degree[n] == 1:
            if u == 0:
                u = n
            else:
                v = n
                break

    su = "n" + str(u)           
    sv = "n" + str(v)           
    T.append([su, sv, 0, 0, 0])
    T.append([sv, su, 0, 0, 0])
    degree[u] -= 1
    degree[v] -= 1

    return T


def getallsequences(nnodes):
    T = []
    seqlength = nnodes-2
    exp = list(reversed(range(seqlength)))
    seq = [0 for i in exp]
    for i, x in enumerate(exp, 0):
        exp[i] = math.pow(nnodes, x)

    cnt = 0
    while cnt < math.pow(nnodes, nnodes-2):
        t = cnt
        for i, x in enumerate(exp, 0):
            s = int(t / x)
            t = t - s*x
            seq[i] = s

        T.append(seq.copy())
        cnt += 1

    return T


def createtrees(nnodes, filname):
    S = getallsequences(nnodes)

    with open(filname, "w") as output:
        writer = csv.writer(output, delimiter=' ')
        for i, seq in enumerate(S, 0):
            t = sequencetotree(seq)
            for val in t:
                writer.writerow(val)
            writer.writerow(["tree {} end".format(i)])


def loadtree(filname):
    retVal = list()

    with open(filname, "r") as file:
        reader = csv.reader(file, delimiter=' ')
        for row in reader:
            if "end" in str(row):
                yield retVal
                retVal = []
            else:
                retVal.append([x for x in row[:2]] + [int(x) for x in row[2:]])


class Tree(Executor):

    def settree(self, T, nnodes):
        super().__init__(nnodes=nnodes)
        self.channels = T
        self.createroutetable()


if __name__ == '__main__':
    args = ["create", "run"]
    if len(sys.argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "transaction_sets/"
    RES_DIR = "results/"
    TRE_DIR = "trees/"

    CMD = sys.argv[1]

    if CMD == "create":
        opt = ["<number of nodes>"]
        if len(sys.argv) != len(opt) + 2:
            print("Pass options: {}".format(opt))
            print("exit"), exit()

        N_NODES = int(sys.argv[2])
        treedata = TRE_DIR + "trees_{}n.data".format(N_NODES)
        createtrees(N_NODES, treedata)

    elif CMD == "run":
        opt = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        if len(sys.argv) != len(opt) + 2:
            print("Pass options: {}".format(opt))
            print("exit"), exit()

        N_NODES = int(sys.argv[2])
        N_TXS = int(sys.argv[3])
        setindexstart = int(sys.argv[4])
        setindexend = int(sys.argv[5])

        for s in range(setindexstart, setindexend+1):
            SET = s
            print("## SET {} ##".format(SET))

            tnxfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(
                N_NODES,N_TXS,SET)
            treedata = TRE_DIR + "trees_{}n.data".format(N_NODES)
            resultdata = RES_DIR + "result_{}n_{}txs_set{}.data".format(
                N_NODES,N_TXS,SET)

            capital = list()
            tree = Tree()
            lt = loadtree(treedata)
            numberoftrees = math.pow(N_NODES, N_NODES-2)

            start = time()

            index = 0
            if numberoftrees > 20:
                percstep = 5
            else:
                percstep = 50
                
            while 1:
                try:
                    t = next(lt)
                except StopIteration:
                    break

                tree.settree(t, N_NODES)
                cap, chan, txs = tree.run(tnxfile)
                capital.append((cap,index))

                if index % int(percstep*numberoftrees/100) == 0:
                    print("{} %".format(percstep * \
                        int(100*index/numberoftrees/percstep + 0.5)))
                index += 1

            end = time()

            print("Time: {}".format(end-start))

            bestcapital = min(capital, key=lambda x:x[0])
            bestcapital = bestcapital[0]
            besttrees = [x[1] for x in capital if x[0] == bestcapital]

            print("Optimal tree. capital: {}, number: {}".format(bestcapital, 
                besttrees))

            output = []
            output.append(["optimal capital: {}".format(bestcapital)])
            output.append(["optimal trees: {}".format(besttrees)])
            output.append(["Results:"])
            output += capital

            ff.writefile(resultdata, output)

    elif CMD == "plot":
        opt = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        if len(sys.argv) != len(opt) + 2:
            print("Pass options: {}".format(opt))
            print("exit"), exit()
        
        N_NODES = int(sys.argv[2])
        N_TXS = int(sys.argv[3])
        setindexstart = int(sys.argv[4])
        setindexend = int(sys.argv[5])

        for s in range(setindexstart, setindexend+1):
            SET = s

            treedata = TRE_DIR + "trees_{}n.data".format(N_NODES)
            resultdata = RES_DIR + "result_{}n_{}txs_set{}.data".format(
                N_NODES,N_TXS,SET)
            resultgraph = RES_DIR + "result_{}n_{}txs_set{}".format(
                N_NODES,N_TXS,SET) + "_graph_{}.png"

            find = "optimal trees: "
            pos, line = ff.searchinfile(resultdata, find)
            line = re.findall(r'\d+', line)
            besttrees = [int(x) for x in line]

            for tn in besttrees:
                pos = 0
                if tn != 0:
                    pos, line = ff.searchinfile(treedata, "tree {} end".format(tn-1))
                    pos += len(line)
                
                t = ff.readfileatuntil(treedata, pos, "tree {} end".format(tn), 
                    delimiter=" ")
                
                edges = [[int(x[0].replace('n','')),int(x[1].replace('n',''))] \
                    for x in t]

                edges = [x for i,x in enumerate(edges,0) if i % 2 == 0 ]

                plotter.plotgraph(edges, N_NODES, 
                    savefilename=resultgraph.format(tn))

    else:
        print("{} unknown".format(CMD))
