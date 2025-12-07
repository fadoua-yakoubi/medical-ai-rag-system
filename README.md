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

## 📋 Project Structure

```
Gen-ai-project/
├── app.py                          # Main Streamlit web interface
├── requirements.txt                # Python dependencies
├── .env                            # Configuration (credentials)
├── README.md                       # This file
└── src/
    ├── __init__.py
    ├── crew.py                     # CrewAI orchestration (2 agents)
    ├── rag_tool.py                 # GraphRAG tool + language detection
    ├── rag_etl.py                  # ETL script for database population
    └── RAG Graph/
        └── medical_data.json       # Medical knowledge base (14 diseases)
```

## ⚡ Quick Start

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
Format Answer in Same Language (FR/EN)
    ↓
Display in Streamlit
```

## 📊 Database Schema

### Knowledge Graph Contents
- **14 Diseases** (Diabète type 2, Hypertension, Asthma, Anemia, etc.)
- **109 Symptoms** (Fatigue, Fever, Cough, Headache, etc.)
- **92 Treatments** (Metformin, Ventoline, Antibiotics, etc.)
- **92 Causes** (Obesity, Insulin resistance, Virus, etc.)
- **293 Relationships** (HAS_SYMPTOM, TREATED_WITH, CAUSED_BY)

### Node Types

**Disease**
```
(:Disease {name: "Diabète type 2"})
```

**Symptom**
```
(:Symptom {name: "Fatigue"})
```

**Treatment**
```
(:Treatment {name: "Metformin"})
```

**Cause**
```
(:Cause {name: "Insulin resistance"})
```

### Relationship Types

```
(disease:Disease)-[:HAS_SYMPTOM]->(symptom:Symptom)
(disease:Disease)-[:TREATED_WITH]->(treatment:Treatment)
(disease:Disease)-[:CAUSED_BY]->(cause:Cause)
```

## 🌐 Language Support

The system automatically detects the language of input questions:

### Detection Keywords
**French 🇫🇷**: je, mon, ma, symptôme, maladie, traitement, cause, avoir, souffrir, etc.
**English 🇬🇧**: i, my, disease, symptom, treatment, cause, have, suffer, etc.

### Response Language
The system responds entirely in the detected language, using appropriate terminology and formatting.

## 🧠 How GraphRAG Works

### Step 1: Cypher Generation
```
Input: "What are the symptoms of diabetes?"
LLM generates:
MATCH (d:Disease {name: "Diabetes"})-[:HAS_SYMPTOM]->(s:Symptom)
RETURN d.name as disease, collect(s.name) as symptoms
```

### Step 2: Neo4j Query
```
Executes Cypher query against Neo4j graph database
Returns structured results with all matching nodes
```

### Step 3: QA Transformation
```
Converts raw query results into natural language explanation
Adds context from symptoms, treatments, and causes
Formats for patient understanding
```

## 📈 Key Components

### rag_tool.py
The core GraphRAG tool with the following methods:
- `_init_graph()` - Initialize Neo4j connection
- `_init_llm()` - Create Groq LLM instance
- `_init_rag_chain()` - Build GraphCypherQAChain
- `_run(query)` - Execute full RAG pipeline
- `detect_language(text)` - Auto-detect FR/EN

### rag_etl.py
Populates the Neo4j database:
- Reads medical_data.json
- Creates Disease, Symptom, Treatment, Cause nodes
- Establishes HAS_SYMPTOM, TREATED_WITH, CAUSED_BY relationships
- Supports URL-based Neo4j (AuraDB compatible)

### crew.py
CrewAI orchestration:
- Diagnostician Agent: Queries knowledge graph
- Explainer Agent: Formats results for users
- Sequential process flow

### app.py
Streamlit web interface:
- Question input area
- Real-time analysis spinner
- Formatted output display
- API key configuration
- Expandable raw output section

## 🛠️ Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | CrewAI ≥0.30.0 | Multi-agent coordination |
| **LLM Framework** | LangChain ≥0.2.0 | RAG and prompting |
| **Graph Database** | Neo4j ≥5.20.0 | Knowledge storage |
| **LLM Provider** | Groq API | Fast inference |
| **Web Framework** | Streamlit ≥1.35.0 | User interface |
| **Graph Tools** | LangChain Neo4j ≥0.0.1 | Neo4j integration |
| **Language Detection** | TextBlob ≥0.17.0 | FR/EN detection |

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named..."**
```bash
pip install -r requirements.txt --upgrade
```

**"Neo4j Connection Error"**
- Verify .env credentials
- Check NEO4J_URI format (neo4j+s:// for cloud)
- Ensure Neo4j instance is running

**"Groq API Key Invalid"**
- Get a free key at https://console.groq.com
- Verify key in .env file
- Check free tier limits (30 req/min)

**"Streamlit command not found"**
```bash
.\venv\Scripts\python -m streamlit run app.py
```

## ⚠️ Disclaimer

**Educational Use Only** - This system is for learning purposes. Do not use for real medical diagnosis. Always consult qualified healthcare professionals.

## 📚 Database Population

First-time setup automatically populates the database:

```bash
.\venv\Scripts\python src/rag_etl.py
```

This creates:
- 14 diseases with full metadata
- 109 symptoms across all diseases
- 92 treatments per disease
- 92 causes per disease
- Complete relationship graph

## 🚀 Performance Metrics

- **Response Time**: 10-15 seconds per question
- **Database Size**: ~50KB
- **Query Rate**: 30 req/min (Groq free tier)
- **Supported Languages**: French, English (easily extensible)
- **Accuracy**: High for medical knowledge retrieval

## 📞 Support & Documentation

For detailed troubleshooting, check:
1. Groq API status: https://console.groq.com
2. Neo4j AuraDB dashboard: https://console.neo4j.io
3. CrewAI documentation: https://docs.crewai.com
4. LangChain documentation: https://python.langchain.com

## 🔮 Future Enhancements

- [ ] Add 100+ more diseases
- [ ] Support 5+ additional languages
- [ ] Implement confidence scoring
- [ ] Add graph visualization
- [ ] Mobile app development
- [ ] Voice input/output support
- [ ] Patient history tracking
- [ ] Integration with medical APIs

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**License**: Educational Use Only

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

## 🤖 Choix Techniques

### Pourquoi Groq + Llama 3.3 70B?
- ✅ **Gratuit**: Pas de coût d'API (vs GPT-4 ~$0.03/1K tokens)
- ✅ **Rapide**: <1s de latence (vs 3-5s pour GPT-4)
- ✅ **Performance**: Llama 3.3 70B rivalise avec GPT-4
- ⚠️ **Limite**: Rate limiting sur free tier (géré avec retries + timeouts)

### Pourquoi Neo4j?
- ✅ **Graph Database native**: Parfait pour relations symptômes-maladies
- ✅ **Cypher Query Language**: Requêtes naturelles et expressives
- ✅ **AuraDB Free**: 200K nodes/400K relationships gratuit
- ✅ **Extensible**: Facile d'ajouter maladies/symptômes

### Architecture Agents (CrewAI):
- **Sequential Process**: Diagnostician → Explainer
- **max_iter=3**: Limite tool calls pour éviter rate limits
- **max_tokens=4000**: Optimisé pour Groq free tier
- **Retry logic**: 3 tentatives avec backoff pour gérer rate limits
- **Normalisation des symptômes**: Retire modificateurs ("severe", "high") automatiquement

## 🔧 Troubleshooting

### "Model not found: llama-3.x-xxb-instant"
**Cause**: Nom de modèle incorrect ou indisponible
**Solution**: 
- Vérifiez les modèles disponibles sur https://console.groq.com
- Modèles courants: `llama-3.3-70b-versatile`, `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`
- Mettez à jour `GOOGLE_MODEL_NAME` dans `.env`

### "Invalid response from LLM call - None or empty"
**Cause**: Rate limiting Groq (free tier)
**Solution**: 
- Attendez 30-60 secondes entre requêtes
- Le code inclut déjà `max_retries=3` et `request_timeout=90s`
- Réduisez `max_iter` si nécessaire

### "Graph Context: []" ou mauvais résultats
**Cause**: Symptômes avec modificateurs non reconnus ("severe headache" vs "headache")
**Solution**: 
- La **normalisation automatique** est maintenant active dans `tools.py`
- Le système retire automatiquement "severe", "high", "bad", etc.
- Enrichissez la base avec `python enrich_database.py`

### Dependences Conflicts
**json-repair**: Utilisez version `0.25.2` (pas 0.54.2)
```bash
pip install json-repair==0.25.2
```

## 📁 Structure du Projet

```
medical_graph_rag/
├── app.py                  # Interface Streamlit principale
├── src/
│   ├── crew.py            # Configuration CrewAI (agents + tasks)
│   ├── tools.py           # Medical Graph Search tool (GraphCypherQAChain + normalisation)
│   └── graph.py           # Neo4j connection + seed_db()
├── requirements.txt       # Dépendances Python
├── .env                   # Configuration (API keys, Neo4j credentials)
├── enrich_database.py     # Script pour enrichir avec 12 maladies et 35+ symptômes
├── reseed.py             # Script pour nettoyer et repeupler Neo4j (ancienne base)
└── README.md             # Documentation

Scripts utilitaires:
├── check_db.py           # Vérifie l'état de Neo4j
└── test_queries.py       # Teste les requêtes Cypher
```

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

## 📈 Évolutions Futures

### Améliorations Techniques:
- [x] Normalisation automatique des symptômes (modificateurs)
- [x] Base de données enrichie (12 maladies, 35+ symptômes)
- [ ] Ajouter propriétés aux maladies (durée, traitement recommandé)
- [ ] Supporter les requêtes en français (actuellement en anglais)

### Optimisations Performance:
- [ ] Caching des requêtes Cypher fréquentes
- [ ] Batch processing pour multiple symptom queries
- [ ] Fallback vers autre LLM si Groq rate limit

### Features:
- [ ] Historique des diagnostics
- [ ] Export PDF du rapport médical
- [ ] Graphe de visualisation Neo4j dans l'UI
- [ ] Ajout de tests et gravité des symptômes

## 📚 Ressources

- [Groq Documentation](https://console.groq.com/docs)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [CrewAI Documentation](https://docs.crewai.com)
- [LangChain GraphCypherQAChain](https://python.langchain.com/docs/use_cases/graph/graph_cypher_qa)

## ⚠️ Disclaimer

Ce projet est **à but éducatif uniquement**. Il ne remplace pas un avis médical professionnel. Consultez toujours un médecin pour un diagnostic réel.

## 📝 Notes de Développement

### Historique des Changements:
- **v1.0**: Version initiale avec Google Gemini (abandonné - quota épuisé)
- **v2.0**: Migration vers Groq + Llama 3.1 8B Instant
- **v2.1**: Fix symptom case sensitivity (lowercase dans Neo4j)
- **v2.2**: Fix intermediate_steps parsing (liste de 2 dicts séparés)
- **v2.3**: Optimisation rate limits (max_iter=3, max_tokens=4000)

### Défis Résolus:
1. **Dependency Conflicts**: `json-repair` downgrade à 0.25.2
2. **Empty Graph Results**: Symptômes en lowercase requis
3. **LLM Empty Responses**: Rate limiting Groq → ajout retry logic
4. **CrewAI Provider Detection**: Override OPENAI_API_BASE vers Groq

---

**Développé avec ❤️ en utilisant 100% d'outils gratuits**
```
