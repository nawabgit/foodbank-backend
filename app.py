from flask import Flask, request, jsonify
import requests
import json
import urllib.request


app = Flask(__name__)


@app.route("/findfoodbanks", methods=["GET"])
def find_food_banks():
    postcode = request.args.get("postcode")
    with urllib.request.urlopen(f"https://www.givefood.org.uk/api/2/foodbanks/search/?address={postcode}") as url:
        data = json.loads(url.read().decode())
    return jsonify(data)


def main():
    app.run(threaded=True, port=5000)


if __name__ == "__main__":
    main()