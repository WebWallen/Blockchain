import hashlib
import requests
import sys
import json
import time

def proof_of_work(last_block):
        last_proof = json.dumps(last_block, sort_keys=True)
        # Assign 0 to proof so we have a variable to increment
        proof = 0
        while valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

def valid_proof(last_proof, proof):
        # Encode the two proof arguments into bytes and assign to guess
        guess = f"{last_proof}{proof}".encode()
        # Use the sha256 library on (guess) , run .hexdigest method, and assign to guess_hash
        guess_hash = hashlib.sha256(guess).hexdigest()
        # Return a guess_hash with six leading zeroes for exacalated difficulty
        return guess_hash[:6] == "000000"

if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()

    # Initialized a coins variable at 0 so people get paid for their proofs
    coins = 0

    # Run forever until interrupted
    while True:
        # Gets the last proof stored on our server with /last_block
        r = requests.get(url=node + "/last_block")
        # breakpoint()
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: Get the block from `data` and use it to look for a new proof
        start_time = time.time()
        new_proof = proof_of_work(data['last_block'])
        end_time = time.time()
        print(f'Time to mine coin: {end_time - start_time} seconds')
        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": id}

        r = requests.post(url=node + "/mine", json=post_data)
        
        try: 
            data = r.json()
        except ValueError:
            print("Error: Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: If the server responds with a 'message' 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        if data.get('message') == 'New Block Forged':
            coins += 1
            print(f"Number of coins mined: {coins}")
        else:
            print(data.get('message'))