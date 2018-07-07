# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 22:01:57 2018

@author: HossamEldeen
"""
#importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

#part 1 - building a blockchain
class Blockchain:
    
    def __init__(self):
            self.chain = []
            self.create_block(proof = 1, previoud_hash = '0')
            
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 -  previous_proof**2).encode())
            if hash_operation[:4] == '0000':
                check_proof = True
                break
            new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
            
        
#part 2 - Mining our Blockchain