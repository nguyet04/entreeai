from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
from flask import Flask, request, g, jsonify, abort, make_response, current_app
from bson.json_util import dumps

from pymongo import MongoClient
DB_URL = 'mongodb://127.0.0.1:27017/'

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"


@app.route("/todo", methods=["GET", "POST"])
def todos():
	if request.method == "GET":
		return "TBD"
	elif request.method == "POST":
		return "TBD"
	else:
		abort(405)


@app.route("/todo/<int: todoid>", methods=["GET", "PUT", "DELETE"])
def todo():
	return "TBD"


def get_db():
	if not hasattr(current_app, "db"):
		print("Connecting to MongoDB")
		db = MongoClient(DB_URL)
		current_app.db = db["todos"]

	return current_app.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()