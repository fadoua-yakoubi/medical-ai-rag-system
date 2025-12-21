from crewai import Agent
from langchain_groq import ChatGroq 
from crewai import Agent, LLM

class MedicalExplainer:
    def __init__(self, llm: LLM):  # ✅ Type CrewAI LLM
        self.llm = llm
    
    def create_agent(self) -> Agent:
        return Agent(
            role='Medical Explainer',
            goal='Explain diagnostic results in patient-friendly language',
            backstory="Medical communicator translating findings for patients",
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
            max_iter=5
        )