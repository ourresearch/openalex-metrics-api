import logging
import os
from flask import jsonify, request
from app import app, db
from flask_cors import CORS

from models import MetricSet, Response
from metrics import get_latest_sample
from schema import schema, test_fields

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
    per_page = int(request.args.get("per_page", 100))
    filter_failing = request.args.get("filterFailing", False)
    if filter_failing:
        filter_failing = filter_failing.split(",")
    sample = get_latest_sample("works")
    
    if not sample or not sample.ids:
        return jsonify([])
    
    if filter_failing:
        from sqlalchemy import text, func
        
        # Build the filter conditions
        filter_conditions = []
        for field in filter_failing:
            filter_conditions.append(f"(match ->> '{field}')::boolean = false")
        
        filter_clause = " AND ".join(filter_conditions)
        
        # Calculate total results count for filtered data
        count_sql = text(f"""
            SELECT COUNT(*)
            FROM responses r
            WHERE r.id = ANY(:sample_ids)
            AND {filter_clause}
        """)
        
        count_result = db.session.execute(count_sql, {
            'sample_ids': sample.ids
        })
        total_results_count = count_result.scalar()
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Order by sample position
        sql = text(f"""
            SELECT r.id, r.entity, r.date, r.prod, r.walden, r.match
            FROM responses r
            WHERE r.id = ANY(:sample_ids)
            AND {filter_clause}
            ORDER BY array_position(:sample_ids, r.id)
            LIMIT :limit OFFSET :offset
        """)
        
        # Execute the query
        result = db.session.execute(sql, {
            'sample_ids': sample.ids,
            'limit': per_page,
            'offset': offset
        })
        
        # Convert results to dict format
        ordered_responses = []
        for row in result:
            ordered_responses.append({
                'id': row.id,
                'entity': row.entity,
                'date': row.date,
                'prod': row.prod,
                'walden': row.walden,
                'match': row.match
            })
        
    else:
        # Normal pagination - get slice of IDs first, then query
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
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
    
        total_results_count = len(sample.ids)
    
    return jsonify({
        "meta": {
            "page": page,
            "per_page": per_page,
            "sample_size": len(sample.ids),
            "count": total_results_count
        },
        "results":ordered_responses
    })


@app.route("/schema", methods=["GET"])
def schema_endpoint():
    return jsonify({"schema": schema, "testFields": test_fields})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5106))
    app.run(host="0.0.0.0", port=port)
