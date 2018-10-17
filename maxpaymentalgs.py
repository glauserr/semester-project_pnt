#!/bin/python3

import sys
import matplotlib.pyplot as plt

from filefunctions import readfile
from capital import getcapital
from capital import getcapitalontxs

from graphfunctions import getroutetables
from graphfunctions import pathexists
from graphfunctions import getcycles

class MaxPaymentAlg():
    def getgraph(self, txsfile):
        return self.alg(txsfile)

    def alg(self, txsfile):
        V = []
        E = []

        routetables = {}

        txs = readfile(txsfile)
        txs = txs[2:]

        while len(txs) > 0:
            maxtxs = max(txs, key=lambda x: x[2])
            pos = txs.index(maxtxs)
            txs.remove(maxtxs)

            si, ri, ai = maxtxs
            si = int(si)
            ri = int(ri)
            ai = int(ai)

            if si not in V:
                V.append(si)
            if ri not in V:
                V.append(ri)

            if si < ri:
                edge = [si, ri]
            else:
                edge = [ri, si]
                
            if not pathexists(si, ri, routetables):
                routetables = getroutetables(V, E)
                E += [edge]

        return V, E


class MaxPaymentAlgWithCycles():
    def getgraph(self, txsfile):
        return self.alg(txsfile)

    def alg(self, txsfile):
        V = []
        E = []

        routetables = {}

        txs = readfile(txsfile)
        txs = txs[2:]

        indexedtxs = {}

        while len(txs) > 0:
            maxtxs = max(txs, key=lambda x: x[2])
            pos = txs.index(maxtxs)
            txs.remove(maxtxs)

            si, ri, ai = maxtxs
            si = int(si)
            ri = int(ri)
            ai = int(ai)

            indexedtxs[pos] = [si, ri, ai]

            if si not in V:
                V.append(si)
            if ri not in V:
                V.append(ri)

            if si < ri:
                edge = [si, ri]
            else:
                edge = [ri, si]

            if not pathexists(si, ri, routetables):
                E += [edge]
                routetables = getroutetables(V, E)
            elif edge not in E: 
                ctxs = list(indexedtxs.items())
                ctxs.sort(key=lambda x: x[0])
                ctxs = [x[1] for x in ctxs]
                C1 = getcapitalontxs(V, E, ctxs)
                C2 = getcapitalontxs(V, E + [edge], ctxs)

                if C2 < C1:
                    E += [edge]
            else:
                pass # edge already exists

        return V, E    


class MaxPaymentAlgWithReduction():
    def getgraph(self, txsfile):
        return self.alg(txsfile)

    def alg(self, txsfile):
        V = []
        E = []

        routetables = {}

        txs = readfile(txsfile)
        txs = txs[2:]

        indexedtxs = {}

        while len(txs) > 0:
            maxtxs = max(txs, key=lambda x: x[2])
            pos = txs.index(maxtxs)
            txs.remove(maxtxs)

            si, ri, ai = maxtxs
            si = int(si)
            ri = int(ri)
            ai = int(ai)

            indexedtxs[pos] = [si, ri, ai]

            if si not in V:
                V.append(si)
            if ri not in V:
                V.append(ri)

            if si < ri:
                edge = [si, ri]
            else:
                edge = [ri, si]

            if not pathexists(si, ri, routetables):
                E += [edge]
                routetables = getroutetables(V, E)
            elif edge not in E: 
                ctxs = list(indexedtxs.items())
                ctxs.sort(key=lambda x: x[0])
                ctxs = [x[1] for x in ctxs]

                cE = E + [edge]
                cycle = getcycles(si, cE)[0]

                bestC = sys.maxsize
                removeedge = [] 

                for i in range(len(cycle)-1):
                    cv1 = cycle[i]
                    cv2 = cycle[i+1]

                    if cv1 < cv2:
                        ce = [cv1, cv2]
                    else:
                        ce = [cv2, cv1]

                    cEtmp = cE.copy()
                    cEtmp.remove(ce)
                    C = getcapitalontxs(V, cEtmp, ctxs)

                    if C < bestC:
                        bestC = C
                        removeedge = ce

                cE.remove(removeedge)
                E = cE
            else:
                pass # edge already exists

        return V, E   

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

    def output(msg, capital, channels, txs):
        profit = (txs - channels) / txs
        capital = capital / txs
        print("[{}]: profit per Txs: {}, capital per Txs: {}, (channels: {}, txs: {})".format(
            msg, profit, capital, channels, txs))
        return profit

    def scatter(capital, channels, txs, name, namepos, c='b'):
        profit = (txs - channels) / txs
        capital = capital / txs
        x, y = namepos
        plt.scatter(capital, profit, c=c, zorder=1000)
        plt.annotate(name, (capital+x, profit+y), zorder=1001)


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

        alg = MaxPaymentAlgWithReduction()

        for s in range(setstart, setend+1):
            print("## SET {}".format(s))
            spec = "{}n_{}txs_set{}".format(nnodes,ntxs,s)

            nnodes = nnodes
            tnxfile = TXS_DIR + "randomtxs_"+ spec +".data"

            V, E = alg.getgraph(tnxfile)
            C = getcapital(V,E, tnxfile)

            # cycles = getcycles(V[0], E)

            print("Capital: {}".format(C))

            plt.clf()
            plt.xlabel("Needed capital / transactions")
            plt.ylabel("Profit / transactions")
            # plt.axis([180, 500, 0.92, 1])
            plt.grid(True)

            scatter(C, len(E), ntxs, "max payment based", (1, 0.01))
            output("offline", C, len(E), ntxs)
            plt.title("Max payment based topology design")
            plt.show()

    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))

if __name__ == '__main__':
    main(sys.argv)