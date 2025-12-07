# 📋 RÉSUMÉ EXÉCUTIF - Communication Multi-Agents et Architecture

## Vue Rapide: Qui Appelle Qui?

```
┌─────────────────────────────────────────────────────────────┐
│  UTILISATEUR (Streamlit)                                    │
│  "Je souffre de fatigue et de vertiges"                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓
        ┌────────────────────┐
        │  MedicalCrew()     │
        │  (crew.py)         │
        └────┬───────────────┘
             │
             ├─ Crée LLM: Groq
             ├─ Crée Agent 1: Diagnostician
             ├─ Crée Agent 2: Explainer
             ├─ Crée Task 1: Diagnosis
             ├─ Crée Task 2: Explanation
             └─ Démarre Crew.kickoff()
                     │
                     ↓
            ┌─────────────────┐
            │ TASK 1: START   │
            └────┬────────────┘
                 │
      Agent 1 Pense:
      "Je dois utiliser MedicalRAGTool"
                 │
                 ↓
        ┌────────────────────────┐
        │ MedicalRAGTool()       │
        │ (rag_tool.py)          │
        └────┬───────────────────┘
             │
             ├─ detect_language(question)
             │  └─→ Trouve accents 'é', 'ê'
             │  └─→ Retourne 'fr'
             │
             ├─ _init_graph()
             │  └─→ Neo4jGraph(url, user, pass)
             │
             ├─ _init_llm()
             │  └─→ ChatOpenAI(groq endpoint)
             │
             ├─ _init_rag_chain()
             │  └─→ GraphCypherQAChain
             │
             └─ qa_chain.invoke()
                     │
            ┌────────┴────────┐
            │                 │
            ↓                 ↓
      [LLM PHASE 1]   [NEO4J PHASE]
      Groq Generate    Execute Cypher
      Cypher Query     Query
            │                 │
            ├─────────────────┤
            │                 │
            ↓                 ↓
         Neo4j          Get Results
         Execute        (JSON)
            │                 │
            └────────┬────────┘
                     │
                     ↓
            [LLM PHASE 2]
            Groq Formats
            Results
            (French)
                     │
                     ↓
        ┌────────────────────┐
        │ Tool Returns       │
        │ Structured Result  │
        └────┬───────────────┘
             │
    Agent 1 Receives:
    "Based on symptoms:
     - Anemia found (FR)
     - Hypotension (FR)
     - Treatments: ..."
             │
             ↓
        ┌─────────────────┐
        │ TASK 1: DONE    │
        └────┬────────────┘
             │
      CrewAI Sequential Check:
      "Task 1 complete? Yes → Start Task 2"
             │
             ↓
        ┌─────────────────┐
        │ TASK 2: START   │
        │ (Receives context│
        │  from Task 1)   │
        └────┬────────────┘
             │
      Agent 2 Pense:
      "Je dois expliquer ces résultats"
             │
             ↓
      ┌──────────────────┐
      │ Call LLM (Groq)  │
      └────┬─────────────┘
           │
           ├─ Input: Task 1 results
           ├─ Instruction: "Structure explanation
           │              with diseases,
           │              why match,
           │              treatments,
           │              causes,
           │              confidence"
           └─ Output: Structured response
                     (French)
           │
           ↓
      Agent 2 Returns:
      "**MALADIES TROUVÉES:**
       1. Anémie
          Corrélation: Manque de globules
          Traitements: Fer, Vit B12
          Causes: Carence
          Confiance: Élevée
       2. Hypotension
          ..."
           │
           ↓
      ┌─────────────────┐
      │ TASK 2: DONE    │
      └────┬────────────┘
           │
      ┌────────────────────┐
      │ Crew Complete      │
      │ Return Final Output│
      └────┬───────────────┘
           │
           ↓
      ┌────────────────────┐
      │ STREAMLIT          │
      │ Display Result     │
      └────┬───────────────┘
           │
           ↓
      ┌────────────────────┐
      │ UTILISATEUR        │
      │ Voit réponse FR    │
      └────────────────────┘
```

---

## Communication: Détail Par Étape

### **Étape 1: Utilisateur → Streamlit**
```
Utilisateur écrit: "Je souffre de fatigue et de vertiges"
                        ↓
Streamlit reçoit input
Streamlit détecte: Français
Streamlit appelle: crew.run(question)
```

### **Étape 2: Streamlit → CrewAI**
```
Streamlit: crew.run("Je souffre...")
                        ↓
CrewAI: __init__()
  ├─ Initialise LLM (Groq)
  ├─ Crée Diagnostician Agent
  ├─ Crée Explainer Agent
  ├─ Crée Diagnosis Task
  ├─ Crée Explanation Task (avec context)
  └─ Retourne self (Crew instance)
                        ↓
CrewAI: kickoff()
  ├─ Démarre TASK 1
  └─ Attend TASK 1 completion
```

### **Étape 3: Agent 1 → MedicalRAGTool**
```
Agent 1 Pense: "Task requiert interrogation base"
Agent 1 Décide: "Utiliser MedicalRAGTool"
Agent 1 Appelle: tool.run(question)
                        ↓
MedicalRAGTool._run():
  ├─ Détecte langue: FR
  ├─ Initialise Neo4j
  ├─ Initialise Groq LLM
  ├─ Crée GraphCypherQAChain
  ├─ Invoque chain
  └─ Retourne résultat
```

### **Étape 4: Tool → LLM (Phase 1)**
```
MedicalRAGTool: "Generate Cypher query"
                        ↓
Groq LLM reçoit:
  - Neo4j Schema
  - Question: "Je souffre de fatigue et vertiges"
  - Prompt: "Generate ONLY Cypher, LOWERCASE
            relationships, UPPERCASE labels"
                        ↓
Groq génère:
  MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
  WHERE s.name IN ['fatigue','vertiges']
  OPTIONAL MATCH (d)-[:TREATED_WITH]->(t:Treatment)
  OPTIONAL MATCH (d)-[:CAUSED_BY]->(c:Cause)
  RETURN DISTINCT d.name, collect(...), ...
                        ↓
Groq retourne: Cypher query string
```

### **Étape 5: Tool → Neo4j**
```
MedicalRAGTool: Exécute Cypher query
                        ↓
Neo4j Graph Engine:
  ├─ Parse query
  ├─ Check schema
  ├─ Traverse graph:
  │  ├─ Find diseases with "fatigue" symptom
  │  ├─ Find diseases with "vertiges" symptom
  │  ├─ Get treatments for each disease
  │  └─ Get causes for each disease
  └─ Return results JSON
                        ↓
Neo4j retourne:
  [
    {
      disease: "Anemia",
      symptoms: ["fatigue", "vertiges"],
      treatments: ["Iron", "Vitamin B12"],
      causes: ["Nutritional deficiency"]
    },
    {
      disease: "Hypotension",
      symptoms: ["fatigue", "vertiges"],
      treatments: ["Hydration", "Salt"],
      causes: ["Dehydration"]
    }
  ]
```

### **Étape 6: Tool → LLM (Phase 2)**
```
MedicalRAGTool: "Format results as explanation"
                        ↓
Groq LLM reçoit:
  - Query Results (JSON)
  - Question: "Je souffre..." (FRENCH)
  - Prompt: "Respond 100% in FRENCH
            Transform results into clear
            explanation with:
            - diseases
            - why they match
            - treatments
            - causes"
                        ↓
Groq Pense:
  "Question is French
   → Répondre 100% EN FRANÇAIS
   NO ENGLISH WORDS
   Translate diseases to French
   Translate symptoms to French
   Translate treatments to French
   Translate causes to French"
                        ↓
Groq génère (TOUT EN FRANÇAIS):
  "Maladies Trouvées:
   - Anémie: Manque de globules rouges
     cause insuffisance oxygénation
     → Fatigue et vertiges
     Traitements: Suppléments Fer,
     Vitamine B12
     Causes: Carence nutritionnelle
   
   - Hypotension: Pression basse
     cause faible apport sanguin
     → Fatigue et vertiges
     Traitements: Augmenter eau/sel,
     repos
     Causes: Déshydratation"
                        ↓
Groq retourne: French explanation text
```

### **Étape 7: Tool → Agent 1**
```
Tool retourne à Agent 1:
  {
    "title": "🏥 RÉSULTATS DIAGNOSTIC RAG MÉDICAL",
    "answer": "[French explanation]",
    "diseases": ["Anémie", "Hypotension"],
    "treatments": ["Fer", "Vitamine B12", ...],
    "causes": ["Carence nutritionnelle", ...]
  }
                        ↓
Agent 1: "Task 1 complete!
          I found the diseases
          and information needed"
```

### **Étape 8: Task 1 → Task 2 (Context)**
```
CrewAI: "Task 1 complete, ready for Task 2"
                        ↓
CrewAI: "Task 2 receives context:
         [output from Task 1]"
                        ↓
Agent 2: "I have context from Agent 1
          Now I need to explain better"
```

### **Étape 9: Agent 2 → LLM**
```
Agent 2: "I need to structure explanation"
                        ↓
Agent 2 appelle LLM (Groq):
  Input:
    - Task 1 results
    - Instruction: "Create structured 
      explanation with:
      1) Diseases matching
      2) Why they match
      3) Recommended treatments
      4) Possible causes
      5) Confidence level"
    - Original question (FRENCH)
                        ↓
Groq reçoit et comprend:
  "Previous results in French
   I need to restructure them
   Maintain French language
   Add structure with sections
   Add reasoning
   Add confidence"
                        ↓
Groq génère (STRUCTURED, FRENCH):
  "**MALADIES CORRESPONDANTES:**
   
   1. ANÉMIE FERRIPRIVE
   Pourquoi correspond:
   - Manque de globules rouges
   - Cause baisse oxygénation
   - Provoque fatigue et vertiges
   
   Traitements recommandés:
   - Suppléments de Fer
   - Vitamine B12
   - Alimentation riche en fer
   
   Causes possibles:
   - Carence nutritionnelle
   - Perte sanguine
   - Problème d'absorption
   
   Niveau de confiance: ÉLEVÉ (90%)
   
   2. HYPOTENSION
   [Same structure...]
   
   **RECOMMANDATION:**
   Consultez un médecin pour diagnostic
   précis et plan traitement personnalisé."
                        ↓
Groq retourne: Structured French text
```

### **Étape 10: Agent 2 → Task 2 Complete**
```
Agent 2: "Task 2 is complete!
          I created structured
          explanation"
                        ↓
CrewAI: "Both tasks complete
         Return final output"
```

### **Étape 11: CrewAI → Streamlit**
```
crew.kickoff() returns:
  final_output = "[Structured French explanation]"
                        ↓
Streamlit reçoit résultat
```

### **Étape 12: Streamlit → Utilisateur**
```
Streamlit: "Affiche résultat formaté"
                        ↓
Utilisateur voit:
  "🏥 RÉSULTATS DIAGNOSTIC RAG MÉDICAL
   
   📋 Réponse Principale:
   [Full French explanation]
   
   🦠 Maladies Trouvées: Anémie, Hypotension
   🔴 Symptômes Associés: Fatigue, Vertiges
   💊 Traitements Recommandés: Fer, Vitamine B12
   ⚠️ Causes Possibles: Carence, Déshydratation
   
   [Expandable Raw Output section]"
```

---

## Types de Communication CrewAI

### **1. Agent-to-Task Communication**
```
Agent 1 reçoit Task Description
Agent analyse "What do I need to do?"
Agent utilise tools ou LLM
Agent retourne résultat
CrewAI valide output vs expected_output
```

### **2. Task-to-Task Communication (Context)**
```
Task 1 complète → Output généré
CrewAI capture output
Task 2 reçoit: context=[task_1_output]
Task 2 peut utiliser Task 1 results
```

### **3. Agent-to-Tool Communication**
```
Agent: "Je dois utiliser tool"
Agent décide: MedicalRAGTool
Agent appelle: tool.run(input)
Tool exécute
Tool retourne output
Agent reçoit output
```

### **4. Tool-to-External Communication**
```
Tool appelle Neo4j: "Execute query"
Neo4j retourne résultats
Tool appelle Groq: "Generate text"
Groq retourne texto
Tool parse et formate
Tool retourne à Agent
```

### **5. Sequential Process Enforcement**
```
Process = Sequential
  ↓
Task 1 start
Task 1 executes
Task 1 complete
  ↓ (Only then)
Task 2 start
Task 2 executes (has Task 1 context)
Task 2 complete
  ↓
Return final result
```

---

## Résumé: Qui Appelle Qui?

| Source | Destination | Message | Attends |
|--------|------------|---------|---------|
| Utilisateur | Streamlit | Question | Réponse |
| Streamlit | CrewAI | question | final_output |
| CrewAI | Agent 1 | Task Description | Task Output |
| Agent 1 | MedicalRAGTool | question | structured_output |
| MedicalRAGTool | Neo4j | Cypher Query | Results JSON |
| MedicalRAGTool | Groq (Phase 1) | Question + Schema | Cypher Query |
| MedicalRAGTool | Groq (Phase 2) | Results + Question | French Text |
| Tool Output | Agent 1 | Results | Agent 1 completes Task |
| Task 1 Output | CrewAI | Results | Sequential Check |
| CrewAI | Agent 2 | Task Description + Context | Task Output |
| Agent 2 | Groq | Results + Instruction | Structured Output |
| Agent 2 Output | CrewAI | Results | Crew Complete |
| CrewAI | Streamlit | final_output | Display |
| Streamlit | Utilisateur | Formatted Result | User Satisfaction |

---

## Points Critiques

✅ **Sequential Execution**: Task 2 attend Task 1 obligatoirement  
✅ **Context Passing**: Task 2 reçoit output de Task 1  
✅ **Tool Autonomy**: Agent 1 décide d'utiliser tool (pas forcé)  
✅ **Language Awareness**: Détecte FR/EN, répond correctement  
✅ **Multi-step RAG**: LLM génère Cypher, puis formatte résultats  
✅ **No Tool for Agent 2**: Agent 2 utilise seulement LLM + contexte  

---

**Cette documentation explique EXACTEMENT qui appelle qui et comment la communication se fait à chaque étape.**
