# Bibliothécaire philo/politique

Application web personnelle de gestion de lectures philosophiques et politiques, avec génération assistée par IA.

## Fonctionnalités

| Mode | Description |
|------|-------------|
| **Livres** | Gestion de bibliothèque + fiches de lecture générées par IA |
| **Cartes conceptuelles** | Croisement d'auteurs, concepts et exemples autour d'un thème |
| **Problématiques** | Génération de problématiques et plans I/II/III (essai ou thread) |

## Stack technique

- **Backend** : FastAPI + Jinja2 (Python 3.11+)
- **Base de données** : SQLite (local) / PostgreSQL (Railway)
- **Frontend** : HTML + TailwindCSS CDN + HTMX
- **ORM** : SQLAlchemy 2.x

---

## Installation locale

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd bibliothecaire-philo

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env si vous voulez brancher une API IA

# 5. Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

L'application est accessible sur http://localhost:8000

---

## Déploiement Railway

1. Pousser le repo sur GitHub
2. Créer un nouveau projet sur [Railway](https://railway.app)
3. Connecter le repo GitHub
4. Commande de démarrage :
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Ajouter les variables d'environnement dans Railway :
   - `AI_API_KEY` : votre clé API
   - `AI_PROVIDER` : `perplexity`, `openai` ou `anthropic`

---

## Brancher l'API IA

Les trois fonctions `generate_*` sont des mocks documentés. Pour les activer :

| Fichier | Fonction | Mode |
|---------|----------|------|
| `app/services/ai_books.py` | `generate_book_summary(book)` | Fiches de lecture |
| `app/services/ai_concepts.py` | `generate_concept_map(theme, authors)` | Cartes conceptuelles |
| `app/services/ai_problems.py` | `generate_problems_and_plans(theme, authors, orientation)` | Problématiques |

Dans chaque fichier, repérez le bloc commenté `── REMPLACER LE MOCK ICI ──` et suivez les exemples Perplexity / Anthropic fournis.

---

## Structure du projet

```
bibliothecaire-philo/
├── app/
│   ├── main.py            # Point d'entrée FastAPI
│   ├── database.py        # SQLAlchemy, session, engine
│   ├── models.py          # Modèles Book, ConceptMap, ProblemSet
│   ├── routers/
│   │   ├── books.py       # Routes Mode 1
│   │   ├── concept_maps.py# Routes Mode 2
│   │   └── problems.py    # Routes Mode 3
│   └── services/
│       ├── ai_books.py    # Mock + point de branchement IA
│       ├── ai_concepts.py # Mock + point de branchement IA
│       └── ai_problems.py # Mock + point de branchement IA
├── templates/
│   ├── base.html
│   ├── books/             # list, new, detail
│   ├── concept_maps/      # list, new, detail
│   └── problems/          # list, new, detail
├── static/
├── data/                  # SQLite DB (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```
