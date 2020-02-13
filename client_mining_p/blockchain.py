import hashlib
import json
import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    # Initialize the Blockchain object
    def __init__(self):
        # Assign an empty array to chain
        self.chain = []
        # Ditto for current_transactions
        self.current_transactions = []
        # Assign nodes to an empty set()
        self.nodes = set()
        # Create the genesis block and pass in previous_hash + proof
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        # Create a block object
        block = {
            # Assign index to the length of chain + 1
            "index": len(self.chain) + 1,
            # Assign the time.time() method to timestamp
            "timestamp": time.time(),
            # Assign current transactions to transactions
            "transactions": self.current_transactions,
            # Assign proof to proof
            "proof": proof,
            # Assign previous hash or last element of chain [-1] to previous hash
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions by assining an empty array
        self.current_transactions = []
        # Append the block to the chain
        self.chain.append(block)
        # Return the new block
        return block

    def new_transaction(self, sender, recipient, amount):
        # Append sender, recipient, and amount to current_transactions in key/value format
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        # Return the last block ['index'] + 1 to create new index which will hold transaction
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # Use json.dumps to convert block(arg) into a string & assign to string_object - add sort_keys=True to make sure it comes in correct order
        string_object = json.dumps(block, sort_keys=True)
        # Use .encode to convert string object into a bytes format and assign to block_string
        block_string = string_object.encode()
        # Use hashlib.sha256 .method to convert block_string(arg) into a hash and assign to hash_object
        hash_object = hashlib.sha256(block_string)
        # Use hexdigest .method to convert hash_object into a string
        hash_string = hash_object.hexdigest()
        # Return the hashed string
        return hash_string

    @staticmethod
    def valid_proof(last_proof, proof):
        # Encode the two proof arguments into bytes and assign to guess
        guess = f"{last_proof}{proof}".encode()
        # Use the sha256 library on (guess) , run .hexdigest method, and assign to guess_hash
        guess_hash = hashlib.sha256(guess).hexdigest()
        # Return a guess_hash with six leading zeroes for exacalated difficulty
        return guess_hash[:6] == "000000"

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        "last_block": blockchain.last_block
    }
    return jsonify(response), 200

@app.route('/mine', methods=['POST'])
def mine():
    # Assign json formatted request to values
    values = request.get_json()
    # Assign required fields to required
    required = ['proof', 'id']
    # If we don't have all the required values...
    if not all(v in values for v in required):
        # Create an error message and assign to response
        response = {'message': 'You are missing some values.'}
        # Return jsonify-ed response and 400 status
        return jsonify(response), 400
    # Assign the get value 'proof' to submitted proof
    submitted_proof = values.get('proof')
    # Assign blockchain's last block to last_block
    last_block = blockchain.last_block
    # Convert the block to a string with JSON dumps
    last_block_string = json.dumps(last_block, sort_keys=True)
    # If comparing the last block string and submitted proof results in a valid proof...
    if blockchain.valid_proof(last_block_string, submitted_proof):
        # Hash the last block to get previous hash and assign as such
        previous_hash = blockchain.hash(last_block)
        # Assign the new_block to block and pass submitted proof + hash
        block = blockchain.new_block(submitted_proof, previous_hash)
        # Specify what we want from the response in object format
        response = {
            "message": "New Block Forged",
            "index": block["index"],
            "transactions": block["transactions"],
            "proof": block["proof"],
            "previous_hash": block["previous_hash"]
        }
        # Return the jsonify-ed response with 200 status
        return jsonify(response), 200
    else:
        response = { "message": "Sorry, you got beat to the punch" }
        return jsonify(response), 200

# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
