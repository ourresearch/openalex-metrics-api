import logging
import os
from flask import jsonify, request
from app import app
from flask_cors import CORS

from models import MetricSet, Response
from metrics import get_latest_sample

logger = logging.getLogger("metrics-api")

CORS(app)

@app.route("/", methods=["GET"])
def base_endpoint():
    return jsonify({
        "msg": "Don't panic"
    })


@app.route("/recall", methods=["GET"])
def recall_endpoint():
    # return the latest metricset with type: "recall"
    metricset = MetricSet.query.filter_by(type="recall").order_by(MetricSet.date.desc()).first()
    return jsonify(metricset.to_dict())


@app.route("/field-match/<entity>", methods=["GET"])
def match_rates_endpoint(entity):
    # return the latest metricset with type: "match_rates"
    metricset = MetricSet.query.filter_by(type="field_match_rates", entity=entity).order_by(MetricSet.date.desc()).first()
    return jsonify(metricset.to_dict())

@app.route("/responses", methods=["GET"])
def responses_endpoint():
    page = int(request.args.get("page", 1))
    sample = get_latest_sample("works")
    
    if not sample or not sample.ids:
        return jsonify([])
    
    # Calculate pagination
    per_page = 100
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get the slice of IDs for this page
    page_ids = sample.ids[start_idx:end_idx]
    
    # Query responses matching these IDs
    responses_dict = {}
    responses = Response.query.filter(Response.id.in_(page_ids)).all()
    
    # Create a dictionary for fast lookup
    for response in responses:
        responses_dict[response.id] = response
    
    # Return responses in the same order as sample IDs
    ordered_responses = []
    for id in page_ids:
        if id in responses_dict:
            ordered_responses.append(responses_dict[id].to_dict())
    
    return jsonify(ordered_responses)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5106))
    app.run(host="0.0.0.0", port=port)
