#!/bin/python3

import sys,re

from random import SystemRandom
from filefunctions import writefile
from filefunctions import readfile

N_NODES = 6
N_TXS = 100
SET = 1
AMOUNT_MIN = 1
AMOUNT_MAX = 100
TXS_DIR = "transaction_sets/"
FILE = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(N_NODES,
    N_TXS,SET)

_sysrand = SystemRandom()

def randomtx():
    repeat = True
    while repeat:
        n1 = _sysrand.randint(0, N_NODES-1)
        n2 = _sysrand.randint(0, N_NODES-1)
        if n1 != n2:
            repeat = False
    amount = _sysrand.randint(AMOUNT_MIN, AMOUNT_MAX)
    return n1, n2, amount


def createrandomtxs():
    txs = list()
    txs.append([])
    txs.append([])

    average = 0
    for n in range(N_TXS):
        n1, n2, amount = randomtx()
        average += amount 
        txs.append((n1, n2, amount))

    average = average / N_TXS

    txs[0] = ["N_NODES: {};".format(N_NODES),
                "N_TXS: {};".format(N_TXS),
                "AMOUNT_MIN: {};".format(AMOUNT_MIN),
                "AMOUNT_MAX: {};".format(AMOUNT_MAX),
                "AMOUNT_AVG: {};".format(average)]
    txs[1] = ["node1", "node2", "amount"]
    
    writefile(FILE, txs)


def removenodes(txs, nodes):
    retval = []
    for si, ri, ai in txs:
        si = int(si)
        ri = int(ri)
        if si in nodes or ri in nodes:
            continue
        retval.append([si,ri,ai])

    return retval

def parse(para, opt=list()):
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
        a5 = None

    return a1, a2, a3, a4, a5


if __name__ == "__main__":
    args = ["create", "reduce"]

    if len(sys.argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    CMD = sys.argv[1]

    if CMD == "create":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]

        if len(sys.argv) == len(para) + 2:
            N_NODES,N_TXS,setstart,setend = parse(para)

            for s in range(setindexstart, setindexend+1):
                SET = s
                FILE = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(N_NODES,
                    N_TXS,SET)
                createrandomtxs()

        elif len(sys.argv) == 2:
            createrandomtxs()

        else:
            print("Pass options: {}".format(para))
            print("exit"), exit()

    elif CMD == "remove":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>", "<nodes to remove>"]   

        N_NODES,N_TXS,setstart,setend,rmd = parse(para)

        for s in range(setstart, setend+1):
            SET = s

            rmd = re.findall(r'\d+', rmd)
            rmd = [int(x) for x in rmd]

            rmtxfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}_rmd{}.data".format(N_NODES,
                N_TXS,SET,rmd)

            txfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(N_NODES,
                N_TXS,SET)

            txs = readfile(txfile)

            removedtxs = removenodes(txs[2:], rmd)

            newtxs = []
            newtxs.append(txs[0])
            newtxs[0].append(";REMOVED {}".format(rmd))
            newtxs.append(txs[1])
            newtxs += removedtxs

            writefile(rmtxfile, newtxs)

    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))
