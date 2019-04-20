import json
import secrets
import hashlib
import time
from itertools import takewhile
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import threading
from urllib.parse import parse_qs, urlparse


class ChainEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Network:
    def __init__(self, difficulty):
        """
        initialize the blockchain network requiring `difficulty` leading 0s
        """
        self.chain = []
        self.difficulty = difficulty

        # TODO: Fill out with address information for other nodes
        self.directory = [
            {"ip": None, "port": None}
        ]

    def add_block(self, block):
        """
        add `block` to the chain
        """
        # if genesis block, just add directly
        if len(self.chain) == 0 and block.index == 0:
            self.chain.append(block)
            return True

        # check that new block is valid and child of current head of the chain
        if self.validate(block, self.chain[-1]):
            self.chain.append(block)
            return True

        return False

    def validate(self, block, parent):
        """
        validate the correctness of `block` against `parent`
        """
        # TODO: Validate whether a received block is legitimate.
        # You'll need five different checks here.
        #   1. Has something to do with the timestamp. <- later than the parent
        #   2. Has something to do with the hash.
        #   3. Has something else to do with the hash.
        #   4. Has something to do with the parent.
        #   5. Has something else to do with the parent.

        # checks on block
        if not block.hash(self.difficulty) == block.hash_val:
            # block's stored hash matches
            return False

        if (block.hash_val[self.difficulty:] !=
                [0 for _ in range(self.difficulty)]):
            # block's hash has the required number of zerores
            return False

        if parent is not None:
            # checks for non-genesis blocks (parent required)
            if block.timestamp < parent.timestamp:
                # block must have been created after its parent
                return False

            if not block.hash(self.difficulty) == block.hash_val:
                # block's stored hash matches
                return False

            if (block.hash_val[self.difficulty:] !=
                    [0 for _ in range(self.difficulty)]):
                # block's hash has the required number of zerores
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
        for block_num, block in enumerate(self.chain[1:]):
            # remainder of chain
            if not self.validate(block, self.chain[block_num-1]):
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
        return bytes(ChainEncoder().encode(self.chain), "utf-8")

    def deserialize(self, chain_repr):
        """
        deserialize the chain from the wire and store
        """
        return json.JSONDecoder().decode(chain_repr)

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
    def __init__(self, index, parent, data):
        """
        initialize a block containing `data` at `index` in the chain with
        `parent` as its parent block
        """
        self.index = index
        self.parent_hash = parent
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
            header = str(self.index).encode("utf-8") + b" " + str(self.parent_hash).encode("utf-8") + \
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
    def __init__(self, network, *args):
        print(f"__init__ called on {self}")
        self.network = network
        self.server_version = "JoanCoin"
        self.sys_version = "0.1.0"
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        print(f"received GET request: {self.request}")
        endpoint = urlparse(self.path).path
        if endpoint == "/broadcast":
            # broadcast request
            self.listen_broadcast()
        elif endpoint == "/genesis":
            # mine genesis block
            self.genesis()
        elif endpoint == "/query":
            # query request
            self.listen_query()
        else:
            self.send_response(404, "no such endpoint")
            self.end_headers()

    def generate(self):
        """
        generate (mine) a new block
        add mined block to this Node's chain
        broadcast mine block to Node's Network
        TODO: Determine input(s) and output(s).
        """
        block = Block(self.chain[-1].index, self.chain[-1].hash, None)

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

    def broadcast(self, block):
        """
        broadcast mined block to network
        """
        for node in self.network.directory:
            r = requests.get(node.ip + ":" + str(node.port) + "/broadcast",
                             params={"index": block.index,
                                     "parent_hash": block.parent_hash,
                                     "data": block.data
                                     })
            print(
                f"broadcasted block to {node.ip}: {node.port} | result: {r}")

    def query_chain(self):
        """
        query the current status of the chain
        """
        # TODO: Request content of chain from all other nodes (using deserialize
        # class method). Keep the majority/plurality (valid) chain.
        chains = []
        for node in self.network.directory:
            r = requests.get(node.ip + ":" + str(node.port) + "/query")
            print(f"{r}")

    def listen_broadcast(self):
        """
        listen for broadcasts of new blocks
        """
        # TODO: Handle newly broadcast prospective block (i.e. add to chain if valid).
        #       If using HTTP, this should be a route handler.
        print(f"`listen_broadcast`: received request")

        if "?" not in self.path:
            # invalid request
            self.send_response(400)
            self.end_headers()
            return

        query_string = self.path.split("?")[-1]
        try:
            params = parse_qs(query_string, max_num_fields=3)
        except ValueError:
            # invalid request (too many parameters)
            self.send_response(400)
            self.end_headers()
            return

        # params is a dictionary of query parameter to list (of length 1)
        # of the associated value

        block = Block(params["index"][0], params["parent"]
                      [0], params["data"][0])
        if self.chain:
            parent = self.chain[-1]
        else:
            parent = None
        block_is_valid = network.validate(block, parent)

        if block_is_valid:
            self.chain.append(block)

    def listen_query(self):
        """
        list for requests for current chain status
        """
        # TODO: Respond to query for contents of full chain (using serialize class method).
        #       If using HTTP, this should be a route handler.
        print(f"`listen_query`: received request {self.request}")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(self.network.serialize())


class NodeServer:
    def __init__(self, ip, port):
        self.network = Network(4)
        self.network.add_node(ip, port)

        def handler(*args):
            Node(self.network, *args)

        self.node_server = HTTPServer((ip, port), handler)

    def start(self):
        self.node_server.serve_forever()


if __name__ == "__main__":
    # start a new thread for each node
    node_a = NodeServer("0.0.0.0", 8888)
    # node_b = NodeServer("0.0.0.0", 9999)

    node_a.start()

    # thread_a = threading.Thread(target=node_a.start)
    # thread_b = threading.Thread(target=node_b.start)

    # thread_a.start()
    # thread_b.start()

    # thread_a.join()
    # thread_b.join()
