import json
import os
from langchain_community.graphs import Neo4jGraph
from ..utils.text_utils import sanitize

class DataSeeder:
    """Peuple Neo4j avec les données médicales."""
    
    def __init__(self, graph: Neo4jGraph):
        self.graph = graph
    
    def seed_from_json(self, json_path: str = "data/medical_data.json") -> bool:
        """Peuple le graphe à partir du fichier JSON."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                medical_data = json.load(f)
            
            print(f"📥 Loaded {len(medical_data)} diseases from JSON")
            
            for disease_entry in medical_data:
                disease_name = disease_entry.get("maladie", "Unknown")
                
                # Créer nœud Disease
                self.graph.query(f"""
                    MERGE (d:Disease {{name: "{disease_name}"}})
                """)
                
                # Créer Symptoms
                for symptom in disease_entry.get("symptomes", []):
                    self.graph.query(f"""
                        MERGE (s:Symptom {{name: "{symptom}"}})
                        WITH s
                        MATCH (d:Disease {{name: "{disease_name}"}})
                        MERGE (d)-[:HAS_SYMPTOM]->(s)
                    """)
                
                # Créer Treatments
                for treatment in disease_entry.get("traitements", []):
                    self.graph.query(f"""
                        MERGE (t:Treatment {{name: "{treatment}"}})
                        WITH t
                        MATCH (d:Disease {{name: "{disease_name}"}})
                        MERGE (d)-[:TREATED_WITH]->(t)
                    """)
                
                # Créer Causes
                for cause in disease_entry.get("causes", []):
                    self.graph.query(f"""
                        MERGE (c:Cause {{name: "{cause}"}})
                        WITH c
                        MATCH (d:Disease {{name: "{disease_name}"}})
                        MERGE (d)-[:CAUSED_BY]->(c)
                    """)
            
            print("✅ Database seeded successfully")
            return True
        
        except FileNotFoundError:
            print(f"❌ JSON file not found: {json_path}")
            return False
        except Exception as e:
            print(f"❌ Seeding error: {e}")
            return False
    
    def clear_database(self):
        """Vide la base de données."""
        try:
            self.graph.query("MATCH (n) DETACH DELETE n")
            print("🗑️ Database cleared")
        except Exception as e:
            print(f"❌ Clear error: {e}")