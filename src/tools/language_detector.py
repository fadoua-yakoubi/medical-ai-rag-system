class LanguageDetector:
    """Détecte la langue d'un texte (français ou anglais)."""
    
    FRENCH_CHARS = ['é', 'è', 'ê', 'ë', 'à', 'â', 'ä', 'ù', 'û', 'ü', 'ç', 'ô', 'ö', 'î', 'ï']
    
    FRENCH_KEYWORDS = [
        'je', 'mon', 'ma', 'mes', 'le', 'la', 'les', 'de', 'du', 'que', 
        'symptome', 'maladie', 'traitement', 'cause', 'avoir', 'souffrir'
    ]
    
    ENGLISH_KEYWORDS = [
        'i', 'my', 'the', 'a', 'is', 'disease', 'symptom', 
        'treatment', 'cause', 'what', 'have'
    ]
    
    @classmethod
    def detect(cls, text: str) -> str:
        """
        Détecte la langue du texte.
        Returns: 'fr' ou 'en'
        """
        text_lower = text.lower()
        
        # Priorité aux accents français
        if any(char in text_lower for char in cls.FRENCH_CHARS):
            return 'fr'
        
        # Comptage mots-clés
        french_count = sum(1 for word in cls.FRENCH_KEYWORDS if word in text_lower)
        english_count = sum(1 for word in cls.ENGLISH_KEYWORDS if word in text_lower)
        
        return 'fr' if french_count >= english_count else 'en'
