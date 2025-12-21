# 🏥 Medical Knowledge Graph & Explainability System

A sophisticated **Multi-Agent AI System** that leverages **Graph RAG** (Retrieval-Augmented Generation) with **Neo4j** to answer any medical question in multiple languages (French & English).

## 🚀 Features

### Core Capabilities
- **🔍 Disease Diagnosis** - Analyze symptoms to find matching diseases
- **💊 Treatment Information** - Query which diseases use specific treatments
- **🔬 Cause Analysis** - Understand what causes specific diseases
- **📚 Medical Information** - Get comprehensive details about diseases
- **🛡️ Prevention Tips** - Learn how to prevent diseases
- **⚖️ Disease Comparison** - Compare different medical conditions
- **🌐 Multilingual Support** - Ask in French or English, get answers in the same language

### Architecture Highlights
- **Agent Orchestration**: CrewAI with 2 specialized agents
  - **Diagnostician**: Queries Neo4j Knowledge Graph using GraphRAG
  - **Explainer**: Structures results into patient-friendly explanations
- **Graph Database**: Neo4j AuraDB (Cloud) with 14 diseases, 109 symptoms, 92 treatments, 92 causes
- **LLM**: Groq API (llama-3.3-70b-versatile) - Fast, Free & Reliable
- **RAG**: LangChain GraphCypherQAChain with intelligent Cypher generation
- **Interface**: Streamlit web application
- **Language Detection**: Automatic FR/EN detection with same-language responses




### Prerequisites
- Python 3.9+
- Groq API Key (free at https://console.groq.com)
- Neo4j AuraDB instance (free tier available)

### Installation (5 minutes)

```bash
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your credentials
# See Configuration section below

# 4. Populate database (first time only)
.\venv\Scripts\python src/rag_etl.py

# 5. Run the application
.\venv\Scripts\python -m streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 🔧 Configuration

Create a `.env` file in the project root:

```env
# Groq API (Get free key at https://console.groq.com)
GROQ_API_KEY=gsk_your_key_here
GOOGLE_MODEL_NAME=llama-3.3-70b-versatile

# Neo4j AuraDB (Free tier available)
NEO4J_URI=neo4j+s://your_database_id.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here

# Optional: Google Gemini API (fallback)
GOOGLE_API_KEY=your_google_key_here
```

## 🎯 Usage Examples

### French Questions 🇫🇷
```
Q: "Quels sont les symptômes du diabète?"
A: [Response in French with symptoms, treatments, and causes]

Q: "Comment traiter l'hypertension?"
A: [French response with treatment options]

Q: "Qu'est-ce qui cause l'asthme?"
A: [French response with causes]
```

### English Questions 🇬🇧
```
Q: "What are the symptoms of diabetes?"
A: [Response in English with symptoms, treatments, and causes]

Q: "How to treat hypertension?"
A: [English response with treatment options]

Q: "What causes asthma?"
A: [English response with causes]
```

## 🔄 How It Works

### Request Flow Diagram

```
User Input (FR or EN)
    ↓
[Auto Language Detection]
    ↓
Streamlit Interface
    ↓
CrewAI Orchestrator
    ↓
Agent 1: Diagnostician
    ├─ MedicalRAGTool
    ├─ Cypher Query Generation (LLM)
    ├─ Neo4j Graph Query
    └─ Results Parsing
    ↓
Agent 2: Explainer
    ├─ Structure Results
    └─ Generate Response
    ↓
Format Answer 
    ↓
Display in Streamlit
```





2.  **Dans l'interface Web** :
    *   La base de données se seed automatiquement au démarrage si vide.
    *   Entrez vos symptômes (ex: *"I have a fever and a sore throat"*).
    *   Cliquez sur **"Analyze Symptoms"**.
    *   Attendez que les 2 agents traitent votre requête.

## 📊 Exemple de Flux

**Input utilisateur**: "I have severe stomach pain and diarrhea"

1. **Agent Diagnostician**:
   - **Normalise** l'input: "severe stomach pain" → "stomach pain"
   - Appelle `Medical Graph Search` tool
   - Génère Cypher: `MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom) WHERE s.name IN ['stomach pain', 'diarrhea'] RETURN DISTINCT d.name`
   - Résultat: Gastroenteritis, COVID-19

2. **Agent Explainer**:
   - Analyse les maladies trouvées
   - Génère explication structurée avec niveau de confiance
   - Output: "Based on your symptoms (stomach pain, diarrhea), you might have Gastroenteritis (80% confidence) or COVID-19 (40% confidence)..."





## 🔑 Variables d'Environnement

```env
# Groq API (LLM Provider)
GROQ_API_KEY=gsk_...                        # Clé API Groq (https://console.groq.com)
GOOGLE_MODEL_NAME=llama-3.3-70b-versatile   # Modèle Groq (vérifier disponibilité)

# Neo4j Database
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io  # URI AuraDB
NEO4J_USERNAME=neo4j                           # Username Neo4j
NEO4J_PASSWORD=your_password                   # Mot de passe Neo4j
```

## 🧪 Exemples de Questions à Tester

### Symptômes Respiratoires:
- "I'm feeling really sick with a high fever and dry cough"
- "I have shortness of breath and chest pain"
- "I have wheezing and can't breathe well"
- "I have sinus pressure and nasal congestion"

### Symptômes Digestifs:
- "I have severe stomach pain and diarrhea"
- "I'm nauseous and vomiting"
- "I have abdominal cramps and feel weak"

### Symptômes Neurologiques:
- "I have a severe headache and feel dizzy"
- "I lost my sense of taste and smell"

### Symptômes Combinés:
- "I have fever, dry cough, and fatigue"
- "I have body aches, chills, and headache"
- "I have sneezing, watery eyes, and itching"


## 📚 Ressources

- [Groq Documentation](https://console.groq.com/docs)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [CrewAI Documentation](https://docs.crewai.com)
- [LangChain GraphCypherQAChain](https://python.langchain.com/docs/use_cases/graph/graph_cypher_qa)


---

```
