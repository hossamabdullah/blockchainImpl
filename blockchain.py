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
#part 2 - Mining our Blockchain