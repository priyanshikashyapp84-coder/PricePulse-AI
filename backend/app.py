from flask import Flask, jsonify, send_from_directory 
from flask_cors import CORS
import json
import os

app = Flask(__name__)


FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend"
)
CORS(app)


@app.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename) 

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "scraper": "connected"
    })


@app.route("/api/products")
def products():
    with open("database/products.json", "r", encoding="utf-8") as file:
        product_data = json.load(file)

    return jsonify({
        "count": len(product_data),
        "products": product_data
    }) 


if __name__ == "__main__":
    app.run(debug=True) 