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
    
    
    def search_nodes_by_name(self, bodyPartName, symptomName, diseaseName, imageType=None):
            with self.get_session() as session:
                # Start building your query string
                query = (
                    "MATCH p=(node:BodyPart|Symptom|Disease|Name)-[:Risk|AssociatedWith|Indicate|Affect|Own_image|Has_image*1]->(target) "
                    "WHERE node.name IN $inputNames "
                )
                
                # If an imageType is specified, add that to the WHERE clause
                if imageType:
                    query += "AND $imageType IN labels(target) "
                
                # Finish off your query
                query += "RETURN DISTINCT p;"

                # Create parameters dictionary
                parameters = {
                    'inputNames': [bodyPartName, symptomName, diseaseName]
                }
                
                # If an imageType is specified, add that to the parameters
                if imageType:
                    parameters['imageType'] = imageType

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