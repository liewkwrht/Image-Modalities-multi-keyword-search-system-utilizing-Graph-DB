from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship, Path
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
                # logging.info("Neo4j Driver connection established.")
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


    def search_nodes_by_name(self, name, patient_id, bodyPartName, symptomName, disease_Name, targetClasses=None):
        with self.get_session() as session:
            inputNames = [value for value in [name, patient_id, bodyPartName] + symptomName + [disease_Name] if value]
            # inputNames = [value for value in inputNames if value or value == 0]
            defaultClasses = ["X_ray", "CT", "MRI", "DSI", "US"]

            
            targetClasses = targetClasses if targetClasses else defaultClasses

            
            query = "WITH $inputNames AS inputNames, $targetClasses AS targetClasses "

            
            query += """ 
            OPTIONAL MATCH (name:Name)-[:Own_image]->(target1)
            WHERE name.name IN inputNames OR name.id IN inputNames AND LABELS(target1)[0] IN targetClasses

            OPTIONAL MATCH (disease:Disease)-[:Has_image]->(target2)
            WHERE disease.name IN inputNames AND LABELS(target2)[0] IN targetClasses

            OPTIONAL MATCH (bodyPart:BodyPart)-[:AssociatedWith]->(target3)
            WHERE bodyPart.name IN inputNames AND LABELS(target3)[0] IN targetClasses

            OPTIONAL MATCH (symptom:Symptom)-[:Indicate]->(:Disease)-[:Has_image]->(target4)
            WHERE symptom.name IN inputNames AND LABELS(target4)[0] IN targetClasses

            WITH target1, target2, target3, target4,
            CASE WHEN target1 IS NULL THEN 0 ELSE 1 END +
            CASE WHEN target2 IS NULL THEN 0 ELSE 1 END +
            CASE WHEN target3 IS NULL THEN 0 ELSE 1 END +
            CASE WHEN target4 IS NULL THEN 0 ELSE 1 END AS notnullTargetCount,
            COLLECT(DISTINCT target1) AS targets1, 
            COLLECT(DISTINCT target2) AS targets2,
            COLLECT(DISTINCT target3) AS targets3, 
            COLLECT(DISTINCT target4) AS targets4

            WITH 
            targets1 + targets2 + targets3 + targets4 AS allTargets,
            notnullTargetCount, target1

            WITH allTargets, notnullTargetCount, apoc.coll.frequencies(allTargets) AS nodeFrequencies

            WITH [entry IN nodeFrequencies | CASE WHEN entry.count = notnullTargetCount THEN entry.item END] AS filteredNodes

            RETURN DISTINCT filteredNodes
            
            """

            parameters = {'inputNames': inputNames, 'targetClasses': targetClasses}
            # test query are running with correct parameter or not

            # logging.info(f"inputNames after processing: {inputNames}")
            logging.info(f"Executing query with parameters: {parameters}")
            logging.info(f"Query: {query}")
            result = session.run(query, parameters=parameters)
            records = list(result)
            serializable_result = []
            
        for record in records:
            filteredNodes = record['filteredNodes']  # This can be a list or None
            if filteredNodes:
                for node in filteredNodes:
                    if isinstance(node, Node):
                        # Handle Node object
                        node_data = {
                            'id': node.id,
                            'labels': list(node.labels),
                            'properties': dict(node)
                        }
                        serializable_result.append({'nodes': [node_data], 'relationships': []})
                    elif isinstance(node, Relationship):
                        # Handle Relationship object
                        relationship_data = {
                            'id': node.id,
                            'type': node.type,
                            'properties': dict(node)
                        }
                        serializable_result.append({'nodes': [], 'relationships': [relationship_data]})
                    # Add more conditions if needed, like for Path objects
            else:
                # Handle the case where filteredNodes is None or empty
                logging.info("No nodes found for the given criteria.")
                # Optionally add more logic here if needed

        return serializable_result
