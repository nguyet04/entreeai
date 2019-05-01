from flask import Flask, jsonify, request, make_response
from pprint import pprint
from difflib import SequenceMatcher
import os, mysql.connector, requests, json


# from spellchecker import SpellChecker
app = Flask(__name__)

interpreterURL = "http://34.217.35.254/parse"
def connection():
    conn = mysql.connector.connect(
		host = "flaskdb",
		user = 'root',
		password = os.environ["MYSQL_ROOT_PASSWORD"],
		database = 'entreeai',
		auth_plugin = 'mysql_native_password'
	)

    c = conn.cursor()
    return c , conn

mycursor, conn = connection()

def findIntent(dataArr):
	print("DATAARR", dataArr)
	allFoods = []
	query = "SELECT \
		food_name, \
		ingredient_name \
		FROM food_ingredient fi \
		INNER JOIN  food f ON f.food_id = fi.food_id \
		INNER JOIN  ingredients i ON i.ingredient_id = fi.ingredient_id \
		WHERE food_name = %s"
	for item in dataArr:
		newFood = {}
		print("Food", item["food"])
		item["food"] = str.lower(item["food"])
		if item["food"].endswith("es"):
			item["food"] = item["food"][:len(item["food"])-1]
		elif item["food"].endswith("s"):
			item["food"] = item["food"][:len(item["food"])]
		newFood["food_name"] = item["food"]

		print(query % item["food"])
		mycursor.execute(query, (item["food"],))
		result = mycursor.fetchall()
		foundIngredients = []
		missingIngredients = []
		for orderIng in item["ingredients"]:
			size = len(foundIngredients)
			for ing in result:
				print("FIRST ING", ing)
				print(item["ingredients"])
				if SequenceMatcher(None, ing[1], orderIng).ratio() > 0.7:
					foundIngredients.append(ing[1])
					break
			if len(foundIngredients) == size:
				missingIngredients.append(orderIng)


		newFood["found_ingredients"] = foundIngredients
		newFood["not_found_ingredients"] = missingIngredients
		allFoods.append(newFood)
		# pprint(newFood)
	print("FINDING ALL:", allFoods)	
	return allFoods

def insertIntoMenuDatabase():
	insertFood = "INSERT INTO food (food_name) values (%s)"	
	insertIngredient = "INSERT INTO ingredients (ingredient_name) values (%s)"	
	insertFoodIng = "INSERT INTO food_ingredient (food_id, ingredient_ID) values (%s, %s)"
	insertUnit = "INSERT IGNORE INTO units (unit_name) values (%s)"	
	insertFoodUnit = "INSERT INTO food_units (food_id, unit_id, price) values (%s, %s, %s)"
	with open('menu.json') as toLoad: 
		menu = json.load(toLoad)
		# pprint(menu)
		for item in menu["food"]:
			try: 
				mycursor.execute(insertFood, (item["name"],))
				conn.commit()
				newestRowID = mycursor.lastrowid
				for ing in item["ingredients"]:
					mycursor.execute(insertIngredient, (ing,))
					conn.commit()
					newestIngID = mycursor.lastrowid
					mycursor.execute(insertFoodIng, (newestRowID, newestIngID,))				
					conn.commit()
				for unit in item["units"]: 
					mycursor.execute(insertUnit, (unit["unit"],))
					conn.commit()
					newestUnitID = mycursor.lastrowid
					mycursor.execute(insertFoodUnit, (newestRowID, newestUnitID, unit["price"],))
			except mysql.connector.Error as error:
				print("Unsuccessful inserting records into database, time to rolback: {}".format(error))
				conn.rollback()

def fetch(stringInput):
	return requests.post('http://34.217.35.254/parse', data=stringInput).content

# insertIntoMenuDatabase()


@app.before_first_request
def activate_job():
	insertIntoMenuDatabase()


@app.route("/v1/flask/test")
def test():
	return 'Hello World!'

@app.route("/v1/flask/item", methods=["POST"])
def item_check():
	print("1", request.get_json())
	request.get_json()
	utterance = request.get_json()["order_utterance"]
	parsedUtterance = json.loads(fetch(utterance))
	print(parsedUtterance)
	finalResult = jsonify(findIntent(parsedUtterance))
	print(finalResult)
	return finalResult



if __name__ == '__main__':
    app.run(host="flaskapp", port=80, debug=False)
