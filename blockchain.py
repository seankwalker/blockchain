import json
import secrets
import hashlib
import time


'''
Network

Constructor
'''
class Network():


    '''
    ___init___

    initialize the blockchain network

    - { int } difficulty - the proof of work difficulty in the network

    returns None (implicit object return)
    '''
    def __init__( self, difficulty ):
        self.chain      = []
        self.difficulty = difficulty

        # TODO: Fill out with address information for other nodes
        self.directory = [
            { 'ip' : None, 'port' : None }
        ]


    '''
    add_block

    add a block to the chain

    - { Block } block - block to add

    returns Bool
    '''
    def add_block( self, block ):
        # if genesis block, just add directly
        if len( self.chain ) == 0 and block.index == 0:
            self.chain.append( block )

            return True

        # check that new block is valid and child of current head of the chain
        if self.validate( block, self.chain[ -1 ] ):
            self.chain.append( block )

            return True

        return False


    '''
    validate

    validate the correctness of a block

    - { Block } block  - block to be checked
    - { Block } parent - parent block to be checked against

    returns Bool
    '''
    def validate( self, block, parent ):
        # TODO: Validate whether a received block is legitimate. You'll need five different checks here.
        #   1. Has something to do with the timestamp.
        #   2. Has something to do with the hash.
        #   3. Has something else to do with the hash.
        #   4. Has something to do with the parent.
        #   5. Has something else to do with the parent.

        return # a boolean denoting whether the block is valid


    '''
    validate_chain

    validate the correctness of the full chain

    returns Bool
    '''
    def validate_chain( self ):
        # TODO: Validate whether the the full chain is legitimate (whether each block is individually legitimate).

        return # a boolean denoting whether the chain is valid


    '''
    add_node

    add a new node to the directory

    returns None
    '''
    def add_node( self, ip, port ):
        self.directory.append( { 'ip' : ip, 'port' : port } )

        return None


    '''
    serialize

    serialize the chain into a format for sharing over the wire

    returns String or Bytes
    '''
    def serialize( self ):
        # TODO: Come up with a way to encode the full chain for sharing with new nodes who join the network. JSON may be useful here.

        return # a string or bytestring


    '''
    deserialize

    deserialize the chain from the wire and store

    returns None
    '''
    def deserialize( self, chain_repr ):
        # TODO: Reverse the behavior of serialize.

        return None


    '''
    __str__

    string representation of the full chain for printing

    returns String
    '''
    def __str__( self ):
        sc = '\nNo. of Blocks: {l}\n'.format( l = len( self.chain ) )

        offset = len( str( len( self.chain ) ) )
        for i, block in enumerate( self.chain ):
            sc += '\tBlock {n}. {h}\n'.format( n = str( i ).rjust( offset ), h = str( block ) )

        sc += '\n'

        return sc


'''
Block

Constructor
'''
class Block():


    '''
    ___init___

    initialize a block

    - { int } index  - the block index in the chain
    - { str } parent - the hash of the parent block
    - { str } data   - the data to be inserted into the block

    returns None (implicit object return)
    '''
    def __init__( self, index, parent, data ):
        self.index       = index
        self.parent_hash = parent
        self.data        = data  # NB: You're welcome to put anything or nothing into the chain.

        self.hashed      = False


    '''
    hash

    mine a (valid) hash for the block

    - { int } difficulty - the difficulty to be met, from the network

    returns String
    '''
    def hash( self, difficulty ):
        # TODO: Implement hashing of block until difficulty is exceeded.
        #       Use the SHA256 hash function (from hashlib library).
        #       The hash should be over the index, hash of parent, a unix epoch timestamp in elapsed seconds (time.time()), a random nonce (from secrets library) and the data.
        #       We will refer to all of these contents except the data as a "header".
        #       It is recommended that you store and use the hex representation of the hash, from hash.hexdigest().
        #
        # HINTS
        #
        #       "[U]ntil difficulty is exceeded" means at least the specified number of leading zeros are present in the
        #       hash as the "proof of work." You'll have to keep hashing with different nonces till you get one that works.
        #
        #       You may query the random nonce once and increment it each try.

        self.timestamp = '{ some timestamp }'
        self.nonce     = '{ some nonce }'
        self.hash      = '{ some hash }'

        self.hashed = True

        return self.hash


    '''
    __str__

    string representation of the block for printing

    returns String
    '''
    def __str__( self ):
        return self.hash


'''
generate

generate (mine) a new block

TODO: Determine input(s) and output(s).
'''
def generate():
    # TODO: Create new block.
    pass


'''
genesis

generate (mine) the genesis block

returns None
'''
def genesis():
    genesis = Block( 0, '0', 'Genesis Block' )
    genesis.hash( network.difficulty )

    network.add_block( genesis )

    return None


'''
broadcast

broadcast mined block to network

TODO: Determine input(s) and output(s).
'''
def broadcast():
    # TODO: Broadcast newly generated block to all other nodes in the directory.
    pass


'''
query_chain

query the current status of the chain

TODO: Determine input(s) and output(s).
'''
def query_chain():
    # TODO: Request content of chain from all other nodes (using deserialize class method). Keep the majority/plurality (valid) chain.
    pass


'''
listen_broadcast

listen for broadcasts of new blocks

TODO: Determine input(s) and output(s).
'''
def listen_broadcast():
    # TODO: Handle newly broadcast prospective block (i.e. add to chain if valid).
    #       If using HTTP, this should be a route handler.
    pass


'''
listen_query

list for requests for current chain status

TODO: Determine input(s) and output(s).
'''
def listen_query():
    # TODO: Respond to query for contents of full chain (using serialize class method).
    #       If using HTTP, this should be a route handler.
    pass




if __name__ == '__main__':
    # hoist the network up to the global context
    # makes it easier to use with both tcp/http
    global network
    network = Network( 4 )
