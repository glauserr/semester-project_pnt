#!/bin/python3

from subprocess import Popen
from subprocess import PIPE

# Popen(["create_node", "n0"], stdout=PIPE, stderr=PIPE)
# process = Popen("echo test".split(), stdout=PIPE)
# output, error = process.communicate()
# print(output, error)

# shell = None 
# env = None 
# stdin = None 
# timeout = None

# args = ["n0"]
# cmdline = '. ./{script} && {func} {args}'.format(
#     script=str("lnddocker.sh"),
#     func="create_node", args=' '.join("'{0}'".format(x) for x in args))

# print(cmdline)
# proc = Popen(cmdline, shell=True, executable=shell, env=env,
#                 stdout=PIPE, stderr=PIPE,
#                 stdin=PIPE if stdin else None)
# stdout, stderr = proc.communicate(input=stdin, timeout=timeout)
# print(stdout)

#########################

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

def format(ShellFuncReturn):
    R = ('\n', '\r', '\t')
    tmp = [x.decode("utf-8") for x in ShellFuncReturn[1:3]]
    for i,t in enumerate(tmp,0):
        for r in R:
            tmp[i] = tmp[i].replace(r,'')
    return [ShellFuncReturn[0]] +  tmp

# # rcode, out, err = cleanup()
# # print(out, err)
# # sleep(3000)

# rcode, out, err = test("frist", "second")
# print(out)

# # master node
def setup():
    rcode, out, err = format(create_node("nmaster"))
    # print("rcode: {}".format(rcode))
    print("out: {}".format(out))
    # print("err: {}".format(err))
    wait_till_node_ready("nmaster")

    rcode, address, err = format(create_newaddress("nmaster"))
    # print("rcode: {}".format(rcode))
    print("addr: {}".format(address))
    # print("err: {}".format(err))

    rcode, out, err = format(set_mining_address(address))
    # print("out:",out)
    # print("err:", err)
    rcode, out, err = mine_blocks(500)
    print("out:",out)
    # print("err:", err)
    wait_till_synchronized("nmaster")
    out = format(get_balance("nmaster"))
    print(out)


def star():
    N_NODES = 3
    nodes = list()

    for i in range(0, N_NODES):
        nodes.append("n{}".format(i))
        create_node(nodes[i])

    for node in nodes:
        # TODO: there is a problem when we have many nodes 
        wait_till_node_ready(node)
        connect_2nodes("nmaster", node)

    sleep(5)
    channels = []
    for node in nodes: 
        rcode, fdtx, err = format(open_channel("nmaster", node, 110000)) # 0.011 BTC
        channels.append(fdtx)
        mine_blocks(3)

    for node in nodes:
        send_payment("nmaster", node, 1000000) # 0.001 BTC
        # close_channel("nmaster", channels[node][0])
        mine_blocks(3)

if __name__ == "__main__":
    setup()
    star()
