#neo4j_script.py
from neo4j import GraphDatabase
import logging

class Neo4jConnector:
    def __init__(self, uri, username, password):
        self._uri = uri
        self._username = username
        self._password = password
        self._driver = None

    def connect(self):
        if not self._driver:
            try:
                self._driver = GraphDatabase.driver(self._uri, auth=(self._username, self._password))
                logging.info("Neo4j Driver connection established.")
            except Exception as e:
                logging.error(f"Failed to connect to Neo4j: {e}")
                raise

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None 

    def get_session(self):
        if not self._driver:
            self.connect()
        return self._driver.session()
    def search_nodes_by_name(self, id, diseaseName, bodyPartName, symptomName):
        with self.get_session() as session:
            query = (
                "MATCH (n:Name {id: $id_value})-[:Own_image]->(imageNode) "
                "WHERE (imageNode:X_ray OR imageNode:CT OR imageNode:MRI OR imageNode:DSI OR imageNode:US) "
                "WITH imageNode "
                "MATCH (disease:Disease)-[:Has_image]->(imageNode) "
                "WHERE disease.name = $disease_name_value "
                "WITH imageNode "
                "MATCH (bodyPart:BodyPart)-[:Risk]->(disease) "
                "WHERE bodyPart.name = $body_part_name_value "
                "WITH imageNode "
                "MATCH (symptom:Symptom)-[:Indicate]->(disease) "
                "WHERE symptom.name = $symptom_name_value "
                "RETURN imageNode"
            )

            parameters = {
                'id_value': int(id),
                'disease_name_value': diseaseName,
                'body_part_name_value': bodyPartName,
                'symptom_name_value': symptomName
            }

            print(f"Executing query: {query}")
            print(f"With parameters: {parameters}")

            try:
                result = session.run(query, parameters)
                result_data = [record["imageNode"] for record in result]
                print(f"Query result: {result_data}")
                return result_data
            except Exception as e:
                print(f"An error occurred: {e}")
                raise


        # The following lines should be in your main Flask app file, not in the neo4j_script.py
        # from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD  
        # neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        # app = Flask(__name__)
        # logging.basicConfig(level=logging.INFO)
