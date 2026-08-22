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

@app.route("/api/price-history")
def price_history():
    try:
        with open("database/price_history.json", "r", encoding="utf-8") as file:
            history_data = json.load(file)

        return jsonify(history_data)


    except FileNotFoundError:
        return jsonify({}) 

@app.route("/api/price-drops")
def price_drops():
    try:
        with open(
            "database/price_history.json",
            "r",
            encoding="utf-8"
        ) as file:
            history_data = json.load(file)

        drops = []

        for product_name, history in history_data.items():

            if len(history) < 2:
                continue

            previous_price = float(
                history[-2]["price"].replace("£", "")
            )

            current_price = float(
                history[-1]["price"].replace("£", "")
            )

            if current_price < previous_price:

                drops.append({
                    "name": product_name,
                    "previous_price": history[-2]["price"],
                    "current_price": history[-1]["price"],
                    "saved": round(
                        previous_price - current_price,
                        2
                    )
                })

        return jsonify({
            "count": len(drops),
            "drops": drops
        })

    except (FileNotFoundError, json.JSONDecodeError):

        return jsonify({
            "count": 0,
            "drops": []
        }) 

if __name__ == "__main__":
    app.run(debug=True) 