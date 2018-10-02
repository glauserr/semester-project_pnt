#!/bin/python3

import csv
from random import SystemRandom

N_NODES = 30
N_TXS = 1000
AMOUNT_MIN = 1
AMOUNT_MAX = 1000
FILE = "randomtxs1000.data"
_sysrand = SystemRandom()


def writefile(csvfile, list):
    with open(csvfile, "w") as output:
        writer = csv.writer(output, delimiter=' ')
        for val in list:
            writer.writerow(val)


def readfile(csvfile):
    retVal = list()
    with open(csvfile, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            retVal.append(row)
    return retVal


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
    createrandomtxs()
    # print(readfile(FILE))
