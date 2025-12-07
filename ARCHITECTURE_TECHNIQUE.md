# 🏥 Architecture Technique - Medical Knowledge Graph & RAG System

## Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Flux de Communication](#flux-de-communication)
3. [Communication Inter-Agents CrewAI](#communication-inter-agents-crewai)
4. [Détails Techniques](#détails-techniques)
5. [Diagramme de Flux](#diagramme-de-flux)

---

## Vue d'Ensemble

Ce système utilise une **architecture multi-agents** avec **CrewAI** pour orchestrer deux agents spécialisés qui collaborent sequentiellement pour répondre aux questions médicales.

### Composants Clés
```
┌─────────────────────────────────────────────────────────────┐
│  UTILISATEUR (Streamlit Web Interface)                       │
│  Pose une question médicale en Français ou Anglais           │
└──────────────────────┬──────────────────────────────────────┘
                       │ (Question + Détection Langue)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  CrewAI Orchestrator (crew.py)                               │
│  - Initialise les agents et tâches                           │
│  - Gère le flux sequential Process                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ↓                             ↓
   ┌─────────────┐             ┌──────────────┐
   │ Agent 1:    │             │ Agent 2:     │
   │ Diagnostic. │──────────→  │ Explainer    │
   │ (Rank 1)    │             │ (Rank 2)     │
   └─────────────┘             └──────────────┘
        │                             │
        │ Utilise Tool                │ Reçoit Contexte
        │                             │ de Task 1
        ↓                             ↓
   ┌─────────────────────────────────────────┐
   │  MedicalRAGTool (rag_tool.py)            │
   │  - Détecte la langue                    │
   │  - Génère Cypher Query                  │
   │  - Interroge Neo4j                      │
   │  - Formate résultats                    │
   └──────────────┬──────────────────────────┘
                  ↓
   ┌─────────────────────────────────────────┐
   │  Neo4j AuraDB (Cloud)                    │
   │  - 14 Diseases                          │
   │  - 109 Symptoms                         │
   │  - 92 Treatments                        │
   │  - 92 Causes                            │
   │  - 293 Relationships                    │
   └─────────────────────────────────────────┘
```

---

## Flux de Communication

### **Sequence d'Exécution (Détail Complet)**

```
[ÉTAPE 1] UTILISATEUR SOUMET QUESTION
──────────────────────────────────────
User Input: "Je souffre de fatigue et de vertiges"
            └─→ Streamlit Interface (app.py)
```

```
[ÉTAPE 2] INITIALISATION DU SYSTÈME
────────────────────────────────────
1. app.py détecte: Question en français
2. Crée instance MedicalCrew()
   └─→ Initialise ChatOpenAI (Groq LLM)
       - Model: llama-3.3-70b-versatile
       - Base URL: https://api.groq.com/openai/v1
       - Temperature: 0.3 (déterministe)
       - Max Tokens: 4000
```

```
[ÉTAPE 3] CREWIE KICKOFF - CRÉATION AGENTS & TASKS
────────────────────────────────────────────────────

crew.run(symptoms) est appelé:

A) AGENT 1 CRÉATION: Medical Diagnostician
   ┌────────────────────────────────────────┐
   │ Role: Medical Diagnostician            │
   │ Goal: Find diseases matching symptoms  │
   │ Tools: [MedicalRAGTool()]              │
   │ Max Iterations: 3                      │
   │ Max RPM: 10 (Rate Limiting)            │
   │ Max Execution Time: 120s               │
   │ LLM: Groq (llama-3.3-70b)             │
   └────────────────────────────────────────┘

B) TASK 1 CRÉATION: Diagnosis Task
   ┌────────────────────────────────────────┐
   │ Description: "Use Medical RAG Tool to  │
   │  query graph for diseases matching     │
   │  symptômes: {symptoms}"                │
   │                                        │
   │ Expected Output: "Complete diagnostic │
   │  information: diseases, symptoms,      │
   │  treatments, causes"                   │
   │                                        │
   │ Assigned to: Medical Diagnostician    │
   └────────────────────────────────────────┘

C) AGENT 2 CRÉATION: Medical Explainer
   ┌────────────────────────────────────────┐
   │ Role: Medical Explainer                │
   │ Goal: Explain RAG results clearly      │
   │ Tools: None (pas de tools)             │
   │ Max Iterations: 5                      │
   │ LLM: Groq (llama-3.3-70b)             │
   └────────────────────────────────────────┘

D) TASK 2 CRÉATION: Explanation Task
   ┌────────────────────────────────────────┐
   │ Description: "Review diagnostic       │
   │  results and create clear structured  │
   │  explanation with:                    │
   │  1) Diseases matching                │
   │  2) Symptom correlation              │
   │  3) Treatments                       │
   │  4) Causes                           │
   │  5) Confidence level"                │
   │                                       │
   │ Expected Output: "Structured medical │
   │  explanation with all details"       │
   │                                       │
   │ Assigned to: Medical Explainer       │
   │ Context: [diagnosis_task]            │
   │ (Reçoit sortie de Task 1)           │
   └────────────────────────────────────────┘

E) CREW CRÉATION
   ┌────────────────────────────────────────┐
   │ Agents: [Diagnostician, Explainer]    │
   │ Tasks: [Diagnosis Task, Explainer]    │
   │ Process: SEQUENTIAL                    │
   │ (Task 1 must complete before Task 2)  │
   │ Memory: False (pas de cache)          │
   └────────────────────────────────────────┘
```

```
[ÉTAPE 4] CREW KICKOFF - EXÉCUTION SEQUENTIELLE
────────────────────────────────────────────────

crew.kickoff() Lance l'orchestration:

┌─ TASK 1 EXÉCUTION ─────────────────────────────┐
│                                                 │
│ Medical Diagnostician Agent PENSE:             │
│ "Je dois utiliser Medical RAG Tool pour       │
│  interroger la base pour les maladies         │
│  correspondant aux symptômes"                  │
│                                                 │
│ ↓ DÉCISION AGENTS: Utiliser Tool              │
│                                                 │
│ ┌─ MEDICAL RAG TOOL INVOCATION ──────────────┐ │
│ │                                              │ │
│ │ Input Query: "Je souffre de fatigue et     │ │
│ │              de vertiges"                   │ │
│ │                                              │ │
│ │ Step 1: detect_language(query)              │ │
│ │         └─→ Trouve accents: 'ê', 'é'       │ │
│ │         └─→ Retourne: 'fr'                 │ │
│ │                                              │ │
│ │ Step 2: _init_rag_chain()                   │ │
│ │         └─→ Crée GraphCypherQAChain        │ │
│ │         └─→ Charge prompts personnalisés   │ │
│ │                                              │ │
│ │ Step 3: qa_chain.invoke({"query": ...})     │ │
│ │         │                                    │ │
│ │         ├─ Cypher Generation Phase:         │ │
│ │         │  ┌──────────────────────────────┐│ │
│ │         │  │ LLM (Groq) receives:         ││ │
│ │         │  │ - Neo4j Schema               ││ │
│ │         │  │ - Question in French         ││ │
│ │         │  │ - Cypher generation prompt  ││ │
│ │         │  │                              ││ │
│ │         │  │ LLM Generate Cypher:        ││ │
│ │         │  │ MATCH (d:Disease)            ││ │
│ │         │  │ -[:HAS_SYMPTOM]->(s:Symptom)││ │
│ │         │  │ WHERE s.name IN [...]        ││ │
│ │         │  │ OPTIONAL MATCH               ││ │
│ │         │  │ (d)-[:TREATED_WITH]->(t)    ││ │
│ │         │  │ OPTIONAL MATCH               ││ │
│ │         │  │ (d)-[:CAUSED_BY]->(c)       ││ │
│ │         │  │ RETURN DISTINCT ...          ││ │
│ │         │  └──────────────────────────────┘│ │
│ │         │                                    │ │
│ │         ├─ Neo4j Query Execution:           │ │
│ │         │  └─→ Execute Cypher Query         │ │
│ │         │  └─→ Retourne Results JSON        │ │
│ │         │                                    │ │
│ │         └─ QA Generation Phase:             │ │
│ │            ┌──────────────────────────────┐ │
│ │            │ LLM (Groq) receives:         │ │
│ │            │ - Query Results (JSON)       │ │
│ │            │ - Original Question (FR)     │ │
│ │            │ - QA generation prompt       │ │
│ │            │ - LANGUAGE RULE: "Respond   │ │
│ │            │   100% in French"            │ │
│ │            │                              │ │
│ │            │ LLM Generate Explanation:    │ │
│ │            │ "Maladies Trouvées:          │ │
│ │            │  - Anémie                    │ │
│ │            │  - Hypotension               │ │
│ │            │ Symptômes Correspondants:    │ │
│ │            │ - Fatigue                    │ │
│ │            │ - Vertiges                   │ │
│ │            │ ..."                         │ │
│ │            └──────────────────────────────┘ │
│ │                                              │ │
│ │ Step 4: _extract_graph_path()               │ │
│ │         └─→ Parse Cypher + Results          │ │
│ │         └─→ Retourne dict:                  │ │
│ │             {                               │ │
│ │               "cypher_query": "...",        │ │
│ │               "diseases": [...],            │ │
│ │               "symptoms": [...],            │ │
│ │               "treatments": [...],          │ │
│ │               "causes": [...]               │ │
│ │             }                               │ │
│ │                                              │ │
│ │ Step 5: Return Output                       │ │
│ │         └─→ Formatted médical analysis      │ │
│ │                                              │ │
│ └──────────────────────────────────────────────┘ │
│                                                 │
│ Tool Returns to Agent: Full analysis text       │
│                                                 │
│ ↓ AGENT FINISHES THOUGHT                        │
│                                                 │
│ Medical Diagnostician Final Output:             │
│ "Based on the RAG analysis, I found:            │
│  - Anémie matches your symptoms because...      │
│  - Hypotension is also likely because...        │
│  - Recommended treatments: ..."                 │
│                                                 │
│ Task 1 COMPLETE                                 │
└─────────────────────────────────────────────────┘

↓↓↓ SEQUENTIAL PROCESS - Task 1 DOIT se terminer avant Task 2 ↓↓↓

┌─ TASK 2 EXÉCUTION ─────────────────────────────┐
│                                                 │
│ Task 2 reçoit CONTEXTE de Task 1:              │
│ (context=[diagnosis_task])                      │
│                                                 │
│ Medical Explainer Agent reçoit:                │
│ - RAG diagnostic results (text from Task 1)    │
│                                                 │
│ Medical Explainer Agent PENSE:                 │
│ "Je dois restructurer et expliquer ces         │
│  résultats de manière claire pour le patient"  │
│                                                 │
│ ↓ AGENT CALLS LLM                              │
│                                                 │
│ ┌─ LLM REASONING ────────────────────────────┐ │
│ │                                              │ │
│ │ Input to Groq:                             │ │
│ │ - Diagnostic results from Task 1 (text)    │ │
│ │ - "Create structured explanation with:     │ │
│ │   1) Which diseases match                  │ │
│ │   2) Why they match (symptom analysis)     │ │
│ │   3) Recommended treatments                │ │
│ │   4) Possible causes                       │ │
│ │   5) Confidence level"                     │ │
│ │ - Original question: (French)              │ │
│ │                                              │ │
│ │ LLM Output:                                │ │
│ │ "**Maladies Diagnostiquées:**               │ │
│ │  1. Anémie ferriprive                      │ │
│ │     - Corrélation: Manque de globules      │ │
│ │       rouges cause fatigue et vertiges     │ │
│ │     - Traitements: Suppléments de Fer,     │ │
│ │       Vitamine B12                         │ │
│ │     - Causes: Carence nutritionnelle       │ │
│ │     - Confiance: Haute                     │ │
│ │                                              │ │
│ │  2. Hypotension                            │ │
│ │     - Corrélation: Pression basse cause    │ │
│ │       fatigue et vertiges                  │ │
│ │     - Traitements: Augmenter apport en     │ │
│ │       sel et eau                           │ │
│ │     - Causes: Déshydratation               │ │
│ │     - Confiance: Moyenne                   │ │
│ │                                              │ │
│ │  Recommandation: Consulter un médecin"     │ │
│ │                                              │ │
│ └──────────────────────────────────────────────┘ │
│                                                 │
│ Medical Explainer Final Output:                 │
│ "[Structured explanation as above]"             │
│                                                 │
│ Task 2 COMPLETE                                 │
└─────────────────────────────────────────────────┘
```

```
[ÉTAPE 5] CREW RETOURNE RÉSULTAT
─────────────────────────────────
crew.kickoff() returns final_output
  ↓
app.py reçoit: Full explanation text
  ↓
Streamlit affiche le résultat à l'utilisateur
```

---

## Communication Inter-Agents CrewAI

### **Modèle de Communication CrewAI**

CrewAI utilise un système de **Task Dependency** et **Context Passing** :

#### **1. Task Dependency (Dépendance de Tâches)**

```python
# Dans crew.py
explanation_task = Task(
    description="...",
    expected_output="...",
    agent=explainer,
    context=[diagnosis_task]  # ← CLIÉ: diagnosis_task doit finir AVANT
)
```

**Effet**: 
- Task 1 s'exécute TOUJOURS en premier
- Task 2 reçoit la sortie de Task 1 comme contexte
- Aucune exécution parallèle (Sequential Process)

#### **2. Process Type: Sequential**

```python
crew = Crew(
    agents=[diagnostician, explainer],
    tasks=[diagnosis_task, explanation_task],
    process=Process.sequential  # ← Exécution séquentielle
)
```

**Signification**:
```
Task 1 Start → Task 1 Complete → Task 2 Start → Task 2 Complete → Return
     ↓              ↓                 ↓              ↓
  Agent 1      Tool Output      Agent 2 Input   Final Output
```

#### **3. Context Passing Mechanism**

```
Task 1 Output: "Based on symptoms: Anemia found, treatments are..."
                                    ↓
            CrewAI Context Manager (interne)
                                    ↓
Task 2 Input: "Here are previous findings: [from Task 1]
               Now structure and explain..."
```

#### **4. Agent Autonomy & Decision Making**

```
Agent 1 (Diagnostician):
  - Reçoit Task Description
  - Analyse situation: "Je dois interroger la base"
  - Réfléchit: "Quel outil utiliser?"
  - Décide: "Utiliser MedicalRAGTool"
  - Exécute: tool.run(query)
  - Rend Résultat
  - Termine Task

Agent 2 (Explainer):
  - Reçoit Task Description + Contexte (Task 1 output)
  - Analyse: "Je dois expliquer ces résultats"
  - Réfléchit: "Comment structurer?"
  - Décide: "Réorganiser par section (maladies, symptômes, traitement)"
  - Appelle LLM: "Crée explanation structurée"
  - Rend Résultat structuré
  - Termine Task
```

---

## Détails Techniques

### **Composants Clés et Leurs Rôles**

#### **1. Streamlit (app.py)**
```
Responsabilités:
├─ Interface utilisateur Web
├─ Reçoit question de l'utilisateur
├─ Initialise MedicalCrew()
├─ Appelle crew.run(question)
├─ Affiche résultats formatés
└─ Gère la configuration API
```

#### **2. CrewAI (crew.py)**
```
Responsabilités:
├─ Crée et configure les agents
├─ Définie les tâches
├─ Orchestre l'exécution séquentielle
├─ Gère la communication Agent-Task
├─ Assure chaque agent a le LLM correct
└─ Retourne résultat final
```

#### **3. MedicalRAGTool (rag_tool.py)**
```
Responsabilités:
├─ Détecte la langue de la question
├─ Initialise connexion Neo4j
├─ Crée GraphCypherQAChain
├─ Invoque LLM pour générer Cypher
├─ Exécute Cypher sur Neo4j
├─ Parse résultats
├─ Formate réponse
└─ Retourne analyse structurée
```

#### **4. Neo4j (Database)**
```
Responsabilités:
├─ Stocke le Knowledge Graph médical
├─ Exécute Cypher queries
├─ Retourne résultats JSON
└─ Indexe pour performance
```

#### **5. Groq LLM**
```
Responsabilités:
├─ Génère Cypher queries (étape 1 du RAG)
├─ Génère explications textuelles (étape 2 du RAG)
├─ Restructure résultats (Agent 2)
├─ Détecte et respecte la langue
└─ Génère réponses patient-friendly
```

### **Types de Communication**

#### **Type 1: Agent ↔ Task**
```
Agent reçoit Task description
Agent pense (reasoning)
Agent décide: "Besoin d'un tool"
Agent invoque tool
Tool retourne données
Agent utilise données pour répondre Task
Agent retourne résultat
```

#### **Type 2: Agent ↔ Tool**
```
Agent dit: "rag_tool.run(query)"
Tool reçoit query
Tool traite
Tool retourne structured_output
Agent reçoit et utilise output
```

#### **Type 3: Tool ↔ LLM**
```
Tool dit: "qa_chain.invoke(input)"
LLM reçoit input + prompt
LLM génère output
Tool reçoit output
Tool retourne à Agent
```

#### **Type 4: Tool ↔ Database**
```
Tool dit: "Execute Cypher query"
Neo4j exécute query
Neo4j retourne résultats JSON
Tool parse et formate
Tool retourne à Agent
```

#### **Type 5: Task ↔ Task (via Context)**
```
Task 1 complète → Output généré
CrewAI capture output
Task 2 reçoit: "Voici contexte de Task 1"
Task 2 utilise contexte
Task 2 exécute
```

---

## Diagramme de Flux

### **Vue Complète d'Exécution**

```
┌────────────────────────────────────────────────────────────────┐
│                    UTILISATEUR                                  │
│        Pose question médicale (FR ou EN)                       │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ↓
┌────────────────────────────────────────────────────────────────┐
│                  STREAMLIT (app.py)                            │
│  ├─ Reçoit input utilisateur                                   │
│  ├─ Crée MedicalCrew() instance                               │
│  └─ Appelle crew.run(question)                                │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ↓
┌────────────────────────────────────────────────────────────────┐
│            CREWIE INITIALIZATION (crew.py)                     │
│  ├─ Initialise Groq LLM instance                              │
│  ├─ Crée Agent 1: Medical Diagnostician                       │
│  ├─ Crée Agent 2: Medical Explainer                           │
│  ├─ Crée Task 1: diagnosis_task                               │
│  ├─ Crée Task 2: explanation_task                             │
│  │  (avec context=[diagnosis_task])                           │
│  └─ Crée Crew(agents, tasks, process=sequential)              │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ↓
┌────────────────────────────────────────────────────────────────┐
│              CREW KICKOFF (Sequential)                         │
└────────────────────┬───────────────────────────────────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ↓                        │
    ┌─────────────┐              │
    │   TASK 1    │              │
    │  EXECUTION  │              │
    └──────┬──────┘              │
           │                      │
    ┌──────↓──────────────────┐  │
    │ Agent 1: Diagnostician  │  │
    │ Thought: "Use RAG Tool" │  │
    └──────┬──────────────────┘  │
           │                      │
    ┌──────↓────────────────────┐│
    │ MEDICAL RAG TOOL          ││
    │ ├─ Detect Language        ││
    │ │  → 'fr'                 ││
    │ ├─ Init Neo4j Connection  ││
    │ ├─ Create GraphCypher     ││
    │ │  QAChain               ││
    │ └─ Invoke Chain:          ││
    │    ├─ LLM generates       ││
    │    │  Cypher query        ││
    │    ├─ Neo4j executes      ││
    │    │  query               ││
    │    ├─ LLM formats         ││
    │    │  response            ││
    │    └─ Return structured   ││
    │       output              ││
    └──────┬────────────────────┘│
           │                      │
    ┌──────↓──────────────────────┐
    │ Task 1 Output:              │
    │ "Based on symptoms:         │
    │  Anemia, Hypotension found  │
    │  Treatments: ...            │
    │  Causes: ..."               │
    └──────┬─────────────────────┘
           │                      │
           │  [Task 1 Complete]   │
           │  ↓                   │
           └──────────────────→ Task 2 Start
                      │
                      ↓
                ┌─────────────┐
                │   TASK 2    │
                │  EXECUTION  │
                └──────┬──────┘
                       │
        ┌──────────────↓──────────────────┐
        │ Agent 2: Medical Explainer       │
        │ Receives Context: [Task 1 output]│
        │                                  │
        │ Thought: "Restructure and        │
        │  explain clearly"                │
        └──────┬──────────────────────────┘
               │
        ┌──────↓──────────────────┐
        │ LLM (Groq) Call         │
        │ ├─ Input: Task 1        │
        │ │        Results        │
        │ ├─ Instruction:         │
        │ │  "Structure:          │
        │ │   diseases,           │
        │ │   why matches,        │
        │ │   treatments,         │
        │ │   causes,             │
        │ │   confidence"         │
        │ └─ Output: Structured   │
        │   explanation (French)  │
        └──────┬──────────────────┘
               │
        ┌──────↓──────────────────┐
        │ Task 2 Output:          │
        │ "**Maladies Trouvées:** │
        │  1. Anémie              │
        │  2. Hypotension         │
        │ Explications...         │
        │ Traitements..."         │
        └──────┬──────────────────┘
               │
               │ [Task 2 Complete]
               │
               ↓
    ┌──────────────────────────┐
    │ Crew Complete            │
    │ Return final_output      │
    └──────────────┬───────────┘
                   │
                   ↓
    ┌──────────────────────────────┐
    │ STREAMLIT DISPLAY            │
    │ Affiche résultat formaté     │
    │ à l'utilisateur              │
    └──────────────────────────────┘
```

---

## Résumé Technique

### **Points Clés**

1. **Sequential Execution**: Task 1 DOIT finir avant Task 2
2. **Context Passing**: Task 2 reçoit la sortie de Task 1
3. **Tool-based Searching**: Agent 1 utilise MedicalRAGTool
4. **No tools for Explainer**: Agent 2 n'a besoin que du LLM
5. **Multi-step RAG**: LLM génère Cypher, puis explications
6. **Language Aware**: Détecte FR/EN, répond dans la même langue
7. **Neo4j Graph**: Source de vérité pour données médicales
8. **Groq LLM**: Moteur de génération pour Cypher et explications

### **Fluxogramme de Décision**

```
Question reçue
    ↓
Langue = FR? → Oui → Tous les labels et réponses en FR
    ↓ Non
        Langue = EN? → Oui → Tous les labels et réponses en EN
            ↓ Non
                Défaut = EN
```

---

**Version**: 1.0  
**Date**: Décembre 2024  
**Auteur**: Architecture Technique Medical RAG System
