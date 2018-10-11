#!/bin/python3

import re,sys
from time import time
import matplotlib.pyplot as plt

from optimaltree import OptimalTree as OPT
import filefunctions as ff


def main():
    argv = sys.argv
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

    args = ["run", "plot"]
    if len(argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "transaction_sets/"
    RES_DIR = "results/"
    OUT_DIR = "optimaltree_analysis/"

    import os
    if not os.path.exists("./" + OUT_DIR):
        os.mkdir(OUT_DIR)    

    CMD = argv[1]
    if CMD == "run":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        opt = ["<iterations>"]

        nnodes,ntxs,setstart,setend,it = parse(para, opt)
        iterations = 1000

        for s in range(setstart, setend+1):
            set = s
            print("Set {}".format(set))

            txsfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
            resultdata = RES_DIR + "result_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
            outputfile = OUT_DIR + "scores_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)

            find = "optimal capital: "
            pos, line = ff.searchinfile(resultdata, find)
            line = re.findall(r'\d+', line)
            optC = [int(x) for x in line][0]

            scores = 0
            output = []

            alg = OPT(nnodes)

            for i in range(iterations):
                start = time()
                V, E, C, ads = alg.getoptimaltree(txsfile)
                end = time()
                output.append([C, end-start, ads])
                if C == optC:
                    scores += 1

            avgtime = sum([x[1] for x in output])
            maxtime = max(output, key=lambda x: x[1])[1]

            output = [["scores: {}".format(scores)],  \
                        ["; accuracy: {} %".format(scores/iterations*100)], \
                        ["; avg. time: {} s".format(avgtime)], \
                        ["; max. time: {} s".format(maxtime)]] \
                    + [["capital, time, (rounds, checked graphs)"]] \
                    + output
            ff.writefile(outputfile, output)

            print("scores: {} out of {}, accuracy: {} %".format(scores, iterations,
                scores/iterations*100))
            print("avg. time: {} s, max. time: {} s".format(avgtime, maxtime))
    
    elif CMD == "plot":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>"]
        opt = ["<iterations>"]

        nnodes,ntxs,setstart,setend,it = parse(para, opt)

        accs = []

        for s in range(setstart, setend+1):
            set = s

            txsfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
            resultdata = RES_DIR + "result_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
            outputfile = OUT_DIR + "scores_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)

            find = "accuracy:"
            pos, line = ff.searchinfile(outputfile, find)
            line = re.findall(r'\d+', line)
            acc = [int(x) for x in line][0]   
            accs.append(acc/100)


        # Make your plot, set your axes labels
        fig,ax = plt.subplots(1)
        ax.set_ylabel('')
        ax.set_xlabel('Probabilty p')

        # Turn off tick labels
        ax.set_yticklabels([])
        # ax.set_xticklabels([])

        ax.axis([0, 1.05, 0.9, 1.1])
        ax.scatter(accs, [1]*len(accs))
        minacc = min(accs)
        ax.annotate("{}".format(minacc), xy=(minacc+0.01, 1+0.005))
        ax.set_title("Probability analysis for {} nodes on {} sets\n".format(nnodes,setend+1-setstart) \
            + "({} iterations are done per each set)".format(1000))
        plt.show()

    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))
if __name__ == '__main__':
    main()