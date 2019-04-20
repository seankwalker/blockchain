"""
    blockchain.py

    Name:  Sean Walker
    NetID: skw34

    CPSC 310, Spring 2019
    Homework 4

    Implements logic for an HTTP blockchain.
"""

import json
import secrets
import hashlib
import time
from itertools import takewhile
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import threading
import urllib.parse as urlparse
import copy
import random
from collections import Counter


# data in the blockchain, just for fun
DATA_MESSAGES = ["hello, world", "yolo",
                 "cpsc 310 for life", "https://youtu.be/dQw4w9WgXcQ"]


class BlockchainEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Network:
    def __init__(self, difficulty):
        """
        initialize the blockchain network requiring `difficulty` leading 0s
        """
        self.chain = []
        self.difficulty = difficulty
        self.directory = []

    def add_block(self, block):
        """
        add `block` to the chain
        """
        # if genesis block, just add directly
        if len(self.chain) == 0 and block.index == 0:
            self.chain.append(block)
            print("appended genesis block!")
            return True

        # check that new block is valid and child of current head of the chain
        if self.validate(block, self.chain[-1]):
            self.chain.append(block)
            print("appended non-genesis block!")
            return True

        print("rejected block")
        return False

    def check_hash(self, block):
        """
        returns hash of `block` with difficulty of this network
        """

        iterations = 0
        while True:
            # keep working on a nonce until we get one exceeding the difficulty
            header = str(block.index).encode("utf-8") + b" " + \
                str(block.parent_hash).encode("utf-8") + \
                b" " + str(block.timestamp).encode("utf-8") + \
                b" " + str(int(block.nonce) + iterations).encode("utf-8")

            hash_attempt = hashlib.sha256(
                header+b" "+str(block.data).encode("utf-8")).hexdigest()

            num_leading_zeroes = sum(
                1 for _ in takewhile("0".__eq__, str(hash_attempt)))

            if num_leading_zeroes > self.difficulty:
                break
            iterations += 1

        return hash_attempt

    def validate(self, block, parent):
        """
        validate the correctness of `block` against `parent`
        """
        if not self.check_hash(block) == block.hash_val:
            # block's stored hash matches
            return False

        if (block.hash_val[:self.difficulty] !=
                "".join(["0" for _ in range(self.difficulty)])):
            # block's hash has the required number of zerores
            return False

        if parent is not None:
            # checks for non-genesis blocks (parent required)
            if block.timestamp < parent.timestamp:
                # block must have been created after its parent
                return False

            if parent.hash_val != block.parent_hash:
                # block's stored hash of its parent should match the parent
                # block's hash
                # n.b. the parent's hash is verified to be valid of its stored
                # hash since it is part of the chain, thus `validate` approved
                # it before
                return False

            if block.index != parent.index+1:
                # block should immediately follow its parent in the chain
                return False

        return True

    def validate_chain(self):
        """
        validate the correctness of the full chain
        """
        if not self.validate(self.chain[0], None):
            # genesis block
            return False
        for parent_idx, block in enumerate(self.chain[1:]):
            # remainder of chain
            if not self.validate(block, self.chain[parent_idx]):
                return False

        return True

    def add_node(self, ip, port):
        """
        add a new node to the directory
        """
        self.directory.append({"ip": ip, "port": port})

    def serialize(self):
        """
        serialize the chain into a format for sharing over the wire
        """
        return bytes(BlockchainEncoder().encode(self.chain), "utf-8")

    def deserialize(self, chain_repr):
        """
        deserialize the chain from the wire and store
        """
        list_of_param_dicts = json.JSONDecoder().decode(str(chain_repr,
                                                            "utf-8"))
        chain = []
        for params in list_of_param_dicts:
            block_params = {"index": int(params["index"]),
                            "data": params["data"],
                            "parent_hash": params["parent_hash"],
                            "hash_val": params["hash_val"],
                            "nonce": int(params["nonce"]),
                            "timestamp": float(params["timestamp"])}
            chain.append(Block(from_dict=block_params))

        return chain

    def __str__(self):
        """
        string representation of the full chain for printing
        """
        sc = "\nNo. of Blocks: {l}\n".format(l=len(self.chain))

        offset = len(str(len(self.chain)))
        for i, block in enumerate(self.chain):
            sc += "\tBlock {n}. {h}\n".format(
                n=str(i).rjust(offset), h=str(block))

        sc += "\n"

        return sc


class Block:
    def __init__(self, index=None, parent_hash=None, data=None, from_dict=None):
        """
        initialize a block containing `data` at `index` in the chain with
        `parent` as its parent block
        """
        if from_dict is not None:
            self.index = from_dict["index"]
            self.parent_hash = from_dict["parent_hash"]
            self.data = from_dict["data"]
            self.hash_val = from_dict["hash_val"]
            self.nonce = from_dict["nonce"]
            self.timestamp = from_dict["timestamp"]
        else:
            self.index = index
            self.parent_hash = parent_hash
            self.data = data

    def hash(self, difficulty):
        """
        mine a (valid) hash for the block with more than `difficulty` leading 0s
        """
        self.timestamp = time.time()
        self.nonce = secrets.randbits(30)

        iterations = 0
        while True:
            # keep working on a nonce until we get one exceeding the difficulty
            header = str(self.index).encode("utf-8") + b" " + \
                str(self.parent_hash).encode("utf-8") + \
                b" " + str(self.timestamp).encode("utf-8") + \
                b" " + str(int(self.nonce) + iterations).encode("utf-8")

            hash_attempt = hashlib.sha256(
                header+b" "+str(self.data).encode("utf-8")).hexdigest()

            num_leading_zeroes = sum(
                1 for _ in takewhile("0".__eq__, str(hash_attempt)))

            if num_leading_zeroes > difficulty:
                print(f"difficult-enough nonce found! {self.nonce}")
                break
            iterations += 1

        self.hash_val = hash_attempt
        return self.hash_val

    def __str__(self):
        """
        string representation of the block for printing
        """
        return self.hash_val


class Node(BaseHTTPRequestHandler):
    def __init__(self, network, ip, port, dishonest, *args):
        self.dishonest = dishonest
        self.ip = ip
        self.network = network
        self.port = port
        self.server_version = "JoanCoin"
        self.sys_version = "0.1.0"
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        self.log_request()
        self.log_message(f"port: {self.port}")
        endpoint = urlparse.urlparse(self.path).path
        if endpoint == "/query":
            # query request
            self.listen_query()
        else:
            self.send_response(404, "no such endpoint")
            self.end_headers()

    def do_HEAD(self):
        self.log_request()
        self.log_message(f"port: {self.port}")
        endpoint = urlparse.urlparse(self.path).path
        if endpoint == "/broadcast":
            # broadcast request
            self.listen_broadcast()
        elif endpoint == "/generate":
            # mine a block
            self.generate()
        elif endpoint == "/genesis":
            # mine genesis block
            self.genesis()
        elif endpoint == "/pull":
            # get valid chain from neighbors
            self.query_chain()
        else:
            self.send_response(404, "no such endpoint")
            self.end_headers()

    def generate(self):
        """
        generate (mine) a new block
        add mined block to this Node's chain
        broadcast mine block to Node's Network
        """
        if len(self.network.chain) == 0:
            print(
                "`generate` called, but chain is nonexistant;",
                "delegating to `genesis`...")
            self.genesis()
            return

        block = Block(self.network.chain[-1].index+1,
                      self.network.chain[-1].hash_val,
                      random.choice(DATA_MESSAGES))

        # mine block
        block.hash(self.network.difficulty)

        # add block to this Node's chain and send it to all other Nodes in
        # network
        self.network.add_block(block)
        self.broadcast(block)

    def genesis(self):
        """
        generate (mine) the genesis block
        """
        genesis = Block(0, "0", "Genesis Block")

        # mine genesis block
        genesis.hash(self.network.difficulty)
        self.network.add_block(genesis)
        self.broadcast(genesis)

    def broadcast(self, block):
        """
        broadcast mined block to network
        """
        for node in self.network.directory:
            print(f"broadcasted block to {node['ip']}:{node['port']}")
            r = requests.head(("http://" + node["ip"] + ":" + str(node["port"])
                               + "/broadcast"),
                              params={"data": block.data,
                                      "hash_val": block.hash_val,
                                      "index": block.index,
                                      "nonce": block.nonce,
                                      "parent_hash": block.parent_hash,
                                      "timestamp": block.timestamp})

    def query_chain(self):
        """
        query the current status of the chain from neighbors and update this
        node's chain to be the longest of all neighbors' valid chains
        """
        chain_counter = Counter()
        for node in self.network.directory:
            r = requests.get("http://" + node["ip"] + ":" +
                             str(node["port"]) + "/query")

            deserialized_chain = self.network.deserialize(r.content)
            if deserialized_chain:
                self.network.chain = deserialized_chain
                if (self.network.validate_chain()):
                    chain_counter[tuple(self.network.chain)] += 1

        self.network.chain = chain_counter.most_common(1)[0][0]

    def listen_broadcast(self):
        """
        listen for broadcasts of new blocks
        """
        self.send_response(200)
        self.end_headers()

        rec_params = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        block_params = {"index": int(rec_params["index"][0]),
                        "data": rec_params["data"][0],
                        "parent_hash": rec_params["parent_hash"][0],
                        "hash_val": rec_params["hash_val"][0],
                        "nonce": int(rec_params["nonce"][0]),
                        "timestamp": float(rec_params["timestamp"][0])}

        if self.dishonest:
            # ignore everything besides the genesis block
            if block_params["index"] != 0:
                return

        rec_block = Block(from_dict=block_params)
        print(f"received block on {self.ip}:{self.port}: {rec_block}")
        self.network.add_block(rec_block)

    def listen_query(self):
        """
        list for requests for current chain status
        """
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(self.network.serialize())


class NodeServer:
    def __init__(self, ip, port, network, dishonest=False):
        self.network = network

        def handler(*args):
            Node(self.network, ip, port, dishonest, *args)

        self.node_server = HTTPServer((ip, port), handler)

    def start(self):
        self.node_server.serve_forever()
