import logging
import os
from flask import jsonify, request
from app import app, db
from flask_cors import CORS

from models import MetricSet, Response, Sample
from schema import tests_schema

logger = logging.getLogger("metrics-api")

CORS(app)

@app.route("/", methods=["GET"])
def base_endpoint():
    return jsonify({
        "msg": "Don't panic"
    })


@app.route("/schema", methods=["GET"])
def schema_endpoint():
    tests_schema_serializable = {
        entity: [
            {**test, "test_func": test.get("test_func").__name__, "key": test.get("display_name").replace(" ", "_").lower()}
            for test in tests
        ]
        for entity, tests in tests_schema.items()
    }
    return jsonify({"tests_schema": tests_schema_serializable})


@app.route("/coverage", methods=["GET"])
def coverage_endpoint():
    # return the latest metricset with type: "coverage"
    scope = request.args.get("sample", "all")
    metricset = MetricSet.query.filter_by(type="coverage", scope=scope).order_by(MetricSet.date.desc()).first()
    return jsonify(metricset.to_dict())


@app.route("/match-rates", methods=["GET"])
def match_rates_endpoint():
    # return the latest metricset with type: "match_rates"
    scope = request.args.get("sample", "all")
    metricset = MetricSet.query.filter_by(type="match_rates", scope=scope).order_by(MetricSet.date.desc()).first()
    return jsonify(metricset.to_dict())


def get_latest_sample(entity, type_="both", scope="all"):
    return db.session.query(Sample).filter_by(entity=entity, type=type_, scope=scope).order_by(Sample.date.desc()).first()


@app.route("/responses/<entity>", methods=["GET"])
def responses_endpoint(entity):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    filter_test = request.args.get("filterTest", "")
    scope = request.args.get("sample", "all")
    if filter_test:
        filter_test = filter_test.split(",")


    sample = get_latest_sample(entity, scope=scope)
    
    if not sample or not sample.ids:
        return jsonify([])
    
    if filter_test:
        from sqlalchemy import text, func
        
        # Build the filter conditions
        filter_conditions = []
        for field in filter_test:
            filter_conditions.append(f"(match ->> '{field}')::boolean = true")
    
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
        "results": ordered_responses
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5106))
    app.run(host="0.0.0.0", port=port)
