import streamlit as st
import os
from src.crew import MedicalCrew
from src.graph import seed_db
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Force all OpenAI calls to go through Groq by setting env vars
# This overrides CrewAI's internal routing
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

# Auto-seed database on startup if empty
try:
    from src.graph import get_graph_db
    graph = get_graph_db()
    result = graph.query("MATCH (n) RETURN count(n) as count")
    node_count = result[0]['count'] if result else 0
    print(f"\n{'='*60}")
    print(f"[STARTUP] Database has {node_count} nodes")
    if node_count == 0:
        print("[STARTUP] Database is empty, seeding with sample data...")
        seed_db()
        result = graph.query("MATCH (n) RETURN count(n) as count")
        print(f"[STARTUP] After seeding: {result[0]['count']} nodes")
    else:
        print("[STARTUP] Database already has data, skipping seed")
    print(f"{'='*60}\n")
except Exception as e:
    print(f"\n[STARTUP ERROR] Could not check/seed database: {e}")
    import traceback
    traceback.print_exc()

st.set_page_config(page_title="Medical Knowledge Graph RAG", layout="wide")

st.title("🏥 Medical Knowledge Graph & Explainability System")
st.markdown("""
This advanced **Multi-Agent System** (CrewAI) with **Graph RAG** (Neo4j + LangChain) answers all types of medical questions:

**System Capabilities:**
1. 🔍 **Disease Diagnosis** - Analyze symptoms to find matching diseases
2. 💊 **Treatment Information** - Query which diseases use specific treatments
3. 🔬 **Cause Analysis** - Understand what causes specific diseases
4. 📚 **Medical Information** - Get comprehensive details about diseases
5. 🛡️ **Prevention Tips** - Learn how to prevent diseases
6. ⚖️ **Disease Comparison** - Compare different medical conditions

**Agents:**
- **Diagnostician:** Queries the Neo4j Knowledge Graph using GraphRAG to find relevant diseases
- **Explainer:** Structures results into clear, patient-friendly explanations
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    # Groq API Key (preferred free)
    groq_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key

    # Optional: Google Gemini API Key (fallback only)
    api_key = st.text_input("Google Gemini API Key (optional)", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    st.caption("Free LLM recommended: Groq (llama-3.1-8b-instant)")

    st.header("Database")
    if st.button("Seed Database (Test Data)"):
        with st.spinner("Seeding database..."):
            try:
                seed_db()
                st.success("Database seeded!")
            except Exception as e:
                st.error(f"Error seeding database: {e}")

# Main Input
st.subheader("📋 Ask Any Medical Question")
st.info("""
**Examples of questions you can ask:**
- Diagnosis: "I have fever and cough"
- Treatments: "What disease is treated with Metformin?"
- Causes: "What causes Diabetes?"
- Information: "Tell me about Asthma"
- Prevention: "How to prevent Hypertension?"
""")

question = st.text_area(
    "Enter your medical question:",
    placeholder="e.g., 'I have fatigue and excessive thirst' OR 'What disease is treated with Ventoline?' OR 'What causes Asthma?'",
    height=100
)

if st.button("🔍 Analyze Question", use_container_width=True):
    if not question:
        st.warning("Please enter a medical question.")
    elif not (os.getenv("GROQ_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        st.error("Please provide a Groq API Key (recommended) or Google Gemini API Key.")
    else:
        with st.spinner("🤖 Medical agents analyzing your question... (This may take 10-15 seconds)"):
            try:
                crew = MedicalCrew()
                result = crew.run(question)
                
                st.subheader("📊 Medical Analysis & Explanation")
                st.markdown(result)
                
                # Optional: Display raw result if needed for debugging
                with st.expander("📋 See Raw Output"):
                    st.write(result)
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.markdown("---")
st.caption("""
🚀 **Powered by:** CrewAI, LangChain, GraphRAG, Neo4j, and Groq LLM  
📚 **System:** 14 diseases | 109 symptoms | 92 treatments | 92 causes  
⚠️ **Disclaimer:** This is for educational purposes. Always consult a healthcare professional for medical advice.
""")
