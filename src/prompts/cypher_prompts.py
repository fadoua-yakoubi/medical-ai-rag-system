from langchain_core.prompts import PromptTemplate

def get_cypher_generation_prompt() -> PromptTemplate:
    """Retourne le prompt de génération Cypher."""
    return PromptTemplate(
        input_variables=["schema", "question"],
        template="""
You are an expert Neo4j Cypher query generator for medical diagnosis.

STRICT RULES:
1. Use LOWERCASE relationship names: HAS_SYMPTOM, TREATED_WITH, CAUSED_BY
2. Use UPPERCASE node labels: Disease, Symptom, Treatment, Cause
3. Return DISTINCT results
4. Match symptoms first, then find related diseases

Schema:
{schema}

Question:
{question}

Generate ONLY the Cypher query:
"""
    )