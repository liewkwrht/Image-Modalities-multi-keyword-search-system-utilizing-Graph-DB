from flask import Flask, jsonify, request
from neo4j_script import Neo4jConnector
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j.exceptions import ServiceUnavailable
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
# Instantiate the Neo4jConnector with the proper configuration variables
neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})
@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    id = data.get('id')
    bodypart = data.get('bodypart')
    disease = data.get('disease')
    symptom = data.get('symptom')

    try:
        # Execute the search query
        result_data = neo4j_connector.search_nodes_by_name(id, disease, bodypart, symptom)

        # Check if the result data is empty
        if not result_data:
            return jsonify([]), 204  # No Content if no results are found

        # Prepare the result data for JSON serialization
        serializable_result = []
        for record in result_data:
            # Assuming each record is a Node object, convert it to a dictionary
            serializable_result.append({
                "id": record.id,
                "labels": list(record.labels),
                "properties": dict(record)
            })

        # Return the JSON-serializable result
        return jsonify(serializable_result)

    except ServiceUnavailable as e:
        app.logger.error(f"Neo4j service is unavailable: {e}")
        return jsonify({'error': "Neo4j service is unavailable"}), 503
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500



@app.teardown_appcontext
def close_connection(exception=None):
    neo4j_connector.close()

# Uncomment these lines to run your application
if __name__ == '__main__':
    app.run(debug=True)
