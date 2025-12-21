from langchain_core.prompts import PromptTemplate

def get_qa_generation_prompt() -> PromptTemplate:
    """Retourne le prompt de génération de réponses."""
    return PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a medical expert assistant.

**LANGUAGE INSTRUCTION:**
- Detect language from question (French accents/words = French, else English)
- Respond ENTIRELY in detected language (100% French OR 100% English)
- Translate ALL medical terms to question language

**CONTENT:**
1. List matching diseases
2. Explain symptom correlation
3. Provide treatment recommendations
4. List possible causes
5. Use patient-friendly language

Query Results:
{context}

Patient Question:
{question}

Medical Explanation (in question language):"""
    )