import requests
from flask import Flask, jsonify, request, make_response
app = Flask(__name__)


print("test123")
@app.route("/", methods=["GET", "POST"])
def otherstuff():
	if request.method == "GET":
		return "poo poo"
	elif request.method == "POST":
		return "tu tu"


	

def fetch(backToUser, toInterpret):
	interpreterURL = "http://34.217.35.254/parse"
	with request.post(interpreterURL, data = toInterpret) as rq:
		body = rq.text
		if rq.status_code != 200: 
			print("Non-valid response code")
			res = make_response("Bad Request", 400)
			return
		print("now we're cookin good lookin")
		res = make_response("Success", 200)
		res.body()
		# Headers, if any, go here.
