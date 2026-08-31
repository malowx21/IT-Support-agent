# IT Support Agent

Agent IA de support technique capable de répondre à des questions à partir
d'une base de connaissances, d'utiliser des outils MCP et de demander une
validation humaine avant toute action sensible.

Ce projet permet d'apprendre et de démontrer les bases de l'agentique, du RAG,
des serveurs MCP, du backend avec FastAPI et du frontend avec React.

## Fonctionnalités

- recherche documentaire avec RAG et embeddings ;
- gestion de tickets stockés dans SQLite ;
- tools, resources et prompts exposés par un serveur MCP ;
- orchestration de l'agent avec LangGraph ;
- validation humaine avant la fermeture d'un ticket ou le changement de sa
  priorité ;
- sauvegarde des checkpoints LangGraph dans SQLite ;
- API REST FastAPI et interface de conversation React ;
- journal d'audit des actions effectuées sur les tickets.

## Architecture

```text
Frontend React
      |
      | HTTP/JSON
      v
API FastAPI
      |
      v
Agent LangGraph ------> Checkpoints SQLite
      |
      v
Client MCP
      |
      v
Serveur MCP
   |         |
   |         +--> RAG / base de connaissances
   +------------> Repository SQLite / tickets / audit
```

Parcours simplifié du graphe :

```text
START
  |
  v
agent
  |-- réponse directe ------------------------> END
  |-- tool non sensible --> tool --> agent
  +-- tool sensible ------> human
                              |-- approve --> tool --> agent
                              +-- reject ----> agent
```

## Technologies

### Backend et agent

- Python 3.12, FastAPI et SQLite
- LangGraph et LangChain
- FastMCP et `langchain-mcp-adapters`
- Gemini via `langchain-google-genai`
- Hugging Face Sentence Transformers

### Frontend

- React, JavaScript et JSX
- Vite, CSS et ESLint

## Structure du projet

```text
.
├── agent/              # Graphe LangGraph et client MCP
├── api/                # Routes, schémas et service FastAPI
├── data/               # Bases SQLite locales, non versionnées
├── frontend/           # Application React
├── mcp_server/         # Serveur MCP, métier et repository
├── rag/                # Chargement, embeddings et recherche
├── tests/              # Tests automatisés du backend
├── requirements.txt
└── README.md
```

## Installation du backend

Depuis la racine du projet :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crée un fichier `.env` contenant ta clé Gemini :

```env
GOOGLE_API_KEY=ta_cle_api
```

Ne publie jamais ce fichier ou une véritable clé API dans Git.

## Préparation de la base RAG

Les documents Markdown se trouvent dans `mcp_server/knowledge/`. Pour générer
leurs chunks et leurs embeddings :

```bash
python -m rag.ingest
```

Le premier lancement peut télécharger le modèle d'embeddings.

## Lancement du backend

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger : <http://127.0.0.1:8000/docs>
- contrôle de santé : <http://127.0.0.1:8000/health>

## Installation et lancement du frontend

Dans un deuxième terminal :

```bash
cd frontend
npm install
npm run dev
```

L'interface est disponible sur <http://localhost:5173>.

## Tests et contrôles

Backend :

```bash
pytest
```

Frontend :

```bash
cd frontend
npm run lint
npm run build
```

## Actions sensibles et validation humaine

`close_ticket` et `update_ticket_priority` nécessitent une validation. Lorsqu'un
de ces outils est demandé, LangGraph interrompt l'exécution. Le frontend affiche
les boutons **Approuver** et **Rejeter**. La décision est envoyée avec le même
`thread_id`, puis le graphe reprend depuis son checkpoint.

## CI/CD

La pipeline prévue vérifiera automatiquement :

```text
Pull Request ou push
├── tests Python avec pytest
├── lint React avec ESLint
├── build de production avec Vite
└── déploiement uniquement si tous les contrôles réussissent
```

La configuration GitHub Actions sera ajoutée dans
`.github/workflows/ci.yml`.
