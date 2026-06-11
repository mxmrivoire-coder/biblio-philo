"""
main.py — Point d'entrée de l'application FastAPI.

Lancement en développement :
    uvicorn app.main:app --reload --port 8000

Déploiement Railway :
    Railway détecte automatiquement uvicorn via le Procfile ou la commande de démarrage.
    Commande recommandée : uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.routers import books, concept_maps, problems

# ─── Initialisation de l'application ─────────────────────────────────────────
app = FastAPI(
    title="Bibliothécaire philo/politique",
    description="Application personnelle de gestion de lectures et d'aide à la réflexion.",
    version="1.0.0",
)

# ─── Création des tables SQLite au démarrage ──────────────────────────────────
# En production (Railway + Postgres), SQLAlchemy crée aussi les tables si elles
# n'existent pas. Pour des migrations complexes, envisager Alembic plus tard.
Base.metadata.create_all(bind=engine)

# ─── Templates Jinja2 ─────────────────────────────────────────────────────────
_templates_path = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(_templates_path))

# Stockage sur app.state pour accès depuis les routers via request.app.state
app.state.templates = templates

# ─── Fichiers statiques ───────────────────────────────────────────────────────
_static_path = Path(__file__).resolve().parent.parent / "static"
_static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_static_path)), name="static")

# ─── Inclusion des routers ────────────────────────────────────────────────────
# Mode 1 — Livres et fiches de lecture
app.include_router(books.router)

# Mode 2 — Cartes conceptuelles
app.include_router(concept_maps.router)

# Mode 3 — Problématiques et plans d'essais
app.include_router(problems.router)


# ─── Route racine ─────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    """Redirige vers la liste des livres (page d'accueil)."""
    return RedirectResponse(url="/books")


# ─── Health-check (utile pour Railway et les probes de monitoring) ────────────

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
