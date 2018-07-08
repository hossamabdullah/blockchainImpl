# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 22:01:57 2018

@author: HossamEldeen
"""
#importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#part 1 - building a blockchain
class Blockchain:
    
    def __init__(self):
            self.chain = []
            self.create_block(proof = 1, previous_hash = '0', transactions= [])
            self.nodes = set()

    def mine(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = self._try_nonce(proof= new_proof, prev_proof= previous_proof)
            if hash_operation[:4] == '0000':
                check_proof = True
                break
            new_proof += 1
        return new_proof
    
    def create_block(self, proof, previous_hash, transactions):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash, 
                 'transactions': transactions}
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self._hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = self._try_nonce(proof = proof, prev_proof = previous_proof)
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
        return True
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def add_transaction(self, transactions,  sender, receiver, amount):
        transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        return transactions

    def _hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def _try_nonce(self, proof, prev_proof):
        return hashlib.sha256(str(proof**2 -  prev_proof**2).encode()).hexdigest()
    
    def _get_chain(self, node):
        response = requests.get(f'http://{node}/get_chain')
        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['chain']
        return (chain, length)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            chain, length = self._get_chain(node)
            if length > max_length and self.is_chain_valid(chain):
                longest_chain = chain
                max_length = length
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
#part 2 - Mining our Blockchain
app = Flask(__name__)

node_address = str(uuid4()).replace('-', '')
# node_address = "http://127.0.0.1:5000"

blockchain = Blockchain()
transactions = []

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    global transactions
    prev_block = blockchain.get_previous_block()
    
    prev_proof = prev_block['proof']
    proof = blockchain.mine(previous_proof= prev_proof)
    prev_block_hash = blockchain._hash(prev_block)
    transactions = blockchain.add_transaction(transactions, sender=node_address, receiver='Hadelin', amount=1)
    block = blockchain.create_block(proof=proof , previous_hash=prev_block_hash, transactions=transactions)
    
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200


@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}    
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {'is_valid': blockchain.is_chain_valid(blockchain.chain)}
    return jsonify(response), 200

@app.route('/add_trans', methods=['POST'])
def add_transaction():
    global transactions
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return "some transaction keys are missing", 400
    
    previous_block = blockchain.get_previous_block()
    index = previous_block['index'] + 1
    transactions = blockchain.add_transaction(transactions, json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201

#part3- decentralizing our blockchain
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    
    for node in nodes:
        blockchain.add_node(node)
    response = {"message": "Nodes added correctly, here are all nodes", "list": list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/check_chains', methods=['GET'])
def check_chains():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        message = {'message': 'another longer chain found',
                    'mew_chain': blockchain.chain}
    else:
        message = {'message': 'Good for you',
                    'actual_chain': blockchain.chain}
    return jsonify(message), 200

    
app.run(host= '0.0.0.0', port= 5002)