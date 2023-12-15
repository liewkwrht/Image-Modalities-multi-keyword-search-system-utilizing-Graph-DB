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

def get_neo4j_connector():
    return Neo4jConnector(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

@app.route('/api/search', methods=['POST'])
def search():
    neo4j_connector = get_neo4j_connector()
    try:
        data = request.json
        name = data.get('name')
        patient_id = data.get('patient_id')
        body_part_name = data.get('bodypart')
        disease_Name = data.get('disease')
        symptom_name = data.get('symptoms', [])
        target_classes = data.get('targetClasses')
        # test parameter received
        # app.logger.info(f"id received: {patient_id}")
        # app.logger.info(f"Name received: {name}")
        # app.logger.info(f"bodypart received: {body_part_name}")
        # app.logger.info(f"disease received: {disease_Name}")
        # app.logger.info(f"symptom received: {symptom_name}")
        # app.logger.info(f"targetClasses received: {target_classes}")


    # print time,result
        try:
            start_time = time.time()
            serializable_result = neo4j_connector.search_nodes_by_name(name,patient_id,body_part_name, symptom_name, disease_Name, target_classes)
            execution_time = time.time() - start_time
            nodes_by_label = defaultdict(list)
            label_counts = defaultdict(int)

            
            for path_data in serializable_result:
                for node in path_data['nodes']:
                    for label in node['labels']:
                        nodes_by_label[label].append(node)
                        label_counts[label] += 1

            # organized data output
            organized_data = {label: {'count': label_counts[label], 'nodes': nodes} 
                                for label, nodes in nodes_by_label.items()}
            unique_uids = {node['properties']['uid'] for path_data in serializable_result 
                            for node in path_data['nodes'] if 'uid' in node['properties']}

            response = {
                        "execution_time": execution_time,
                        "data": organized_data, 
                        "unique_uid_count": len(unique_uids)
                    }


            return jsonify(response), 200
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return jsonify({'error': str(e)}), 500

    finally:
        neo4j_connector.close()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    