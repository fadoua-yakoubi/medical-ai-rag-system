"""
rag_tool.py - Tool RAG avancé pour CrewAI
Intègre GraphCypherQAChain avec Groq LLM
Supporte multilingue: détecte la langue et répond dans la même langue
Retourne: Réponse textuelle + Chemin graphe + Traitements + Causes
"""
from crewai.tools import BaseTool
from pydantic import Field
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
import os
import re
from dotenv import load_dotenv
from typing import Any

load_dotenv()

def detect_language(text: str) -> str:
    """
    Détecte la langue du texte (français, anglais, etc.)
    Retourne: 'fr', 'en', etc.
    Priorité: Cherche d'abord les accents français
    """
    text_lower = text.lower()
    
    # Caractères accents français (très spécifiques) - PRIORITAIRE
    if any(char in text_lower for char in ['é', 'è', 'ê', 'ë', 'à', 'â', 'ä', 'ù', 'û', 'ü', 'ç', 'ô', 'ö', 'î', 'ï']):
        return 'fr'
    
    # Mots français courants (sans accents)
    french_keywords = ['je', 'mon', 'ma', 'mes', 'le', 'la', 'les', 'de', 'du', 'a', 'que', 'quoi', 'quelle', 'comment', 'pourquoi', 'symptome', 'maladie', 'traitement', 'cause', 'avoir', 'souffrir', 'malade', 'j ai', 'quels', 'qu est']
    # Mots anglais courants
    english_keywords = ['i', 'my', 'the', 'a', 'is', 'are', 'have', 'disease', 'symptom', 'treatment', 'cause', 'what', 'which', 'how', 'why', 'affected', 'suffer']
    
    french_count = sum(1 for word in french_keywords if word in text_lower)
    english_count = sum(1 for word in english_keywords if word in text_lower)
    
    if french_count >= english_count:
        return 'fr'
    else:
        return 'en'

def get_translations(lang: str) -> dict:
    """
    Retourne les traductions des labels selon la langue.
    """
    if lang == 'fr':
        return {
            'title': '🏥 RÉSULTATS DIAGNOSTIC RAG MÉDICAL',
            'answer': '📋 Réponse Principale:',
            'query': '🔍 Requête Graphe Utilisée:',
            'diseases': '🦠 Maladies Trouvées:',
            'symptoms': '🔴 Symptômes Associés:',
            'treatments': '💊 Traitements Recommandés:',
            'causes': '⚠️ Causes Possibles:',
            'raw': 'Données Graphe Brutes',
            'none': 'Aucun',
            'results': 'résultats'
        }
    else:
        return {
            'title': '🏥 MEDICAL RAG DIAGNOSTIC RESULTS',
            'answer': '📋 Primary Answer:',
            'query': '🔍 Graph Query Used:',
            'diseases': '🦠 Diseases Found:',
            'symptoms': '🔴 Associated Symptoms:',
            'treatments': '💊 Recommended Treatments:',
            'causes': '⚠️ Possible Causes:',
            'raw': 'Raw Graph Data',
            'none': 'None',
            'results': 'results'
        }

class MedicalRAGTool(BaseTool):
    """
    Tool RAG avancé pour diagnostiquer maladies basé sur symptômes
    Utilise GraphCypherQAChain avec Groq LLM
    """
    name: str = "Medical RAG Graph Search"
    description: str = (
        "Outil RAG avancé pour interroger le graphe de connaissances médicales. "
        "Retourne maladies, symptômes, traitements et causes. "
        "Input: description des symptômes (ex: 'fever and sore throat')"
    )
    
    # Attributs pour le fonctionnement interne
    graph: Any = Field(default=None, description="Neo4j graph connection")
    llm: Any = Field(default=None, description="Groq LLM instance")
    qa_chain: Any = Field(default=None, description="GraphCypherQAChain instance")
    detected_language: str = Field(default="en", description="Detected language of the query")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.graph is None:
            self.graph = self._init_graph()
        if self.llm is None:
            self.llm = self._init_llm()
        if self.qa_chain is None:
            self.qa_chain = self._init_rag_chain()
    
    def _init_graph(self) -> Neo4jGraph:
        """Initialise connexion Neo4j."""
        try:
            graph = Neo4jGraph(
                url=os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
                username=os.getenv("NEO4J_USERNAME", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "")
            )
            graph.refresh_schema()
            return graph
        except Exception as e:
            raise Exception(f"Erreur connexion Neo4j: {e}")
    
    def _init_llm(self) -> ChatOpenAI:
        """Initialise Groq LLM."""
        return ChatOpenAI(
            model=os.getenv("GOOGLE_MODEL_NAME", "llama-3.3-70b-versatile"),
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            temperature=0,
            max_tokens=2000,
            request_timeout=60,
            max_retries=3
        )
    
    def _init_rag_chain(self) -> GraphCypherQAChain:
        """Initialise GraphCypherQAChain avec prompts personnalisés."""
        
        cypher_generation_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template="""
You are an expert Neo4j Cypher query generator for medical diagnosis.

STRICT RULES:
1. Use LOWERCASE relationship names: HAS_SYMPTOM, TREATED_WITH, CAUSED_BY
2. Use UPPERCASE node labels: Disease, Symptom, Treatment, Cause
3. Return DISTINCT results to avoid duplicates
4. Match symptoms first, then find diseases with those symptoms
5. Include treatments and causes in the results when relevant

Schema:
{schema}

Medical Question:
{question}

Generate ONLY the Cypher query, no explanation:
"""
        )
        
        qa_generation_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a medical expert assistant. Transform Neo4j query results into a clear medical explanation.

**LANGUAGE INSTRUCTION - CRITICAL AND MANDATORY:**
1. Detect the language of the patient question by looking for French accents or words
2. If French is detected (accents: é, è, ê, à, â, ù, ç OR words: je, mon, ma, symptôme, maladie, traitement): Respond ENTIRELY IN FRENCH ONLY
3. If English is detected: Respond ENTIRELY IN ENGLISH ONLY
4. DO NOT MIX LANGUAGES - Response must be 100% in one language

**IF QUESTION IS IN FRENCH:**
- Translate ALL disease names to French
- Translate ALL symptom descriptions to French  
- Translate ALL treatments to French
- Translate ALL causes to French
- Use French medical terminology ONLY
- NO ENGLISH WORDS ALLOWED

**IF QUESTION IS IN ENGLISH:**
- Use English medical terminology
- Keep everything in English

CONTENT INSTRUCTIONS:
1. Extract and list the diseases that match
2. Explain why they match the symptoms
3. Provide treatment recommendations
4. List possible causes
5. Use clear, patient-friendly language

Query Results from Medical Knowledge Graph:
{context}

Patient Question (Detect language from this):
{question}

Medical Explanation (MUST be 100% in question language - All French if French detected, All English if English detected):"""
        )
        
        qa_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            cypher_prompt=cypher_generation_prompt,
            qa_prompt=qa_generation_prompt,
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
            top_k=10  # Limiter résultats
        )
        return qa_chain
    
    def _extract_graph_path(self, intermediate_steps: list) -> dict:
        """
        Extrait le chemin graphe des étapes intermédiaires.
        Retourne: {
            "cypher_query": "...",
            "graph_results": [...],
            "diseases": [...],
            "symptoms": [...],
            "treatments": [...],
            "causes": [...]
        }
        """
        result = {
            "cypher_query": "",
            "graph_results": [],
            "diseases": [],
            "symptoms": [],
            "treatments": [],
            "causes": []
        }
        
        try:
            for step in intermediate_steps:
                # Récupérer requête Cypher
                if isinstance(step, dict) and "query" in step:
                    result["cypher_query"] = step.get("query", "")
                
                # Récupérer résultats graphe
                if isinstance(step, dict) and "context" in step:
                    context_data = step.get("context", [])
                    
                    if isinstance(context_data, list):
                        result["graph_results"] = context_data
                        
                        # Parser les résultats
                        for row in context_data:
                            if isinstance(row, dict):
                                # Diseases
                                disease = row.get("disease") or row.get("d.name") or row.get("Disease")
                                if disease and disease not in result["diseases"]:
                                    result["diseases"].append(disease)
                                
                                # Symptoms
                                symptom = row.get("symptom") or row.get("s.name") or row.get("Symptom")
                                if symptom and symptom not in result["symptoms"]:
                                    result["symptoms"].append(symptom)
                                
                                # Treatments
                                treatment = row.get("treatment") or row.get("t.name") or row.get("Treatment")
                                if treatment and treatment not in result["treatments"]:
                                    result["treatments"].append(treatment)
                                
                                # Causes
                                cause = row.get("cause") or row.get("c.name") or row.get("Cause")
                                if cause and cause not in result["causes"]:
                                    result["causes"].append(cause)
        except Exception as e:
            print(f"⚠️ Erreur extraction chemin graphe: {e}")
        
        return result
    
    def _run(self, query: str) -> str:
        """
        Exécute la chaîne RAG et retourne réponse structurée.
        Détecte la langue et répond dans la même langue.
        """
        try:
            # Détecter la langue de la question
            lang = detect_language(query)
            self.detected_language = lang
            
            # Invoke RAG chain
            response = self.qa_chain.invoke({"query": query})
            
            # Résultats principaux
            answer = response.get("result", "No answer generated")
            intermediate_steps = response.get("intermediate_steps", [])
            
            # Extraire chemin graphe et composants
            graph_info = self._extract_graph_path(intermediate_steps)
            
            # Format des labels selon la langue
            if lang == 'fr':
                labels = {
                    'title': '🏥 RÉSULTATS DIAGNOSTIC RAG MÉDICAL',
                    'answer': '📋 Réponse Principale:',
                    'query': '🔍 Requête Graphe Utilisée:',
                    'diseases': '🦠 Maladies Trouvées:',
                    'symptoms': '🔴 Symptômes Associés:',
                    'treatments': '💊 Traitements Recommandés:',
                    'causes': '⚠️ Causes Possibles:',
                    'raw': 'Données Graphe Brutes',
                    'none': 'Aucun'
                }
            else:
                labels = {
                    'title': '🏥 MEDICAL RAG DIAGNOSTIC RESULTS',
                    'answer': '📋 Primary Answer:',
                    'query': '🔍 Graph Query Used:',
                    'diseases': '🦠 Diseases Found:',
                    'symptoms': '🔴 Associated Symptoms:',
                    'treatments': '💊 Recommended Treatments:',
                    'causes': '⚠️ Possible Causes:',
                    'raw': 'Raw Graph Data',
                    'none': 'None'
                }
            
            # Construire résultat structuré dans la bonne langue
            output = f"""
{labels['title']}

{labels['answer']}
{answer}

{labels['query']}
{graph_info['cypher_query'][:500]}...

{labels['diseases']} {', '.join(graph_info['diseases']) if graph_info['diseases'] else labels['none']}
{labels['symptoms']} {', '.join(graph_info['symptoms']) if graph_info['symptoms'] else labels['none']}
{labels['treatments']} {', '.join(graph_info['treatments']) if graph_info['treatments'] else labels['none']}
{labels['causes']} {', '.join(graph_info['causes']) if graph_info['causes'] else labels['none']}

{labels['raw']} ({len(graph_info['graph_results'])} résultats):
{graph_info['graph_results']}
            """
            
            return output
        
        except Exception as e:
            import traceback
            lang = detect_language(query)
            if lang == 'fr':
                error_msg = f"""
❌ ERREUR dans la Recherche RAG Médicale:
{str(e)}

Traceback:
{traceback.format_exc()}
                """
            else:
                error_msg = f"""
❌ ERROR in Medical RAG Search:
{str(e)}

Traceback:
{traceback.format_exc()}
                """
            return error_msg
