from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/refresh", methods=["POST"])
def refresh():
    url = request.json["url"]
    requests.post("http://localhost:5001/parse", json={"url": url})
    return jsonify({"refreshed": url})

if __name__ == "__main__":
    app.run(port=6000)
