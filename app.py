# encoding=utf8

from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app) # CORS feature cover all routes in the app

import random
import math

from functools import wraps
from bson.json_util import dumps

import os
import io
import unicodecsv as csv

#Setup database connection
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId


db_uri = os.getenv("MONGODB_URI", 'mongodb://db:27017/rosa_database') 
#client = MongoClient('mongodb://db:27017/rosa_database')# used in docker deploy 

client = MongoClient(db_uri)
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
        
    new_id = complaint.insert_one({"_id": random_id, "status":"aberto", "observacao":{}}).inserted_id
    
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

@app.route("/complaint/search")
@require_appkey
def complaint_search():
    limit = 10
    page = 1
    start = 1

    args = {}
    search_term = request.args.get('search')
    if search_term is not None and search_term != '':
        args['$text'] = {'$search': str(request.args.get('search'))}

    if request.args.get('limit') is not None:
        limit = int(request.args.get('limit'))

    cursor = complaint.find(args)
    total = cursor.count(True)
    
    cursor = cursor.limit(limit)

    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
        if page > 1:
            start = (limit * (page - 1)) + 1
            cursor = cursor.skip(start)

    end = limit * page

    cursor.sort([
        ('anoassedio', pymongo.DESCENDING),
        ('datassedio', pymongo.DESCENDING)]
    )

    data = [row for row in cursor]

    json_return = {
        'total': total,
        'pages': math.ceil(float(total) / limit) if total > limit else 1,
        'items': data,
        'page': page,
        'start': start,
        'end': end,
        'limit': limit
    }

    return dumps(json_return)

@app.route("/complaint/csv", methods=['GET'])
@require_appkey
def complaint_csv():
    args = {}
    search_term = request.args.get('search')
    if search_term is not None and search_term != '':
        args['$text'] = {'$search': str(request.args.get('search'))}

    cursor = complaint.find(args)

    header = None
    items = []
    for item in cursor:
        if header is None:
            header = item.keys()
        row = [item[key] for key in header]
        items.append(row)

    csv_data = [header] + items

    dest = io.BytesIO()
    writer = csv.writer(dest)
    writer.writerows(csv_data)

    output = make_response(dest.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route("/complaint/update/<int:complaint_id>", methods=['GET', 'POST'])
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
