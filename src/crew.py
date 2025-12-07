from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from .rag_tool import MedicalRAGTool
import os

class MedicalCrew:
    def __init__(self):
        # Configure LLM explicitly for Groq using ChatOpenAI
        self.llm = ChatOpenAI(
            model=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            temperature=0.3,
            max_tokens=4000,
            request_timeout=90,
            max_retries=3
        )

    def run(self, symptoms: str):
        # 1. Define Agents
        diagnostician = Agent(
            role='Medical Diagnostician',
            goal='Find diseases matching patient symptoms using the advanced medical knowledge graph with GraphRAG.',
            backstory="You are a medical expert who uses the RAG system to query a graph database to match symptoms with diseases, treatments, and causes.",
            tools=[MedicalRAGTool()],
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
            max_iter=3,
            max_rpm=10,
            max_execution_time=120
        )

        explainer = Agent(
            role='Medical Explainer',
            goal='Explain the RAG diagnostic results in clear, patient-friendly language with structured information.',
            backstory="You translate medical findings from the RAG system into easy-to-understand explanations for patients, including treatments and causes.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
            max_iter=5
        )

        # 2. Define Tasks
        diagnosis_task = Task(
            description=(
                f"Use the Medical RAG Graph Search tool to query the medical knowledge graph for diseases matching these symptoms: {symptoms}. "
                "The tool will return: diseases, associated symptoms, treatments, and causes. "
                "Extract and report all findings from the RAG results."
            ),
            expected_output=(
                "Complete diagnostic information including: diseases found, matching symptoms, recommended treatments, and possible causes"
            ),
            agent=diagnostician
        )

        explanation_task = Task(
            description=(
                "Review the RAG diagnostic results and create a clear, structured explanation. "
                "Include: 1) Which diseases match 2) Why they match (symptom correlation) 3) Recommended treatments 4) Possible causes 5) Confidence level"
            ),
            expected_output=(
                "A structured medical explanation with disease names, symptom reasoning, treatments, causes, and confidence assessment."
            ),
            agent=explainer,
            context=[diagnosis_task]
        )

        # 3. Create Crew
        crew = Crew(
            agents=[diagnostician, explainer],
            tasks=[diagnosis_task, explanation_task],
            process=Process.sequential,
            verbose=True,
            memory=False # Disable memory to avoid OpenAI Embeddings dependency
        )

        result = crew.kickoff()
        return result
