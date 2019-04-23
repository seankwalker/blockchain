from blockchain import *
"""
    main.py

    Name:  Sean Walker
    NetID: skw34

    CPSC 310, Spring 2019
    Homework 4

    Main driver program for blockchain simulation.
"""


# difficulty of network
NET_DIFF = 4


if __name__ == "__main__":

    g_network = Network(NET_DIFF)   # generator node
    h_network = Network(NET_DIFF)   # honest node
    d_network = Network(NET_DIFF)   # dishonest node
    j_network = Network(NET_DIFF)   # joiner node

    # generator broadcasts to honest and dishonest nodes
    g_network.add_node("0.0.0.0", 7777)
    g_network.add_node("0.0.0.0", 8888)

    # honest broadcasts to generator and dishonest nodes
    h_network.add_node("0.0.0.0", 6666)
    h_network.add_node("0.0.0.0", 8888)

    # dishonest broadcasts to generator and honest nodes
    d_network.add_node("0.0.0.0", 6666)
    d_network.add_node("0.0.0.0", 7777)

    # joiner node is (one-way) neighbor to all other nodes
    j_network.add_node("0.0.0.0", 6666)
    j_network.add_node("0.0.0.0", 7777)
    j_network.add_node("0.0.0.0", 8888)

    g_node = NodeServer("0.0.0.0", 6666, g_network)
    h_node = NodeServer("0.0.0.0", 7777, h_network)
    d_node = NodeServer("0.0.0.0", 8888, d_network, dishonest=True)
    j_node = NodeServer("0.0.0.0", 9999, j_network)

    threads = [
        threading.Thread(target=g_node.start),
        threading.Thread(target=h_node.start),
        threading.Thread(target=d_node.start),
        threading.Thread(target=j_node.start)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
