from flask import Flask, jsonify, request
from neo4j_script import Neo4jConnector  # Ensure neo4j_script.py is in the same directory and has the correct implementation
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from flask_cors import CORS
import logging
import time
from collections import defaultdict

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)


neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    name = data.get('name')
    id = data.get('id')
    body_part_name = data.get('bodypart')
    disease_name = data.get('disease')
    symptom_name = data.get('symptom', [])
    target_classes = data.get('targetClasses')  

    try:
        start_time = time.time()
        serializable_result = neo4j_connector.search_nodes_by_name(name,id,body_part_name, symptom_name, disease_name, target_classes)
        execution_time = time.time() - start_time
        nodes_by_label = defaultdict(list)
        label_counts = defaultdict(int)

        for path_data in serializable_result:
            for node in path_data['nodes']:
                for label in node['labels']:
                    nodes_by_label[label].append(node)
                    label_counts[label] += 1

        
        organized_data = {label: {'count': label_counts[label], 'nodes': nodes} for label, nodes in nodes_by_label.items()}
        unique_uids = set()
        for path_data in serializable_result:
            for node in path_data['nodes']:
                if 'uid' in node['properties']:
                    unique_uids.add(node['properties']['uid'])

        uid_count = len(unique_uids)
        response = {
                    "execution_time": execution_time,
                    "data": organized_data, 
                    "unique_uid_count": uid_count  
                }


        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.teardown_appcontext
def close_connection(exception=None):
    neo4j_connector.close()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
