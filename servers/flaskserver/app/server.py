from flask import Flask, jsonify, request, make_response
from pprint import pprint
import os, mysql.connector, requests, json

# from spellchecker import SpellChecker
app = Flask(__name__)

interpreterURL = "http://34.217.35.254/parse"
# if __name__ == '__main__':
#     app.run(debug=False, host='0.0.0.0')

print(os.environ["MYSQL_ROOT_PASSWORD"])

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

mycursor, conn = connection()



@app.route("/", methods=["GET", "POST"])
def otherstuff():
	if request.method == "GET":
		return "methodone"
	elif request.method == "POST":
		return "methodtwo"


def fetch(data):
    return json.loads(requests.post(interpreterURL, data=data).content)

def insertIntoMenuDatabase():
	insertFood = "INSERT INTO food (food_name) values (%s)"	
	insertIngredient = "INSERT INTO ingredients (ingredient_name) values (%s)"	
	insertFoodIng = "INSERT INTO food_ingredient (food_id, ingredient_ID) values (%s, %s)"
	insertUnit = "INSERT IGNORE INTO units (unit_name) values (%s)"	
	insertFoodUnit = "INSERT INTO food_units (food_id, unit_id, price) values (%s, %s, %s)"
	with open('menu.json') as toLoad: 
		menu = json.load(toLoad)
		pprint(menu)
		for item in menu["food"]:
			try: 
				print(insertFood % item["name"])
				mycursor.execute(insertFood, (item["name"],))
				conn.commit()
				newestRowID = mycursor.lastrowid
				print(newestRowID)
				for ing in item["ingredients"]:
					print(insertIngredient % ing)
					mycursor.execute(insertIngredient, (ing,))
					conn.commit()
					newestIngID = mycursor.lastrowid
					print(newestIngID)
					print(insertFoodIng % (newestRowID, newestIngID))
					mycursor.execute(insertFoodIng, (newestRowID, newestIngID,))				
					conn.commit()
				for unit in item["units"]: 
					print(unit)
					print(unit["unit"], unit["price"])
					print(insertUnit % unit["unit"])
					mycursor.execute(insertUnit, (unit["unit"],))
					conn.commit()
					newestUnitID = mycursor.lastrowid
					print(insertFoodUnit % (newestRowID, newestUnitID, unit["price"]))
					mycursor.execute(insertFoodUnit, (newestRowID, newestUnitID, unit["price"],))
			except mysql.connector.Error as error:
				print("Unsuccessful inserting records into database, time to rolback: {}".format(error))
				conn.rollback()
		
insertIntoMenuDatabase()
fetch("Pizza dough, mozzarella cheese, mushrooms")

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

