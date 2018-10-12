#!/bin/python3

import sys,re
import csv
import math
from time import time
from random import SystemRandom

import filefunctions as ff
import plotter as plotter

from capital import getcapital

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
                if v < n:
                    T.append([v, n])
                else:
                    T.append([n, v])
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

    if v < u:
        T.append([v, u])
    else:
        T.append([u, v])
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
                retVal.append([int(x) for x in row])


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
        a5 = []

    return a1, a2, a3, a4, a5

if __name__ == '__main__':
    args = ["create", "run", "plot"]
    if len(sys.argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "transaction_sets/"
    RES_DIR = "results/"
    TRE_DIR = "trees/"

    import os
    if not os.path.exists("./" + TRE_DIR):
        os.mkdir(TRE_DIR)
    if not os.path.exists("./" + RES_DIR):
        os.mkdir(RES_DIR)
        
    CMD = sys.argv[1]

    if CMD == "create":
        opt = ["<number of nodes>"]
        if len(sys.argv) != len(opt) + 2:
            print("Pass options: {}".format(opt))
            print("exit"), exit()

        nnodes = int(sys.argv[2])
        treedata = TRE_DIR + "trees_{}n.data".format(nnodes)
        createtrees(nnodes, treedata)

    elif CMD == "run":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        opt = [""]

        nnodes,ntxs,setstart,setend,rmd = parse(para, opt)

        for s in range(setstart, setend+1):
            print("## SET {} ##".format(s))

            spec = "{}n_{}txs_set{}".format(nnodes,ntxs,s)

            treedata = TRE_DIR + "trees_{}n.data".format(nnodes)
            tnxfile = TXS_DIR + "randomtxs_"+ spec +".data"
            resultdata = RES_DIR + "result_"+ spec +".data"

            V = range(nnodes)
            capital = list()
            lt = loadtree(treedata)
            numberoftrees = math.pow(nnodes, nnodes-2)

            start = time()

            index = 0
            if numberoftrees > 20:
                percstep = 5
            else:
                percstep = 50
                
            while 1:
                try:
                    E = next(lt)
                except StopIteration:
                    break

                cap = getcapital(V, E, tnxfile)
                capital.append((cap,index))

                if index % int(percstep*numberoftrees/100) == 0:
                    print("{} %".format(percstep * \
                        int(100*index/numberoftrees/percstep + 0.5)), end=".. ", flush=True)
                index += 1
            print("")

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
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        opt = [""]

        nnodes,ntxs,setstart,setend,rmd = parse(para, opt)

        nodes = range(nnodes)

        for s in range(setstart, setend+1):
            spec = "{}n_{}txs_set{}".format(nnodes,ntxs,s)

            treedata = TRE_DIR + "trees_{}n.data".format(nnodes)
            resultdata = RES_DIR + "result_"+ spec +".data"
            resultgraph = RES_DIR + "result_"+ spec +"_graph_{}.png"

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

                plotter.plotgraph(edges, nodes, 
                    savefilename=resultgraph.format(tn))

    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))
