from flask import Flask, request, jsonify
import json
import urllib.request
import uuid
import random
from flask_cors import cross_origin, CORS
import requests
import dateutil.parser

app = Flask(__name__)


@app.route("/findfoodbanks", methods=["GET"])
@cross_origin()
def find_food_banks():
	postcode = request.args.get("postcode")
	with urllib.request.urlopen(f"https://www.givefood.org.uk/api/2/foodbanks/search/?address={postcode}") as url:
		data = json.loads(url.read().decode())

	new_data = []
	import random
	headers = {
		"Authorization": '563492ad6f917000010000015c451fa13b65484e93b2a3aab6691039'

	}
	params = {
		"query": "charity",
		"per_page": 100,
		"page": 3
	}
	response = requests.get("http://api.pexels.com/v1/search", headers=headers, params=params)
	image_data = response.json()

	for x in data:
		d = {"name": x["name"], "location": x["address"], "needs": x["needs"], "phone": x["phone"],
		     "url": x["urls"]["homepage"], "priority": generate_priority(x["name"]), "lat": x["lat_lng"].split(",")[0], "lon":x["lat_lng"].split(",")[1], "distance":x["distance_m"]}

		i = image_data["photos"][random.randint(0,50)]["src"]["medium"]
		d["image"] = i
		new_data.append(d)

	return jsonify(new_data)


def validate_date(date_text):
    try:
        dateutil.parser.parse(date_text)
    except ValueError:
        return False
    else:
        return True


@app.route("/donate", methods=["POST"])
@cross_origin()
def donate():
	data = request.json

	if not validate_date(data['info']['dateTime']):
		return jsonify({200: "success"}) 

	data["status"] = "Pending"
	data["donationid"] = str(uuid.uuid1())
	headers = {
		"Authorization": '563492ad6f917000010000015c451fa13b65484e93b2a3aab6691039'
	}
	params = {
		"query": "person",
		"per_page": 100,
		"page": 3
	}
	response = requests.get("http://api.pexels.com/v1/search", headers=headers, params=params)
	image_data = response.json()

	with urllib.request.urlopen("http://api.postcodes.io/postcodes/"+data["postcode"]) as url:
		post_code_data = json.loads(url.read().decode())
	data["start_lat"] = post_code_data["result"]["latitude"]
	data["start_lon"] = post_code_data["result"]["longitude"]

	with open("donations.json", "r") as f:
		donations = json.load(f)

	username = data["username"]
	if username not in donations:
		i = image_data["photos"][random.randint(0,50)]["src"]["medium"]
		donations[username] = {"image":  i, "donations": [] }

	donations[username]["donations"].append(data)

	with open("donations.json", "w") as f:
		json.dump(donations, f)

	return jsonify({200: "success"})


@app.route("/userdonations", methods=["GET"])
@cross_origin()
def donations():
	username = request.args.get("username")

	with open("donations.json", "r") as f:
		donations = json.load(f)

	return jsonify({"data": donations[username]})


@app.route("/getalldonations", methods=["GET"])
@cross_origin()
def get_all_donations():
	with open("donations.json", "r") as f:
		donations = json.load(f)

	all_donations = []
	for k, v in donations.items():
		for items in v["donations"]:
			if items["status"] in ("Pending", "InProgress"):
				all_donations.append(items)

	return jsonify({"data": all_donations})


@app.route("/changestatus", methods=["GET"])
@cross_origin()
def change_donation_status():
	data = request.json
	donation_id = request.args.get("donationid")
	status = request.args.get("status")
	with open("donations.json", "r") as f:
		donations = json.load(f)

	for k, v in donations.items():
		for items in v["donations"]:
			if items["donationid"] == donation_id:
				items["status"] = status

	with open("donations.json", "w") as f:
		json.dump(donations, f)

	return jsonify({200: "success"})


@app.route("/purgedatabase")
@cross_origin()
def purge_database():
	with open("donations.json", "w") as f:
		json.dump("{}", f)


def generate_priority(name):
	if ord(name[0]) % 3 == 0:
		return "High"
	elif ord(name[0]) % 3 == 1:
		return "Medium"
	else:
		return "Low"


def main():
	cors = CORS(app)
	app.config['CORS_HEADERS'] = 'Content-Type'
	app.run(debug=True)
	app.run(threaded=True, port=5000)


if __name__ == "__main__":
	main()
