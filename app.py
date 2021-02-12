from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route("/bruh")
def bruhbruh():
    return "bruh"


def main():
    app.run(threaded=True, port=5000)


if __name__ == "__main__":
    main()
