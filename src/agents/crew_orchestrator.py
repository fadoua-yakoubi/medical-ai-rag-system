from crewai import Task, Crew, Process, LLM
from .medical_diagnostician import MedicalDiagnostician
from .medical_explainer import MedicalExplainer
from ..models.groq_llm import GroqLLM

class MedicalCrewOrchestrator:
    """Orchestre les agents avec Groq via LiteLLM."""
    
    def __init__(self):
        groq = GroqLLM()
        
        # ✅ Utiliser LLM de CrewAI avec LiteLLM
        self.llm = LLM(
            model=groq.get_model_name(),  # "groq/llama-3.3-70b-versatile"
            api_key=groq.api_key,
            temperature=0.3
        )
        
        # Passer le LLM aux agents
        self.diagnostician = MedicalDiagnostician(self.llm).create_agent()
        self.explainer = MedicalExplainer(self.llm).create_agent()
    
    def run(self, symptoms: str) -> str:
        """Exécute le workflow complet."""
        
        diagnosis_task = Task(
            description=(
                f"Use Medical RAG to find diseases matching: {symptoms}. "
                "Extract diseases, symptoms, treatments, and causes."
            ),
            expected_output="Complete diagnostic: diseases, symptoms, treatments, causes",
            agent=self.diagnostician
        )
        
        explanation_task = Task(
            description=(
                "Create structured explanation with: "
                "1) Diseases 2) Symptom correlation 3) Treatments 4) Causes 5) Confidence"
            ),
            expected_output="Clear medical explanation with all diagnostic elements",
            agent=self.explainer,
            context=[diagnosis_task]
        )
        
        crew = Crew(
            agents=[self.diagnostician, self.explainer],
            tasks=[diagnosis_task, explanation_task],
            process=Process.sequential,
            verbose=True,
            memory=False
        )
        
        result = crew.kickoff()
        return str(result)