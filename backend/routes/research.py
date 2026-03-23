from flask import Blueprint, jsonify

research_bp = Blueprint('research', __name__)

@research_bp.route('/api/research', methods=['GET'])
def get_research():
    # Example mock data for research graph
    data = {
        "nodes": [
            {"id": 1, "type": "document", "title": "Architecture Patterns", "x": 50, "y": 50, "connections": [2]},
            {"id": 2, "type": "api", "title": "API Design Notes", "x": 300, "y": 80, "connections": [3]},
            {"id": 3, "type": "database", "title": "Schema Definitions", "x": 200, "y": 200, "connections": []}
        ]
    }
    return jsonify({"data": data})
