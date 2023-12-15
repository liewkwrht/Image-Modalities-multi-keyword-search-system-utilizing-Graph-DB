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
            OPTIONAL MATCH (n:Name)

            WITH inputNames, targetClasses, CASE WHEN n.name IN inputNames AND n.id IN inputNames THEN 1 ELSE 0 END AS isnameandid 
            OPTIONAL MATCH p1 = (node:BodyPart|Disease|Name)-[:Risk|AssociatedWith|Indicate|Affect|Own_image|Has_image*1]->(target)
            WHERE (node.name IN inputNames OR node.id IN inputNames) AND LABELS(target)[0] IN targetClasses

            WITH target AS commonTarget, p1, inputNames, targetClasses, node, isnameandid 

            OPTIONAL MATCH p2 = (symptom:Symptom)-[:Indicate]->(disease:Disease)-[:Has_image*1]->(target)
            WHERE symptom.name IN inputNames AND LABELS(target)[0] IN targetClasses AND (commonTarget IS NULL OR target = commonTarget)

            WITH commonTarget, COLLECT(DISTINCT p1) AS paths1, COLLECT(DISTINCT p2) AS paths2, node, inputNames, symptom, isnameandid , target
            WHERE ANY(path IN paths1 WHERE path IS NOT NULL) OR ANY(path IN paths2 WHERE path IS NOT NULL)

            WITH commonTarget, COUNT(DISTINCT node) AS relatedNodeCount, COUNT(DISTINCT symptom) AS relatedsymptom , inputNames, isnameandid, target
            WHERE relatedNodeCount = SIZE(inputNames) - relatedsymptom - isnameandid
            RETURN DISTINCT commonTarget, target;
            
            """

            parameters = {'inputNames': inputNames, 'targetClasses': targetClasses}
            # test query are running with correct parameter or not

            logging.info(f"inputNames after processing: {inputNames}")
            logging.info(f"Executing query with parameters: {parameters}")
            logging.info(f"Query: {query}")
            result = session.run(query, parameters=parameters)
            records = list(result)
            serializable_result = []
            
        for record in records:
            # You have a record which is a dictionary with keys "commonTarget" and "target"
            commonTarget = record['commonTarget']  # This can be None/null
            target = record['target']  # This should be a Node object
            
            # Initialize an empty dictionary to store node data
            node_data = {}
            
            # If commonTarget is None, handle it by skipping or other logic
            if commonTarget is None:
                # logging.info("commonTarget is None, handling accordingly.")
                # You could skip this record, continue, or decide to add the target info anyway
                # If you choose to add the target info, you'd create a dictionary for it
                if isinstance(target, Node):
                    node_data = {
                        'id': target.id,
                        'labels': list(target.labels),
                        'properties': dict(target)
                    }
                    serializable_result.append({'nodes': [node_data], 'relationships': []})
            elif isinstance(commonTarget, Node):
                    # Handle a single Node object
                    node_data = {
                        'id': commonTarget.id,
                        'labels': list(commonTarget.labels),
                        'properties': dict(commonTarget)
                    }
                    serializable_result.append({'nodes': [node_data], 'relationships': []})
                
            elif isinstance(commonTarget, Relationship):
                
                    relationship_data = {
                        'id': commonTarget.id,
                        'type': commonTarget.type,
                        'properties': dict(commonTarget)
                    }
                    serializable_result.append({'nodes': [], 'relationships': [relationship_data]})
                
            elif isinstance(commonTarget, Path):
                    
                    nodes = [{'id': node.id, 'labels': list(node.labels), 'properties': dict(node)} for node in commonTarget.nodes]
                    relationships = [{'id': rel.id, 'type': rel.type, 'properties': dict(rel)} for rel in commonTarget.relationships]
                    path_data = {'nodes': nodes, 'relationships': relationships}
                    serializable_result.append(path_data)
            else:
                    
                    logging.error(f"Unhandled type for commonTarget: {type(commonTarget)}")

                
            #serializable result
                    serializable_result.append({'nodes': [node_data], 'relationships': []})
            
    # Add logging to debug the loop execution
            # logging.debug(f"Processed record with target id: {node_data.get('id', 'Unknown')}")

        return serializable_result