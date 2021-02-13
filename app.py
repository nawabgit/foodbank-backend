from flask import Flask, request, jsonify
import json
import urllib.request
import uuid

app = Flask(__name__)


@app.route("/findfoodbanks", methods=["GET"])
def find_food_banks():
	postcode = request.args.get("postcode")
	with urllib.request.urlopen(f"https://www.givefood.org.uk/api/2/foodbanks/search/?address={postcode}") as url:
		data = json.loads(url.read().decode())

	new_data = []

	for x in data:
		d = {"name": x["name"], "location": x["address"], "needs": x["needs"], "phone": x["phone"],
		     "url": x["urls"]["homepage"], "priority": generate_priority(x["name"]), "lat_lon": x["lat_lng"]}
		new_data.append(d)

	return jsonify(new_data)


@app.route("/donate", methods=["POST"])
def donate():
	data = request.json

	data["status"] = "Pending"
	data["donationid"] = uuid.uuid1()

	with urllib.request.urlopen("http://api.postcodes.io/postcodes/"+data["postcode"]) as url:
		post_code_data = json.loads(url.read().decode())
	data["start_lat_lon"] = post_code_data["result"]["latitude"], post_code_data["result"]["longitude"]

	with open("donations.json", "r") as f:
		donations = json.load(f)

	username = data["username"]
	if username not in donations:
		donations[username] = []

	donations[username].append(data)

	with open("donations.json", "w") as f:
		json.dump(donations, f)

	return jsonify({200: "success"})


@app.route("/userdonations", methods=["GET"])
def donations():
	username = request.args.get("username")

	with open("donations.json", "r") as f:
		donations = json.load(f)

	return jsonify({"data": donations[username]})


@app.route("/getalldonations", methods=["GET"])
def get_all_donations():
	with open("donations.json", "r") as f:
		donations = json.load(f)

	all_donations = []
	for k, v in donations.items():
		if v["status"] == "Pending":
			all_donations += v

	return jsonify({"data": all_donations})


@app.route("/changestatus", methods=["POST"])
def change_donation_status():
	data = request.json
	donation_id = data["donationid"]
	status = data["status"]
	with open("donations.json", "r") as f:
		donations = json.load(f)

	for k, v in donations.items():
		if v["donationid"] == donation_id:
			v["status"] = status

	with open("donations.json", "w") as f:
		json.dump(donations, f)

	return jsonify({200: "success"})


def generate_priority(name):
	if ord(name[0]) % 3 == 0:
		return "High"
	elif ord(name[0]) % 3 == 1:
		return "Medium"
	else:
		return "Low"


def main():
	app.run(debug=True)
	app.run(threaded=True, port=5000)


if __name__ == "__main__":
	main()
