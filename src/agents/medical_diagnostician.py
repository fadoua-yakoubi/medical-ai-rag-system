from ..tools.medical_rag_tool import MedicalRAGTool
from langchain_groq import ChatGroq 

from crewai import Agent, LLM
from ..tools.medical_rag_tool import MedicalRAGTool

class MedicalDiagnostician:
    def __init__(self, llm: LLM):  # ✅ Type CrewAI LLM
        self.llm = llm
        self.tool = MedicalRAGTool()
    
    def create_agent(self) -> Agent:
        return Agent(
            role='Medical Diagnostician',
            goal='Find diseases matching patient symptoms using GraphRAG',
            backstory="Medical expert using graph database for diagnosis",
            tools=[self.tool],
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
            max_iter=3
        )
