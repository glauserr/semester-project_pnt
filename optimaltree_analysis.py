#!/bin/python3

import re,sys, json, copy
from time import time
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

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
        a5 = int(argv[6])

        try:
            a6 = argv[7]
        except IndexError:
            a6 = ""

        return a1, a2, a3, a4, a5, a6

    def scoredatareadtrees(scorefile):
        find = "Trees"
        pos, line = ff.searchinfile(scorefile, find)
        pos += len(line)
        line = re.findall(r'\d+', line)
        ntrees = int(line[0])
        
        lines = ff.readfileat(scorefile, pos, ntrees, delimiter="\n\r")
        outputtree = []
        capitals = []
        for l in lines:
            t = re.findall(r'\d+\-\d+',l[0])
            c = re.findall(r'\d+', re.findall(r'C=\d+"',l[0])[0])[0]
            outputtree.append(t)
            capitals.append(int(c))

        return outputtree, capitals

    args = ["run", "plot", "analysis"]
    if len(argv) < 2:
        print("Pass an argument: {}".format(args))
        print("exit"), exit()

    TXS_DIR = "transaction_sets/"
    RES_DIR = "results/"
    OUT_DIR = "optimaltree_analysis/"
    TRE_DIR = "trees/"

    import os
    if not os.path.exists("./" + OUT_DIR):
        os.mkdir(OUT_DIR)    

    CMD = argv[1]
    if CMD == "run" or CMD == "run_on_star":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>","<iterations>"]
        opt = ["<check to brute-force (true/false)>"]

        nnodes,ntxs,setstart,setend,it, bt = parse(para, opt)
        iterations = it

        for s in range(setstart, setend+1):
            set = s
            print("Set {}".format(set))

            txsfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
            resultdata = RES_DIR + "result_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
            if CMD == "run_on_star":
                outputfile = OUT_DIR + "scores_{}n_{}txs_set{}_its{}_star.data".format(nnodes,ntxs,set,iterations)
            else: 
                outputfile = OUT_DIR + "scores_{}n_{}txs_set{}_its{}.data".format(nnodes,ntxs,set,iterations)

            if bt == "true":
                find = "optimal capital: "
                pos, line = ff.searchinfile(resultdata, find)
                line = re.findall(r'\d+', line)
                optC = [int(x) for x in line][0]

            scores = 0
            output = []

            alg = OPT(nnodes)
            trees = []
            capitals = []
            deviations = []
            txs = ff.readfile(txsfile)[2:]
            for i in range(iterations):
                start = time()
                if CMD == "run_on_star":
                    V, E, C, W, ads = alg.getoptimaltree(txs, start="star")
                else:
                    V, E, C, W, ads = alg.getoptimaltree(txs)
                end = time()
                # output tree
                edges = [str(x[0]) + "-" + str(x[1]) for x in E]
                edges = str(sorted(edges))
                if edges not in trees:
                    trees.append(edges)
                    capitals.append(C)
                # edges marked during search
                markededges = alg.getmarkededgelist()
                markededges = [str(x[0]) + "-" + str(x[1]) for x in markededges]
                markededges = Counter(markededges)

                ti = trees.index(edges)
                output.append([ti, end-start, C, markededges, ads])

            if bt != "true":
                optC = min(output, key=lambda x: x[2])[2]

            for o in output:
                if o[2] == optC:
                    scores += 1
                o[2] = o[2] / optC
                deviations.append(o[2])

            avgtime = sum([x[1] for x in output])
            maxtime = max(output, key=lambda x: x[1])[1]
            bestC = min(capitals)
            bestT = capitals.index(bestC)

            out = [["scores: {}".format(scores)],  \
                        ["accuracy: {} %".format(scores/iterations*100)], \
                        ["avg. deviation: {0:.3f}".format(sum(deviations)/len(deviations))], \
                        ["max. deviation: {0:.3f}".format(max(deviations))], \
                        ["total time: {0:.3f} s".format(avgtime)], \
                        ["max. time: {0:.3f} s".format(maxtime)], \
                        ["best tree: {} capital: {}".format(bestT, bestC)]] \
                    + [["Trees ({}):".format(len(trees))]]
            for i,t in enumerate(trees):
                out +=  [["({}) {} C={}".format(i,t,capitals[i])]]

            out += [["index, time, C/optC, marked edges counter, (rounds, checked graphs)"]] \
                    + output
            ff.writefile(outputfile, out)

            print("scores: {} out of {}, accuracy: {} %".format(scores, iterations,
                scores/iterations*100))
            print("avg. time: {} s, max. time: {} s".format(avgtime, maxtime))
    
    elif CMD == "plot":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>", "<iterations>"]
        opt = ["<type>"]
        types = ["<probability>", "<distribution>", "<scatter>", "<overall probability>"]

        nnodes,ntxs,setstart,setend,its,type = parse(para, opt)


        if type == "p": #probability
            accs = []
            for s in range(setstart, setend+1):
                set = s

                txsfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
                # resultdata = RES_DIR + "result_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
                scoredata = OUT_DIR + "scores_{}n_{}txs_set{}_its{}.data".format(nnodes,ntxs,set,its)

                find = "accuracy:"
                pos, line = ff.searchinfile(scoredata, find)
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
                + "({} iterations are done per each set)".format(its))
            plt.show()
        elif type == "d": # distribution
            for s in range(setstart, setend+1):
                set = s

                txsfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
                scoredata = OUT_DIR + "scores_{}n_{}txs_set{}_its{}.data".format(nnodes,ntxs,set,its)
                outputfile = OUT_DIR + "scores_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)

                trees, capitals = scoredatareadtrees(scoredata)
                # capitals = sorted(capitals)

                def find(string, stringline):
                    for line in stringline:
                        if string in line[0]:
                            return line


                cnt = Counter()
                lines = ff.readfile(scoredata)

                avgdevi = find("avg. deviation", lines)[0]
                avgdevi = re.findall(r'\d+.\d+', avgdevi)[0]

                maxdevi = find("max. deviation", lines)[0]
                maxdevi = re.findall(r'\d+.\d+', maxdevi)[0]

                avgdevi = float(avgdevi)
                maxdevi = float(maxdevi)

                for line in lines:
                    if len(line)>1:
                        cnt.update({line[0]:1})

                items = cnt.items()
                keys = [x[0] for x in items]
                values = [x[1] for x in items]

                data = []
                for key,value in list(zip(keys, values)):
                    data += value * [capitals[int(key)]]

                optcap = min(capitals)
                maxcap = max(capitals)

                plt.hist(data, bins=sorted(capitals),edgecolor='black', linewidth=1)
                plt.errorbar([optcap], [max(values)/4], 
                    xerr=[[0],[(maxcap - optcap)]], fmt='-',
                    linestyle='None', capsize=8, capthick=3, color='orange')
                plt.annotate(str(maxdevi), (0.98*maxcap, max(values)/3.9), color='orange', fontsize=11)
                plt.plot([optcap*avgdevi]*2, [0, 1.5 * max(values)], linewidth=3, color='green')
                plt.annotate("average", (optcap*avgdevi, 1.52 * max(values)), color='green')
                plt.title("Output distribution of alg. for {} nodes, {} iterations".format(nnodes,its))
                plt.xlabel("Needed capital [1]")
                plt.ylabel("Occurrence [1]")
                plt.show()

        elif type == 's': #scatter
            for s in range(setstart, setend+1):
                set = s

                txsfile = TXS_DIR + "randomtxs_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)
                scoredata = OUT_DIR + "scores_{}n_{}txs_set{}_its{}.data".format(nnodes,ntxs,set,its)
                outputfile = OUT_DIR + "scores_{}n_{}txs_set{}.data".format(nnodes,ntxs,set)

                trees, capitals = scoredatareadtrees(scoredata)
                optcap = min(capitals)
                opttree = capitals.index(optcap)

                lines = ff.readfile(scoredata)

                resulttree = []
                ncheckedtrees = []

                for line in lines:
                    if len(line) >1:
                        resulttree.append(int(line[0]))
                        nct = re.findall(r'\d+',line[len(line)-1])[1]
                        ncheckedtrees.append(int(nct))

                for rt, nct in list(zip(resulttree,ncheckedtrees)):
                    if rt == opttree:
                        plt.scatter(capitals[rt], nct, color='red')
                    else:
                        plt.scatter(capitals[rt], nct, color='blue')

                plt.show()

    elif CMD == "acc": # accuracy
        import os
        files = os.listdir("./" + OUT_DIR)
        yacc = []
        xnodes = []
        for file in files:
            nnodes = re.findall(r'\d+', file)[0]
            xnodes.append(int(nnodes))

            find = "accuracy:"
            pos, line = ff.searchinfile("./" + OUT_DIR + file, find)
            acc = re.findall(r'\d+', line)[0]
            yacc.append(int(acc)) 

        minxy = []
        done = []
        for n in xnodes:
            if n not in done:
                acc = [yacc[i] for i in range(len(xnodes)) if n == xnodes[i]]
                minxy.append((n,min(acc)))
                done.append(n)

        minxy = sorted(minxy, key=lambda x:x[0])
        minyacc = [x[1] for x in minxy]
        minxnodes = [x[0] for x in minxy]
        plt.plot(minxnodes, minyacc, label="min. accuracy")
        plt.xlabel("Number of nodes [1]")
        plt.ylabel("Accuracy [%]")
        plt.title("Minimal accuracy of all sets")
        plt.show()

    elif CMD == "medges": # marked edges 
        import os
        files = os.listdir("./" + OUT_DIR)
        
        xnodes = []
        markingmax = []
        for file in files:
            nnodes = re.findall(r'\d+', file)[0]
            xnodes.append(int(nnodes))
            
            lines = ff.readfile("./" + OUT_DIR + file)

            markingrounds = []

            for line in lines:
                if len(line) >1:
                    mr = re.findall(r'\d+',line[len(line)-1])[0]
                    markingrounds.append(int(mr))

            markingmax.append(max(markingrounds))

        markingfrac = []
        for me, n in list(zip(markingmax, xnodes)):
            m = (n-1) #number of edges
            frac = (me/m)
            plt.scatter(n, frac,  color='blue')

        plt.title("The question of termination")
        plt.ylabel("Number of markings / number of egdes [1]")
        plt.xlabel("Number of nodes [1]")
        plt.show()

    elif CMD == "analysis":
        para = ["<number of nodes>", "<number of transactions>",
                "<starting set>", "<ending set>","<iterations>"]
        opt = ["<type>"]

        nnodes,ntxs,setstart,setend,its,type = parse(para, opt)

        if type == "me":
            for s in range(setstart, setend+1):
                set = s
                print("Set {}".format(set))

                scoredata = OUT_DIR + "scores_{}n_{}txs_set{}_its{}.data".format(nnodes,ntxs,set,its)

                # load the optimal tree
                outputtree, capitals = scoredatareadtrees(scoredata)

                thresholdit = []
                thresholdnotit = []

                find = "Counter"
                lines= ff.readfile(scoredata)
                for line in lines:
                    if len(line) > 3 and find in line[3]:
                        dic = re.findall(r'{.+?}', line[3])
                        json_accept = dic[0].replace("'", "\"")
                        markededges = json.loads(json_accept)
                        treeindex = int(line[0])
                        # c = Counter(dic)                
                        for me in markededges:
                            if me in outputtree[treeindex]:
                                thresholdit.append(markededges[me])
                            else:
                                thresholdnotit.append(markededges[me])

                print("Edges in tree:")
                print("marked min: {}".format(min(thresholdit)))
                print("marked max: {}".format(max(thresholdit)))
                if len(thresholdnotit) > 0:
                    print("Edges NOT in tree:")
                    print("marked min: {}".format(min(thresholdnotit)))
                    print("marked max: {}".format(max(thresholdnotit)))

                data = max(thresholdit) * [set]
                plt.hist(data, bins=[set,set + 0.25,set+0.5],color='blue', edgecolor='black', linewidth=1)
                data = max(thresholdnotit) * [set+0.5]
                plt.hist(data, bins=[set,set + 0.25,set+0.5],color='red',edgecolor='black', linewidth=1)

            plt.title("How often the maximal marked edge was marked. for {} nodes".format(nnodes))
            plt.xlabel("Set number [1]")
            plt.ylabel("x times [1]")
            plt.show()

        elif type == "oc":
            for s in range(setstart, setend+1):
                set = s
                print("Set {}".format(set))

                scoredata = OUT_DIR + "scores_{}n_{}txs_set{}_its{}.data".format(nnodes,ntxs,set,its)

                # load the trees of socredata
                outputtree, capitals = scoredatareadtrees(scoredata)
                optC = min(capitals)
                index = capitals.index(optC)
                opttree = outputtree[index]

                listofoccurrence = []
                occurrencewrongedges = Counter()
                for tree in outputtree:
                    if tree == opttree:
                        continue
                    ocedges = [0] * len(opttree)
                    for e in tree:
                        if e in opttree:
                            i = opttree.index(e)
                            ocedges[i] = 1
                        else:
                            occurrencewrongedges.update([e])

                    listofoccurrence.append(copy.deepcopy(ocedges))

                for i,opte in enumerate(opttree,0):
                    oc = sum([x[i] for x in listofoccurrence])
                    print("edge: {}, occurrence: {}".format(opte, oc))

                print(occurrencewrongedges)

        else:
            print("{} unknown. Allowed opts: {}".format(type, opt))

    else:
        print("{} unknown. Allowed args: {}".format(CMD, args))

if __name__ == '__main__':
    main()