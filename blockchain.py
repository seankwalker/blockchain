import json
import secrets
import hashlib
import time
from itertools import takewhile
from http.server import BaseHTTPRequestHandler, HTTPServer


class Network():
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
        # TODO: Validate whether a received block is legitimate. You"ll need five different checks here.
        #   1. Has something to do with the timestamp.
        #   2. Has something to do with the hash.
        #   3. Has something else to do with the hash.
        #   4. Has something to do with the parent.
        #   5. Has something else to do with the parent.

        if parent is None:
            # genesis block
            pass
        else:
            pass

        return  # a boolean denoting whether the block is valid

    def validate_chain(self):
        """
        validate the correctness of the full chain
        """
        # TODO: Validate whether the the full chain is legitimate (whether each block is individually legitimate).
        if not self.validate(self.chain[0], None):
            return False
        for block_num, block in enumerate(self.chain[1:]):
            if not self.validate(block, self.chain[block_num-1]):
                return False

        return True

    def add_node(self, ip, port):
        """
        add a new node to the directory
        """
        self.directory.append({"ip": ip, "port": port})

        return None

    def serialize(self):
        """
        serialize the chain into a format for sharing over the wire
        """
        # TODO: Come up with a way to encode the full chain for sharing with new nodes who join the network. JSON may be useful here.
        o = json.JSONEncoder().encode(self.chain)
        print(o)
        return  # a string or bytestring

    def deserialize(self, chain_repr):
        """
        deserialize the chain from the wire and store
        """
        # TODO: Reverse the behavior of serialize.
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


class Block():
    def __init__(self, index, parent, data):
        """
        initialize a block containing `data` at `index` in the chain with
        `parent` as its parent block
        """
        self.index = index
        self.parent_hash = parent
        # NB: You"re welcome to put anything or nothing into the chain.
        self.data = data

        self.hashed = False

    def hash(self, difficulty):
        """
        mine a (valid) hash for the block with more than `difficulty` leading 0s
        """
        # TODO: Implement hashing of block until difficulty is exceeded.
        #       Use the SHA256 hash function (from hashlib library).
        #       The hash should be over the index, hash of parent, a unix epoch timestamp in elapsed seconds (time.time()), a random nonce (from secrets library) and the data.
        #       We will refer to all of these contents except the data as a "header".
        #       It is recommended that you store and use the hex representation of the hash, from hash.hexdigest().
        #
        # HINTS
        #
        #       "[U]ntil difficulty is exceeded" means at least the specified number of leading zeros are present in the
        #       hash as the "proof of work." You"ll have to keep hashing with different nonces till you get one that works.
        #
        #       You may query the random nonce once and increment it each try.

        self.timestamp = time.time()
        self.nonce = secrets.token_byes()

        iterations = 0
        while True:
            # keep working on a nonce until we get one exceeding the difficulty
            header = str(self.index).encode("utf-8") + b" " + str(self.parent_hash).encode("utf-8") + \
                b" " + str(self.timestamp).encode("utf-8") + \
                b" " + str(self.nonce + iterations).encode("utf-8")

            hash_attempt = hashlib.sha256(
                header+b" "+str(self.data).encode("utf-8")).hexdigest()

            num_leading_zeroes = sum(
                1 for _ in takewhile("0".__eq__, str(hash_attempt)))

            if num_leading_zeroes > difficulty:
                print(f"difficult-enough nonce found! {nonce}")
                break
            iterations += 1

        self.hash = hash_attempt
        self.hashed = True

        return self.hash

    def __str__(self):
        """
        string representation of the block for printing
        """
        return self.hash


class Node(BaseHTTPRequestHandler):
    def generate():
        """
        generate (mine) a new block
        TODO: Determine input(s) and output(s).
        """
        pass

    def genesis():
        """
        generate (mine) the genesis block
        """
        genesis = Block(0, "0", "Genesis Block")
        genesis.hash(network.difficulty)

        network.add_block(genesis)

        return None

    def broadcast():
        """
        broadcast mined block to network
        """
        # TODO: Broadcast newly generated block to all other nodes in the directory.
        pass

    def query_chain():
        """
        query the current status of the chain
        """
        # TODO: Request content of chain from all other nodes (using deserialize class method). Keep the majority/plurality (valid) chain.
        pass

    def listen_broadcast():
        """
        listen for broadcasts of new blocks
        """
        # TODO: Handle newly broadcast prospective block (i.e. add to chain if valid).
        #       If using HTTP, this should be a route handler.
        pass

    def listen_query(self):
        """
        list for requests for current chain status
        """
        # TODO: Respond to query for contents of full chain (using serialize class method).
        #       If using HTTP, this should be a route handler.
        pass

    def do_GET(self):
        if self.path == "/query":
            listen_query(self)
        elif self.path == "/broadcast":

        else:
            self.send_error(400, "invalid endpoint")


if __name__ == "__main__":
    # hoist the network up to the global context
    # makes it easier to use with both tcp/http
    global network
    network = Network(4)
