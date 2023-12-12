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
    
    
    def search_nodes_by_name(self, bodyPartName, symptomName, diseaseName, targetClasses=None):
        with self.get_session() as session:
            # Define input names
            inputNames = [name for name in [bodyPartName, symptomName, diseaseName] if name]

            # Start building your query string
            query = "WITH $inputNames AS inputNames "

            # Add target classes to the query if provided
            if targetClasses:
                query += ", $targetClasses AS targetClasses "
                query += (
                    "MATCH p=(node:BodyPart|Symptom|Disease|Name)-[:Risk|AssociatedWith|Indicate|Affect|Own_image|Has_image*1]->(target) "
                    "WHERE node.name IN inputNames AND LABELS(target)[0] IN targetClasses "
                )
            else:
                query += (
                    "MATCH p=(node:BodyPart|Symptom|Disease|Name)-[:Risk|AssociatedWith|Indicate|Affect|Own_image|Has_image*1]->(target) "
                    "WHERE node.name IN inputNames "
                )

            # Finish off your query
            query += "RETURN DISTINCT p;"

            # Create parameters dictionary
            parameters = {'inputNames': inputNames}
            
            # Add targetClasses to parameters if provided
            if targetClasses:
                parameters['targetClasses'] = targetClasses

            # Run the query
            result = session.run(query, parameters=parameters)
            records = list(result)

        # Process the records to serialize the paths
        serializable_result = []
        for record in records:
            path = record['p']
            # Extract nodes and relationships from the path
            nodes = [{'id': node.id, 'labels': list(node.labels), 'properties': dict(node)} for node in path.nodes]
            relationships = [{'id': rel.id, 'type': rel.type, 'properties': dict(rel)} for rel in path.relationships]
            path_data = {'nodes': nodes, 'relationships': relationships}
            serializable_result.append(path_data)

        return serializable_result
