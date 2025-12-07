from crewai.tools import BaseTool
from pydantic import Field
from .graph import get_graph_db
import os
import re

class GraphSearchToolInput(BaseTool):
    """Input for GraphSearchTool."""
    query: str = Field(..., description="The natural language query to ask the medical knowledge graph.")

class MedicalGraphSearchTool(BaseTool):
    name: str = "Medical Graph Search"
    description: str = (
        "Useful for answering questions about medical symptoms and diseases by querying a Neo4j graph database. "
        "Input should be a natural language question like 'What disease has symptoms of fever and cough?'"
    )
    
    def _normalize_symptoms(self, text: str) -> str:
        """Normalise les symptômes en retirant les modificateurs."""
        symptom_mappings = {
            r'\b(high|severe|bad|terrible|awful|extreme|intense)\s+fever\b': 'fever',
            r'\b(dry|persistent|chronic)\s+cough\b': 'dry cough',
            r'\b(?:regular|wet|productive)\s+cough\b': 'cough',
            r'\b(severe|bad|terrible|awful)\s+headache\b': 'headache',
            r'\b(severe|bad|terrible|awful|intense)\s+stomach pain\b': 'stomach pain',
            r'\b(severe|bad|chronic)\s+diarrhea\b': 'diarrhea',
            r'\b(very|really|extremely)\s+dizzy\b': 'dizziness',
            r'\b(very|extremely)\s+weak\b': 'weakness',
            r'\b(severe|bad)\s+nausea\b': 'nausea',
            r'\b(severe|bad)\s+sore throat\b': 'sore throat',
            r'\b(stuffy|blocked)\s+nose\b': 'nasal congestion',
            r'\bshortness of breath\b': 'shortness of breath',
            r'\bcan\'t breathe well\b': 'shortness of breath',
            r'\bdifficulty breathing\b': 'shortness of breath',
            r'\bstomach ache\b': 'stomach pain',
        }
        
        normalized = text.lower()
        for pattern, replacement in symptom_mappings.items():
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized
    
    def _extract_symptoms(self, text: str) -> list:
        """Extract symptom words from user input."""
        normalized = self._normalize_symptoms(text)
        
        # List of all known symptoms in the database
        known_symptoms = [
            'fever', 'cough', 'dry cough', 'sore throat', 'runny nose', 
            'nasal congestion', 'shortness of breath', 'chest pain', 'wheezing', 
            'fatigue', 'headache', 'body aches', 'muscle pain', 'chills', 
            'sweating', 'weakness', 'loss of appetite', 'nausea', 'vomiting', 
            'diarrhea', 'stomach pain', 'abdominal cramps', 'dizziness', 
            'confusion', 'loss of taste', 'loss of smell', 'rash', 'itching', 
            'skin redness', 'ear pain', 'sinus pressure', 'sneezing', 'watery eyes'
        ]
        
        # Find symptoms mentioned in the text
        found_symptoms = []
        for symptom in known_symptoms:
            if symptom.lower() in normalized:
                found_symptoms.append(symptom)
        
        return found_symptoms

    def _run(self, query: str) -> str:
        """Execute graph search with direct Cypher query."""
        try:
            graph = get_graph_db()
            
            # Extract symptoms from user input
            symptoms = self._extract_symptoms(query)
            
            if not symptoms:
                return "No recognized symptoms found. Please mention symptoms like fever, cough, sore throat, etc."
            
            # Build Cypher query directly - no LLM needed
            symptoms_str = "', '".join(symptoms)
            cypher_query = f"""
            MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
            WHERE s.name IN ['{symptoms_str}']
            RETURN DISTINCT d.name as disease, COUNT(s) as matching_symptoms
            ORDER BY matching_symptoms DESC
            """
            
            # Execute query
            result = graph.query(cypher_query)
            
            if not result:
                return f"No diseases found matching symptoms: {', '.join(symptoms)}"
            
            # Format results
            diseases = [row['disease'] for row in result]
            unique_diseases = list(dict.fromkeys(diseases))  # Remove duplicates, preserve order
            
            output = f"""Medical Graph Search Results:

Symptoms Found: {', '.join(symptoms)}

Matching Diseases:
{', '.join(unique_diseases)}

Number of matching diseases: {len(unique_diseases)}
"""
            return output
            
        except Exception as e:
            import traceback
            return f"Error querying graph: {str(e)}\n{traceback.format_exc()}"

