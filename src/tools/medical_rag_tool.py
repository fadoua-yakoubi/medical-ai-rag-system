from crewai.tools import BaseTool
from pydantic import Field
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from typing import Any
from ..database.neo4j_connector import Neo4jConnector
from ..models.groq_llm import GroqLLM
from ..prompts.cypher_prompts import get_cypher_generation_prompt
from ..prompts.qa_prompts import get_qa_generation_prompt
from .language_detector import LanguageDetector

class MedicalRAGTool(BaseTool):
    """Tool RAG pour interroger le graphe médical."""
    
    name: str = "Medical RAG Graph Search"
    description: str = (
        "Advanced RAG tool for medical knowledge graph queries. "
        "Returns diseases, symptoms, treatments, and causes."
    )
    
    graph: Any = Field(default=None)
    llm: Any = Field(default=None)
    qa_chain: Any = Field(default=None)
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.graph is None:
            self.graph = Neo4jConnector().get_graph()
        if self.llm is None:
            self.llm = GroqLLM().get_llm()
        if self.qa_chain is None:
            self.qa_chain = self._init_rag_chain()
    
    def _init_rag_chain(self) -> GraphCypherQAChain:
        """Initialise GraphCypherQAChain."""
        qa_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            cypher_prompt=get_cypher_generation_prompt(),
            qa_prompt=get_qa_generation_prompt(),
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
            top_k=10
        )
        return qa_chain
    
    def _run(self, query: str) -> str:
        """Exécute la recherche RAG."""
        try:
            # Détection langue
            lang = LanguageDetector.detect(query)
            
            # Invoke RAG
            response = self.qa_chain.invoke({"query": query})
            answer = response.get("result", "No answer")
            
            # Extraction données graphe
            intermediate_steps = response.get("intermediate_steps", [])
            graph_info = self._extract_graph_data(intermediate_steps)
            
            # Format résultat selon langue
            return self._format_output(answer, graph_info, lang)
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _extract_graph_data(self, steps: list) -> dict:
        """Extrait les données du graphe."""
        result = {
            "cypher_query": "",
            "diseases": [],
            "symptoms": [],
            "treatments": [],
            "causes": []
        }
        
        for step in steps:
            if isinstance(step, dict):
                if "query" in step:
                    result["cypher_query"] = step.get("query", "")
                
                if "context" in step:
                    context_data = step.get("context", [])
                    for row in context_data:
                        if isinstance(row, dict):
                            # Extraire diseases, symptoms, treatments, causes
                            disease = row.get("disease") or row.get("d.name")
                            if disease:
                                result["diseases"].append(disease)
                            
                            symptom = row.get("symptom") or row.get("s.name")
                            if symptom:
                                result["symptoms"].append(symptom)
                            
                            treatment = row.get("treatment") or row.get("t.name")
                            if treatment:
                                result["treatments"].append(treatment)
                            
                            cause = row.get("cause") or row.get("c.name")
                            if cause:
                                result["causes"].append(cause)
        
        # Retirer doublons
        result["diseases"] = list(set(result["diseases"]))
        result["symptoms"] = list(set(result["symptoms"]))
        result["treatments"] = list(set(result["treatments"]))
        result["causes"] = list(set(result["causes"]))
        
        return result
    
    def _format_output(self, answer: str, graph_info: dict, lang: str) -> str:
        """Formate la sortie selon la langue."""
        labels = self._get_labels(lang)
        
        output = f"""
{labels['title']}

{labels['answer']}
{answer}

{labels['diseases']} {', '.join(graph_info['diseases']) or labels['none']}
{labels['symptoms']} {', '.join(graph_info['symptoms']) or labels['none']}
{labels['treatments']} {', '.join(graph_info['treatments']) or labels['none']}
{labels['causes']} {', '.join(graph_info['causes']) or labels['none']}
        """
        return output
    
    def _get_labels(self, lang: str) -> dict:
        """Retourne les labels traduits."""
        if lang == 'fr':
            return {
                'title': '🏥 RÉSULTATS DIAGNOSTIC',
                'answer': '📋 Réponse:',
                'diseases': '🦠 Maladies:',
                'symptoms': '🔴 Symptômes:',
                'treatments': '💊 Traitements:',
                'causes': '⚠️ Causes:',
                'none': 'Aucun'
            }
        return {
            'title': '🏥 DIAGNOSTIC RESULTS',
            'answer': '📋 Answer:',
            'diseases': '🦠 Diseases:',
            'symptoms': '🔴 Symptoms:',
            'treatments': '💊 Treatments:',
            'causes': '⚠️ Causes:',
            'none': 'None'
        }