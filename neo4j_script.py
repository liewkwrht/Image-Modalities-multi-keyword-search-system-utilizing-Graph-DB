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


    def search_nodes_by_name(self, name, id, bodyPartName, symptomName, diseaseName, targetClasses=None):
        with self.get_session() as session:
            inputNames = [name, id, bodyPartName] + symptomName + [diseaseName]
            inputNames = [name for name in inputNames if name]
            defaultClasses = ["X_ray", "CT", "MRI", "DSI", "US"]

            
            targetClasses = targetClasses if targetClasses else defaultClasses

            
            query = "WITH $inputNames AS inputNames, $targetClasses AS targetClasses "

            
            query += (
                "OPTIONAL MATCH p1 = (node:BodyPart|Disease|Name)-[:Risk|AssociatedWith|Indicate|Affect|Own_image|Has_image*1]->(target) "
                "WHERE node.name IN inputNames AND LABELS(target)[0] IN targetClasses "
                "WITH target AS commonTarget, p1, inputNames, targetClasses, node "
                "OPTIONAL MATCH p2 = (symptom:Symptom)-[:Indicate]->(disease:Disease)-[:Has_image*1]->(target) "
                "WHERE symptom.name IN inputNames AND LABELS(target)[0] IN targetClasses AND target = commonTarget "
                "WITH commonTarget, COLLECT(DISTINCT p1) AS paths1, COLLECT(DISTINCT p2) AS paths2, node, inputNames, symptom "
                "WHERE ANY(path IN paths1 WHERE path IS NOT NULL) OR ANY(path IN paths2 WHERE path IS NOT NULL) "
                "WITH commonTarget, COUNT(DISTINCT node) AS relatedNodeCount, COUNT(DISTINCT symptom) AS relatedSymptom, inputNames "
                "WHERE relatedNodeCount = SIZE(inputNames) - relatedSymptom "
                "RETURN DISTINCT commonTarget;"
            )

            parameters = {'inputNames': inputNames, 'targetClasses': targetClasses}

            result = session.run(query, parameters=parameters)
            records = list(result)
            serializable_result = []
            for record in records:
                commonTarget = record['commonTarget']
                
                if isinstance(commonTarget, Node):
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

            return serializable_result