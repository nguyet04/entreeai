from flask import Flask, jsonify, request, make_response
from pprint import pprint
import os, mysql.connector, requests, json

# from spellchecker import SpellChecker
app = Flask(__name__)

interpreterURL = "http://34.217.35.254/parse"
# if __name__ == '__main__':
#     app.run(debug=False, host='0.0.0.0')

print(os.environ["MYSQL_ROOT_PASSWORD"])

# currdb = pymysql.connect(
# 	host = "127.0.0.1",
# 	user = "root",
# 	password = os.environ['MYSQL_ROOT_PASSWORD'],
# 	db = "entreeai",
# 	cursorclass = pymysql.cursors.DictCursor
# )

def connection():
    conn = mysql.connector.connect(
		host = "flaskdb",
		user = 'root',
		password = os.environ["MYSQL_ROOT_PASSWORD"],
		database = 'entreeai',
		auth_plugin='mysql_native_password'
	)

    c = conn.cursor()
    return c , conn

# currdb = pymysql.connect(
# 	host='flaskdb', port=3306, user='root', 
# 	passwd=os.environ["MYSQL_ROOT_PASSWORD"], db='entreeai'
# )



mycursor, conn = connection()



@app.route("/", methods=["GET", "POST"])
def otherstuff():
	if request.method == "GET":
		return "methodone"
	elif request.method == "POST":
		return "methodtwo"


def fetch(data):
    print(requests.post(interpreterURL, data=data).content)	

def insertIntoMenuDatabase():
	insertFood = "INSERT INTO food (food_name) values (%s)"	
	insertIngredient = "INSERT INTO ingredient (ingredient_name) values (%s)"	

	insertIngredients = ""
	insertUnits = ""
	print("lol")
	with open('menu.json') as toLoad: 
		menu = json.load(toLoad)
		pprint(menu)
		for item in menu["food"]:
			print(insertFood % item["name"])
			mycursor.execute(insertFood, item["name"])
			conn.commit()
			newestRowID = mycursor.lastrowid()
			mycursor.executemany(insertIngredient, item["ingredients"])
			conn.commit()
			print(mycursor.rowcount())





insertIntoMenuDatabase()

# def fetch(toInterpret):
# 	with request.post(interpreterURL, data = toInterpret) as rq:
# 		body = rq.text
# 		if rq.status_code != 200: 
# 			print("Non-valid response code")
# 			res = make_response("Bad Request", 400)
# 			return
# 		print("now we're cookin good lookin")
# 		res = make_response("Success", 200)
# 		print(body)
# 		# Headers, if any, go here.

# def sentenceCleaner(inputString):
# 	strList = inputString.split()
# 	spell = SpellChecker()
# 	fullList = [""] * len(strList)
# 	for i, word in enumerate(strList):
# 		if spell.correction(word):
# 			fullList[i] = spell.correction(word)
# 		else: 
# 			fullList[i] = word
		
# 	cleanSentence = " ".join(word for word in fullList)
# 	return cleanSentence

# fetch("Pizza dough, mozzarella cheese, mushrooms")