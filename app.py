from flask import Flask, jsonify, request, abort
app = Flask(__name__)

import random

from functools import wraps

import os

#Setup database connection
from pymongo import MongoClient

#db_uri = os.getenv("MONGODB_URI", 'mongodb://0.0.0.0:27017/rosa_database')#Used on heroku
client = MongoClient('mongodb://db:27017/rosa_database')

#client = MongoClient(db_uri)# Used on Heroku
db = client.get_database()
complaint = db['complaint']

#Setup api key and decorator
APPKEY_HERE = os.getenv("ROSA_CRUD_KEY", 'ROSABOT')

# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and request.args.get('key') == APPKEY_HERE:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


@app.route("/")
def root_page():
    return "ROSABOT"

def get_random_id():
    return random.randint(10000, 99999)

def get_new_id():
    random_id = get_random_id()
    while complaint.find_one({"_id": random_id}):
        random_id = get_random_id()
        
    new_id = complaint.insert_one({"_id": random_id}).inserted_id
    
    return new_id


@app.route("/complaint/create", methods=['GET'])
@require_appkey
def complaint_new():
    new_id = get_new_id()
    return str(new_id)


@app.route("/complaint/list")
@require_appkey
def complaint_list():
    id_list = list()

    for c_obj in complaint.find():
         id_list.append(c_obj['_id'])

    return jsonify(id_list)


@app.route("/complaint/update/<int:complaint_id>", methods=['POST'])
@require_appkey
def complaint_update(complaint_id):
    request_json = request.get_json()
    
    if request_json == None:
        return jsonify({'error':"No valid JSON body sent."})

    complaint_obj = complaint.find_one({"_id": complaint_id})
    if complaint_obj == None:
        return jsonify({'error':"Complaint id not found."})
        
    complaint.update_one({'_id': complaint_id}, {'$set': request_json})

    return jsonify({'status':"updated"})


@app.route("/complaint/status/<int:complaint_id>", methods=['GET'])
@require_appkey
def complaint_status(complaint_id):

    complaint_obj = complaint.find_one({"_id": complaint_id})

    if complaint_obj == None:
        return jsonify({'error':"Complaint id not found."})

    return jsonify(complaint_obj)



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
