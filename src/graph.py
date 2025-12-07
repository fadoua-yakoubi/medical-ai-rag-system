import os
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

load_dotenv()

def get_graph_db():
    """
    Initializes and returns the Neo4jGraph connection.
    """
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    return graph

def seed_db():
    """
    Seeds the database with some sample medical data for testing purposes.
    """
    graph = get_graph_db()
    
    # Clear existing data first
    print("Clearing existing data...")
    graph.query("MATCH (n) DETACH DELETE n")
    
    print("Seeding database with sample medical data...")
    
    cypher_queries = [
        """
        CREATE (f:Symptom {name: 'fever'}),
               (c:Symptom {name: 'cough'}),
               (h:Symptom {name: 'headache'}),
               (rn:Symptom {name: 'runny nose'}),
               (st:Symptom {name: 'sore throat'}),
               (fgt:Symptom {name: 'fatigue'}),
               
               (flu:Disease {name: 'Influenza'}),
               (cold:Disease {name: 'Common Cold'}),
               (cov:Disease {name: 'COVID-19'}),
               
               (flu)-[:HAS_SYMPTOM]->(f),
               (flu)-[:HAS_SYMPTOM]->(c),
               (flu)-[:HAS_SYMPTOM]->(h),
               (flu)-[:HAS_SYMPTOM]->(fgt),
               (flu)-[:HAS_SYMPTOM]->(st),
               
               (cold)-[:HAS_SYMPTOM]->(rn),
               (cold)-[:HAS_SYMPTOM]->(st),
               (cold)-[:HAS_SYMPTOM]->(c),
               
               (cov)-[:HAS_SYMPTOM]->(f),
               (cov)-[:HAS_SYMPTOM]->(c),
               (cov)-[:HAS_SYMPTOM]->(fgt),
               (cov)-[:HAS_SYMPTOM]->(st),
               (cov)-[:HAS_SYMPTOM]->(h)
        """
    ]
    
    for query in cypher_queries:
        graph.query(query)
    
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed_db()
