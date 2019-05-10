from flask import Flask, jsonify, request, make_response
from pprint import pprint
from difflib import SequenceMatcher
import os, mysql.connector, requests, json


# from spellchecker import SpellChecker
app = Flask(__name__)

API_KEY = "https://nlu.entree.ai/staging/parse"
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
		food.food_id, \
		food.food_name, \
		other_names.fo_name, \
		food.price \
		FROM other_names \
		INNER JOIN food ON other_names.food_id = food.food_id \
		WHERE food_name = %s \
		OR fo_name = %s"
	shakequery = "SELECT \
		food.food_id, \
		food.food_name, \
		other_names.fo_name, \
		food.price, \
		flavors.flavor_name \
		FROM other_names \
		INNER JOIN food ON other_names.food_id = food.food_id \
		INNER JOIN flavors on other_names.food_id = flavors.food_id \
		WHERE (food_name = %s OR fo_name = %s) \
		AND flavor_name = %s"
	foundFoods = []
	missingFoods = []
	for item in dataArr:
		print("Food Name", item["name"])
		item["name"] = str.lower(item["name"])
		print("52, ITEM NAME", item["name"])
		if "shake" in item["name"]:
			shake_item = item["name"].split()
			print("SHAKE_ITEM", shake_item)
			if len(shake_item) > 1:
				print("PRINT SHAKE", shakequery % (shake_item[1], shake_item[1], shake_item[0]))
				mycursor.execute(shakequery, (shake_item[1], shake_item[1], item[0],))
			elif len(item["nested"]) > 0:
				print("PRINT OTHER SHAKE", shakequery % (shake_item[1], shake_item[1], item["nested"][0]))
				mycursor.execute(shakequery, (shake_item[1], shake_item[1], item["nested"][0],))
			else:
				mycursor.execute(shakequery, (shake_item[1], shake_item[1], "vanilla",))
			result = mycursor.fetchone()
			shakeItemString = " ".join(shake_item)
			if result is None:
				missingFoods.append(shakeItemString)
			else:
				newFood = {}
				newFood["food_name"] = result[4] + " " + result[1]
				newFood["price"] = result[3]
				print("NEW SHAKE FOOD", newFood)
		elif item["brand"] is not None and (item["name"] == "soda" or item["name"] == "pop"):
			item["brand"] = str.lower(item["brand"])
			print("SODA WITH BRAND", query % (item["name"], item["brand"]))
			mycursor.execute(query, (item["name"], item["brand"],))
			if result is None:
				missingFoods.append(shakeItemString)
			else:
				newFood = {}
				if result[2] is not None:
					newFood["food_name"] = result[2]
				else:
					newFood["food_name"] = result[1]
				newFood["price"] = result[3]
				print(newFood)
				foundFoods.append(newFood)
		else:
			print("FOOD W ", query % (item["name"], item["name"]))
			mycursor.execute(query, (item["name"], item["name"],))
			result = mycursor.fetchone()
			if result is None:
				missingFoods.append(item["name"])
			else: 
				newFood = {}
				print("FOUND FOOD", result)
				if result[1] == "soda" and result[1] is not None:
					newFood["food_name"] = result[2]
				elif result[1] == "soda" or result[2] == "pop":
					newFood["food_name"] = "coke"
				else:	
					newFood["food_name"] = result[1]
				newFood["food_price"] = result[3]
				print("food price", result[3])
				foundFoods.append(newFood)
		# pprint(newFood)
	print("FINDING ALL:", foundFoods)
	print("MISSING FOOD", missingFoods)
	return foundFoods

def insertIntoMenuDatabase():
	insertFood = "INSERT IGNORE INTO food (food_name, price) values (%s, %s)"
	insertOtherName = "INSERT IGNORE INTO other_names (fo_name, food_id) values (%s, %s)"
	insertUnit = "INSERT IGNORE INTO units (unit_name, price, food_id) values (%s, %s, %s)"
	insertFlavor = "INSERT IGNORE INTO flavors (flavor_name, food_id) values (%s, %s)"

	with open('dicks.json') as toLoad:
		menu = json.load(toLoad)
		for item in menu["food"]:
			try:
				print(insertFood % (item["name"],item["price"]))
				mycursor.execute(insertFood, (item["name"], item["price"]))
				newestRowID = mycursor.lastrowid
				print(newestRowID)
				for other_name in item["other_names"]:
					print(insertOtherName % (other_name, newestRowID))
					mycursor.execute(insertOtherName, (other_name, newestRowID, ))
				if "units" in item:
					for unit in item["units"]:
						print(insertUnit % (unit["name"], unit["price"], newestRowID))
						mycursor.execute(insertUnit, (unit["name"], unit["price"], newestRowID,))
				if "flavors" in item:
					for flav in item["flavors"]:
						print(insertFlavor % (flav, newestRowID))
						mycursor.execute(insertFlavor, (flav, newestRowID,))
			except mysql.connector.Error as error:
				print("Unsuccessful inserting records into database, time to rolback: {}".format(error))
				conn.rollback()
			conn.commit()

insertIntoMenuDatabase();

def fetch(stringInput):
	return requests.post(API_KEY, json={"data": stringInput}).json()
findIntent(fetch("I want a plain burger and a fanta"))

# insertIntoMenuDatabase()


# @app.before_first_request
# def activate_job():
# 	insertIntoMenuDatabase()


# @app.route("/v1/flask/test")
# def test():
# 	return 'Hello World!'

# @app.route("/v1/flask/item", methods=["POST"])
# def item_check():
# 	print("1", request.get_json())
# 	request.get_json()
# 	utterance = request.get_json()["order_utterance"]
# 	parsedUtterance = json.loads(fetch(utterance))
# 	print(parsedUtterance)
# 	finalResult = jsonify(findIntent(parsedUtterance))
# 	print(finalResult)
# 	return finalResult



# if __name__ == '__main__':
#     app.run(host="flaskapp", port=80, debug=False)
