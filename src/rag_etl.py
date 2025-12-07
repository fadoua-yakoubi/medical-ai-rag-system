"""
rag_etl.py - ETL unifié pour populer Neo4j avec données enrichies
Intègre la logique de la collègue + configuration URL
Supporte: Disease, Symptom, Treatment, Cause + Relations
"""
import json
import os
import re
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

load_dotenv()

def sanitize(name: str) -> str:
    """Transforme un nom en identifiant Neo4j valide."""
    if not name:
        return "unknown"
    name = name.lower()
    # Accents
    name = re.sub(r"[éèêë]", "e", name)
    name = re.sub(r"[àâä]", "a", name)
    name = re.sub(r"[îï]", "i", name)
    name = re.sub(r"[ôö]", "o", name)
    name = re.sub(r"[ùûü]", "u", name)
    name = re.sub(r"[ç]", "c", name)
    # Caractères spéciaux
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")

def get_graph_db():
    """
    Initialise et retourne la connexion Neo4jGraph.
    Supporte URL Neo4j (AuraDB) et local.
    """
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "")
    )
    return graph

def populate_graph_from_json(graph: Neo4jGraph, json_path: str = "src/RAG Graph/medical_data.json"):
    """
    Lit le JSON et peuple le graphe Neo4j avec:
    - Disease nodes
    - Symptom nodes
    - Treatment nodes
    - Cause nodes
    - Relations: HAS_SYMPTOM, TREATED_WITH, CAUSED_BY
    """
    
    # Lire JSON
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            medical_data = json.load(f)
        print(f"✅ Fichier {json_path} lu avec succès")
    except FileNotFoundError:
        print(f"❌ ERREUR : Fichier {json_path} non trouvé")
        return False
    except json.JSONDecodeError:
        print(f"❌ ERREUR : JSON invalide dans {json_path}")
        return False
    
    print("🧱 Création du graphe Neo4j avec données enrichies...")
    
    disease_count = 0
    symptom_count = 0
    treatment_count = 0
    cause_count = 0
    relation_count = 0
    
    try:
        for disease_entry in medical_data:
            disease_name = disease_entry.get("maladie", "Unknown Disease")
            disease_id = sanitize(disease_name)
            
            # Créer nœud Disease
            graph.query(f"""
                MERGE (d:Disease {{name: "{disease_name}"}})
            """)
            disease_count += 1
            
            # Créer relations HAS_SYMPTOM
            for symptom_name in disease_entry.get("symptomes", []):
                symptom_name = symptom_name.strip()
                symptom_id = sanitize(symptom_name)
                
                graph.query(f"""
                    MERGE (s:Symptom {{name: "{symptom_name}"}})
                    WITH s
                    MATCH (d:Disease {{name: "{disease_name}"}})
                    MERGE (d)-[:HAS_SYMPTOM]->(s)
                """)
                symptom_count += 1
                relation_count += 1
            
            # Créer relations TREATED_WITH
            for treatment_name in disease_entry.get("traitements", []):
                treatment_name = treatment_name.strip()
                treatment_id = sanitize(treatment_name)
                
                graph.query(f"""
                    MERGE (t:Treatment {{name: "{treatment_name}"}})
                    WITH t
                    MATCH (d:Disease {{name: "{disease_name}"}})
                    MERGE (d)-[:TREATED_WITH]->(t)
                """)
                treatment_count += 1
                relation_count += 1
            
            # Créer relations CAUSED_BY
            for cause_name in disease_entry.get("causes", []):
                cause_name = cause_name.strip()
                cause_id = sanitize(cause_name)
                
                graph.query(f"""
                    MERGE (c:Cause {{name: "{cause_name}"}})
                    WITH c
                    MATCH (d:Disease {{name: "{disease_name}"}})
                    MERGE (d)-[:CAUSED_BY]->(c)
                """)
                cause_count += 1
                relation_count += 1
        
        print("✅ Graphe créé avec succès !")
        print(f"""
📊 Statistiques:
  - Maladies (Disease): {disease_count}
  - Symptômes (Symptom): {symptom_count}
  - Traitements (Treatment): {treatment_count}
  - Causes (Cause): {cause_count}
  - Relations totales: {relation_count}
        """)
        return True
    
    except Exception as e:
        print(f"❌ ERREUR lors du peuplement du graphe: {e}")
        return False

def clear_graph(graph: Neo4jGraph):
    """Vide le graphe Neo4j."""
    try:
        graph.query("MATCH (n) DETACH DELETE n")
        print("🗑️  Graphe vidé avec succès")
        return True
    except Exception as e:
        print(f"❌ ERREUR lors du vidage du graphe: {e}")
        return False

def main():
    """Script principal: vide et peuple le graphe."""
    
    print("=" * 60)
    print("🏥 ETL Neo4j - Peuplement avec données enrichies")
    print("=" * 60)
    
    # Initialiser connexion
    try:
        graph = get_graph_db()
        print(f"✅ Connecté à Neo4j: {os.getenv('NEO4J_URI')}")
    except Exception as e:
        print(f"❌ Impossible de se connecter à Neo4j: {e}")
        return False
    
    # Vider graphe
    if not clear_graph(graph):
        return False
    
    # Peupler graphe
    if not populate_graph_from_json(graph):
        return False
    
    # Afficher statistiques finales
    try:
        stats = graph.query("MATCH (n) RETURN labels(n)[0] as type, COUNT(*) as count")
        print("\n📈 Répartition des nœuds:")
        for row in stats:
            print(f"  - {row.get('type', 'Unknown')}: {row.get('count', 0)}")
    except Exception as e:
        print(f"⚠️  Impossible d'afficher les statistiques: {e}")
    
    print("\n✅ ETL terminé avec succès!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
