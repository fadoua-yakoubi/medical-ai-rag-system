from src.database.neo4j_connector import Neo4jConnector
from src.database.data_seeder import DataSeeder

def main():
    print("=" * 60)
    print("🏥 Medical Database Population")
    print("=" * 60)
    
    # Connexion
    connector = Neo4jConnector()
    if not connector.test_connection():
        print("❌ Cannot connect to Neo4j")
        return False
    
    graph = connector.get_graph()
    
    # Seeding
    seeder = DataSeeder(graph)
    seeder.clear_database()
    success = seeder.seed_from_json("data/medical_data.json")
    
    if success:
        # Stats
        stats = graph.query("MATCH (n) RETURN labels(n)[0] as type, COUNT(*) as count")
        print("\n📈 Database Statistics:")
        for row in stats:
            print(f"  - {row.get('type', 'Unknown')}: {row.get('count', 0)}")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)