import os, sys, hashlib, json

import pymongo
from pymongo import MongoClient, ReturnDocument

def hash_pass(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'0', 1)

if __name__ == "__main__":
    assert len(sys.argv) >= 3, "You must provide a 'login' and 'password'"

    username = sys.argv[1]
    password = hash_pass(sys.argv[2])

    db_uri = os.getenv("MONGODB_URI", 'mongodb://localhost:27017/rosa_database') 
    client = MongoClient(db_uri)
    db = client.get_database()
    users = db['users']

    user = users.find_one({"username": username})
    if user == None:
        users.insert_one({"username": username, "password": password})
        print("Created!")
    else:
        print("User already exists!")
