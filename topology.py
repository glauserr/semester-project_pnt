#!/bin/python3

import sys
from time import sleep

import shellfuncs

# from lnddocker import test
with shellfuncs.config(shell='/bin/bash'):
    from lnddocker import list_channels
    from lnddocker import create_node
    from lnddocker import create_newaddress
    from lnddocker import set_mining_address
    from lnddocker import mine_blocks
    from lnddocker import connect_2nodes
    from lnddocker import open_channel
    from lnddocker import cleanup
    from lnddocker import get_balance
    from lnddocker import send_payment
    from lnddocker import close_channel
    from lnddocker import wait_till_node_ready
    from lnddocker import wait_till_synchronized
    from lnddocker import wait_till_connected
    from lnddocker import cleanup
    from lnddocker import is_open

import genrandomtxs as txsfile


def format(ShellFuncReturn):
    R = ('\n', '\r', '\t')
    tmp = [x.decode("utf-8") for x in ShellFuncReturn[1:3]]
    for i, t in enumerate(tmp, 0):
        for r in R:
            tmp[i] = tmp[i].replace(r, '')
    return [ShellFuncReturn[0]] + tmp


class Network():
    nodes = []
    network = {}  # {n1: {channels: [{n2:dkkd, id:2943}]}
    tmpl_channels = {"channels": []}
    tmpl_entry = {"target_node": "", "capital": 0, "id": ""}

    def __init__(self, n_nodes):
        self.init_master()
        self.init(n_nodes)

    def init_master(self):
        print("clean up... ", end="")
        cleanup()
        print("Done")

        init = "initializing master node... "
        print(init)
        rcode, out, err = format(create_node("nmaster"))
        print(" node: {}".format(out))
        wait_till_node_ready("nmaster")

        rcode, address, err = format(create_newaddress("nmaster"))
        print(" addr: {}".format(address))

        set_mining_address(address)
        mine_blocks(500)

        wait_till_synchronized("nmaster")
        out = format(get_balance("nmaster"))
        print(" balance: {}".format(out[1]))

    def init(self, n_nodes):
        print("creating {} nodes... ".format(n_nodes))
        self.createnodes(n_nodes)
        print(self.nodes)
        new_channels = list()
        new_payments = list()
        for node in self.nodes:
            new_channels.append(("nmaster", node, 1100000))
            new_payments.append(("nmaster", node, 1000000))
        print("connecting nodes to master...")
        self.connectnodes([(c[0], c[1]) for c in new_channels])
        print("opening channels to master...")
        self.openchannels(new_channels)
        print("send payment to nodes...")
        self.sendpayments(new_payments)
        print("closing channels to master")
        self.closechannels([(c[0], c[1]) for c in new_channels])
        print("initialization DONE")

    def createnodes(self, n_nodes, name=None):
        startindex = 0
        prefix = name
        if prefix == None:
            startindex = len(self.nodes)
            prefix = "n"

        endindex = startindex + n_nodes

        for i in range(startindex, endindex):
            if name != None and i == 0:
                n_name = name
            else:
                n_name = prefix + "{}".format(i)

            create_node(n_name)
            self.nodes.append(n_name)

    def connectnodes(self, list_args):
        # [ (n1, n2), (), ..]
        for src, target in list_args:
            wait_till_node_ready(src)
            wait_till_node_ready(target)
            connect_2nodes(src, target)

    def openchannels(self, list_args):
        # [ (n1, n2, capital), (), ..]
        for src, target, capital in list_args:
            wait_till_connected(src, target)
            wait_till_synchronized(src)
            wait_till_synchronized(target)
            rc, fdtx, err = format(open_channel(src, target, capital))
            mine_blocks(3)
            if format(is_open(src, fdtx))[1] == "true":
                entry = self.tmpl_entry.copy()
                entry['target_node'] = target
                entry['capital'] = capital
                entry['id'] = fdtx

                if src not in self.network:
                    self.network.update({src: self.tmpl_channels.copy()})

                self.network[src]['channels'].append(entry)

    def closechannels(self, list_args):
        # [ (src, target), (), ..]
        for src, target in list_args:
            channels = self.network[src]['channels']
            entry = next(
                (item for item in channels if item["target_node"] == target), {})

            if entry != {}:
                close_channel(src, entry['id'])
                self.network[src]['channels'].remove(entry)
            else:
                print("remove failed: {}".format(entry))

        mine_blocks(3)

    def sendpayments(self, list_args):
        # [ (src, target, amount), (), ..]
        retVal = list()
        for src, target, amount in list_args:
            rc, state, err = format(send_payment(src, target, amount))
            if state == "successful":
                retVal.append(True)
            else:
                retVal.append(False)

        return retVal


class Star(Network):
    N_NODES = 30

    def __init__(self):
        print("creating star topology...")
        super().__init__(N_NODES)


if __name__ == "__main__":
    Network(3)
