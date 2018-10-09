#!/bin/python3

# Note: this does not create the optimal tree.

import sys, re

import plotter
import filefunctions as ff

def getmaxflowsandnodes(txs):
    nodes = []
    maxflow = {} # {<edge>: [<value>, <direction>], ...}
    currentflow = {} # {<edge>: <value>, ...}

    for n1, n2, a, in txs:
        n1 = int(n1)
        n2 = int(n2)
        a = int(a)

        if n1 not in nodes:
            nodes.append(n1)
        if n2 not in nodes:
            nodes.append(n2)
        # always smaller node to larger node
        if n1 > n2:
            t = n1
            n1 = n2
            n2 = t
            a = -a

        edge = "{}-{}".format(n1,n2)

        if edge not in currentflow:
            currentflow[edge] = 0
            maxflow[edge] = [0,0]

        currentflow[edge] += a

        if abs(currentflow[edge]) > maxflow[edge][0]:
            maxflow[edge][0] = abs(currentflow[edge])
            if a > 0:
                maxflow[edge][1] = 1
            else: 
                maxflow[edge][1] = -1

    return maxflow, nodes


def parse(para, opt):
    if len(sys.argv) not in range(len(para)+2, len(para+opt)+3):
        print("Pass parameters: {}, options: {}".format(para, opt))
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


def main():
    args = ["run", ]
    if len(sys.argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "transaction_sets/"
    RES_DIR = "results/"
    TRE_DIR = "trees/"

    CMD = sys.argv[1]

    if CMD == "run":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        opt = ["<removed nodes>"]

        nnodes, ntxs, setstart, setend, rmd = parse(para, opt)

        specadd = ""
        mapping = None
        if rmd != []:
            rmd = re.findall(r'\d+', rmd)
            rmd = [int(x) for x in rmd]
            specadd = "_rmd{}".format(rmd)
            nodes = [n for n in range(nnodes) if n not in rmd]
            mapping = getmapping(nodes)

        for s in range(setstart, setend+1):
            print("## SET {} ##".format(s))

            spec = "{}n_{}txs_set{}".format(nnodes, ntxs, s)
            spec += specadd

            nnodes = nnodes - len(rmd)
            treedata = TRE_DIR + "trees_{}n.data".format(nnodes)
            tnxfile = TXS_DIR + "randomtxs_" + spec + ".data"
            resultdata = RES_DIR + "result_" + spec + ".data"

            txs = ff.readfile(tnxfile)

            maxflows, nodes = getmaxflowsandnodes(txs[2:])
            print(maxflows)

            # print("Max flow edge: {}".format(maxflow))
            edges = []
            for i in range(len(nodes) - 1): 
                edge = max(maxflows, key= lambda x: maxflows[x][0])
                maxflows.pop(edge)
                
                edge = re.findall(r'\d+', edge)
                edges.append([int(x) for x in edge])

            print(edges)

            # edges = [[x[0], x[1]] for x in maxflows]
            # plotter.plotgraph(edges, nodes)

if __name__ == '__main__':
    main()
