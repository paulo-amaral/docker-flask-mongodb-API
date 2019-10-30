#encoding=utf8

from flask import Flask, jsonify, request, abort, make_response, render_template, redirect
from flask_cors import CORS, cross_origin

import random

app = Flask(__name__)
app.secret_key = str(random.randint(0,999999999))
CORS(app) # CORS feature cover all routes in the app

import random
import math

from functools import wraps
from bson.json_util import dumps

import json

import os
import io
import unicodecsv as csv

#Setup database connection
import pymongo
from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId


#Authorization things
from create_user import hash_pass
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

logged_users = dict()


db_uri = os.getenv("MONGODB_URI", 'mongodb://localhost:27017/rosa_database') 
#client = MongoClient('mongodb://db:27017/rosa_database')# used in docker deploy 

client = MongoClient(db_uri)
db = client.get_database()
complaint = db['complaint']
counters = db['counters']
users = db['users']

#Setup api key and decorator
APPKEY_HERE = os.getenv("ROSA_CRUD_KEY", 'ROSABOT')


class RosaUser(UserMixin):
    def __init__(self, username):
        super().__init__()
        self._id = username.encode()
    def get_id(self):
        return self._id


@login_manager.user_loader
def load_user(user_id):
    return RosaUser(user_id.decode())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            return "Missing username and/or password."

        username = request.form['username']
        password = hash_pass(request.form['password'])

        user = users.find_one({"username": username})
        if user == None or user['password'] != password:
            return "Username or password wrong."
        
        login_user(RosaUser(username))

        return redirect("/logout")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        return redirect('/login')
    else:
        return render_template('logout.html')

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
    if current_user.is_authenticated:
        return redirect("/logout")
    else:
        return redirect("/login")

def get_random_id():
    return random.randint(10000, 99999)

def get_new_id():
    new_comp_id = get_new_inc_id()
    #Ensures non repeat id
    while complaint.find_one({"_id": new_comp_id}):
        new_comp_id = get_new_inc_id()
        
    new_id = complaint.insert_one({"_id": new_comp_id, "status":'', "observacao":''}).inserted_id
    
    return new_id

def get_new_inc_id():
    """Return a new incremental id, updating the last count in the database."""
    #return counters.find_one_and_update(
    #    {'_id': 'complaintid'},
    #    {'$inc': {'sequence_value': 1}},
    #    return_document=ReturnDocument.AFTER)['sequence_value']

    return int(counters.find_one_and_update(
        {'_id': 'complaintid'},
        {'$inc': {'sequence_value': 1}},
        return_document=ReturnDocument.AFTER)['sequence_value'])

@app.route("/complaint/create", methods=['GET']) 
@require_appkey
def complaint_new():
    new_id = get_new_id()
    return str(new_id)


@app.route("/complaint/list")
@login_required
@require_appkey
def complaint_list():
    id_list = list()

    for c_obj in complaint.find():
        if is_jsonable(c_obj):
            id_list.append(c_obj['_id'])

    return jsonify(id_list)



def is_jsonable(x):
    """
    Function to check if an object can dumped as json.
    Ensures API only returns valid objects and do not crashes.
    """
    try:
        json.dumps(x)
        return True
    except:
        return False

@app.route("/complaint/search")
@login_required
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
@login_required
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
            
        #row = [item[key] for key in header
        row = [item.get(key, " ") for key in header]
        items.append(row)

    csv_data = [header] + items
   
    dest = io.BytesIO()
    #writer = csv.writer(dest)
    writer = csv.writer(dest, delimiter=',') 
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
