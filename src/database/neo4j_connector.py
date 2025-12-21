import os
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnector:
    """Gère la connexion à Neo4j."""
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self._graph = None
    
    def get_graph(self) -> Neo4jGraph:
        """Retourne la connexion Neo4j."""
        if self._graph is None:
            self._graph = Neo4jGraph(
                url=self.uri,
                username=self.username,
                password=self.password
            )
            self._graph.refresh_schema()
        return self._graph
    
    def test_connection(self) -> bool:
        """Teste la connexion Neo4j."""
        try:
            graph = self.get_graph()
            result = graph.query("MATCH (n) RETURN count(n) as count LIMIT 1")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
