import streamlit as st
import os
from src.agents.crew_orchestrator import MedicalCrewOrchestrator
from src.database.neo4j_connector import Neo4jConnector
from src.database.data_seeder import DataSeeder
from dotenv import load_dotenv
load_dotenv(override=True)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

# Définir TOUTES les variables pour forcer Groq
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["GROQ_MODEL_NAME"] = GROQ_MODEL

# ⚠️ DÉSACTIVER complètement OpenAI
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("OPENAI_API_BASE", None)
os.environ.pop("OPENAI_BASE_URL", None)
os.environ.pop("OPENAI_MODEL_NAME", None)

# Importer APRÈS configuration
from src.agents.crew_orchestrator import MedicalCrewOrchestrator
from src.database.neo4j_connector import Neo4jConnector
from src.database.data_seeder import DataSeeder

print(f"\n{'='*60}")
print(f"🔑 Configuration LLM:")
print(f"  Provider: Groq")
print(f"  Model: {GROQ_MODEL}")
print(f"  API Key: {GROQ_API_KEY[:15]}...{GROQ_API_KEY[-4:]}")
print(f"{'='*60}\n")

# Auto-seed si nécessaire
try:
    connector = Neo4jConnector()
    graph = connector.get_graph()
    result = graph.query("MATCH (n) RETURN count(n) as count")
    node_count = result[0]['count'] if result else 0
    
    print(f"[DATABASE] {node_count} nodes found")
    
    if node_count == 0:
        print("[DATABASE] Seeding...")
        seeder = DataSeeder(graph)
        seeder.seed_from_json("data/medical_data.json")
        print("[DATABASE] Seeded successfully")
except Exception as e:
    print(f"[DATABASE ERROR] {e}")

# Interface Streamlit
st.set_page_config(page_title="Medical RAG", layout="wide")
st.title("🏥 Medical Knowledge Graph & RAG System")

st.markdown("""
**Capabilities:** Disease Diagnosis | Treatment Info | Cause Analysis

**Agents:** Diagnostician (GraphRAG) + Explainer (Patient-friendly)
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.success(f"""
    **LLM:** Groq ({GROQ_MODEL})  
    **Key:** {GROQ_API_KEY[:10]}...
    """)
    
    # Override (optionnel)
    new_key = st.text_input(
        "Override Groq Key", 
        type="password",
        help="Leave empty to use .env"
    )
    if new_key:
        os.environ["GROQ_API_KEY"] = new_key

# Main input
question = st.text_area(
    "Ask your medical question:",
    placeholder="e.g., 'I have fever and cough'",
    height=100
)

if st.button("🔍 Analyze Question", use_container_width=True):
    if not question:
        st.warning("⚠️ Please enter a question")
    elif not GROQ_API_KEY:
        st.error("❌ Groq API Key missing in .env")
    else:
        with st.spinner("🤖 Analyzing (10-15 seconds)..."):
            try:
                # ✅ Vérifier variables avant exécution
                print(f"\n[EXECUTION] Starting with:")
                print(f"  GROQ_API_KEY: {os.getenv('GROQ_API_KEY')[:20]}...")
                print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT SET')}")
                
                orchestrator = MedicalCrewOrchestrator()
                result = orchestrator.run(question)
                
                st.subheader("📊 Results")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                
                # Diagnostic détaillé
                with st.expander("🔍 Debug Info"):
                    st.code(f"""
Error: {str(e)}

Environment Variables:
- GROQ_API_KEY: {os.getenv('GROQ_API_KEY', 'NOT SET')[:20]}...
- OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT SET')}
- GROQ_MODEL_NAME: {os.getenv('GROQ_MODEL_NAME', 'NOT SET')}
                    """)

st.caption("⚠️ Educational purposes only")