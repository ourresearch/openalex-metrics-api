import logging
import os
from flask import jsonify
from app import app
from flask_cors import CORS


logger = logging.getLogger("metrics-api")

CORS(app)

@app.route("/", methods=["GET"])
def base_endpoint():
    return jsonify({
        "msg": "Don't panic"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5106))
    app.run(host="0.0.0.0", port=port)
