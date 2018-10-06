#!/bin/python3

import sys

from random import SystemRandom
from filefunctions import writefile
from filefunctions import readfile

N_NODES = 6
N_TXS = 100
SET = 1
AMOUNT_MIN = 1
AMOUNT_MAX = 100
FILE = "transaction_sets/randomtxs_{}n_{}txs_set{}.data".format(N_NODES,
    N_TXS,SET)

_sysrand = SystemRandom()

def setfile():
    global FILE
    FILE = "transaction_sets/randomtxs_{}n_{}txs_set{}.data".format(N_NODES,
        N_TXS,SET)

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


if __name__ == "__main__":

    if len(sys.argv) == 5:
        N_NODES = int(sys.argv[1])
        N_TXS = int(sys.argv[2])
        setindexstart = int(sys.argv[3])
        setindexend = int(sys.argv[4])

        for s in range(setindexstart, setindexend+1):
            SET = s
            setfile()
            createrandomtxs()

    elif len(sys.argv) == 1:
        createrandomtxs()

    else:
        print("Invalid arguments: {}".format(sys.argv[1:]))
