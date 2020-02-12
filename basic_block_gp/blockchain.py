import hashlib
import json
import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the block to the chain
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string - add sort_keys to make sure it comes in correct order
        string_object = json.dumps(block, sort_keys=True)
        # Use .encode to convert string into a bytes format
        block_string = string_object.encode()
        # Use hashlib.sha256 to create a hash
        hash_object = hashlib.sha256(block_string)
        # Use hexdigest to convert to a string
        hash_string = hash_object.hexdigest()
        # Return the hashed string
        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Simple Proof of Work Algorithm
        Stringify the block and look for a proof.
        Loop through possibilities, checking each one against `valid_proof`
        in an effort to find a number that is a valid proof
        :return: A valid proof for the provided block
        """
        # Stringify the last block, sort keys in right direction
        string_object = json.dumps(self.last_block, sort_keys=True)
        # Assign zero to proof so we have something to increment
        proof = 0
        # While the valid proof is false (incomplete)...
        while self.valid_proof(string_object, proof) is False:
            # Try again (increment by 1)
            proof += 1
        # Return the proof
        return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # Convert guess to a string and encode into bytes
        guess = f"{block_string}{proof}".encode()
        # Convert string to a hash and back to a string
        guess_hash = hashlib.sha256(guess).hexdigest()
        # Confirm we went 3 leading zeroes and return (true or false)
        result = True if guess_hash[:3] == "000" else False
        return result

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    # Run the proof of work algorithm to get the next proof
    proof = blockchain.proof_of_work(last_proof)
    # Create a hash for last_block of blockchain and assign to previous_hash
    previous_hash = blockchain.hash(blockchain.last_block)
    # Assign new_block, including proof and previous hash, to block
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "We mined a new block!",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"]
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
