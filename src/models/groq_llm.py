import os
from langchain_groq import ChatGroq
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

class GroqLLM:
    """Configure et retourne le LLM Groq avec support CrewAI."""
    
    def __init__(self):
        self.model = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY manquant dans .env")
        
        os.environ["GROQ_API_KEY"] = self.api_key
        
        print(f"\n{'='*60}")
        print(f"🔑 GroqLLM initialized with LiteLLM:")
        print(f"  Model: groq/{self.model}")
        print(f"  API Key: {self.api_key[:15]}...{self.api_key[-4:]}")
        print(f"{'='*60}\n")
    
    def get_llm(self):
        """Retourne une instance ChatGroq compatible CrewAI."""
        return ChatGroq(
            model=self.model,
            api_key=self.api_key,
            temperature=0.3,
            max_tokens=4000,
            timeout=90,
            max_retries=3
        )
    
    def get_model_name(self) -> str:
        """Retourne le nom du modèle pour LiteLLM."""
        return f"groq/{self.model}"