from flask import Flask, request, jsonify
import json
import urllib.request


app = Flask(__name__)


@app.route("/findfoodbanks", methods=["GET"])
def find_food_banks():
    postcode = request.args.get("postcode")
    with urllib.request.urlopen(f"https://www.givefood.org.uk/api/2/foodbanks/search/?address={postcode}") as url:
        data = json.loads(url.read().decode())
    return jsonify(data)


@app.route("/donate", methods=["POST"])
def donate():
    data = request.json
    print(data)

    with open("donations.json", "r") as f:
        donations = json.load(f)

    username = data["username"]
    if username not in donations:
        donations[username] = []
    
    donations[username].append(data)

    with open("donations.json", "w") as f:
        json.dump(donations, f)

    return jsonify({200: "success"})


@app.route("/donations", methods=["GET"])
def donations():
    username = request.args.get("username")

    with open("donations.json", "r") as f:
        donations = json.load(f)

    return jsonify({"data": donations[username]})


def main():
    app.run(threaded=True, port=5000)


if __name__ == "__main__":
    main()
