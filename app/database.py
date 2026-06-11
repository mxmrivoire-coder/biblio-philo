"""
database.py — Configuration SQLAlchemy et session de base de données.

En local  : SQLite dans data/biblioth.db
Railway   : la variable d'environnement DATABASE_URL est injectée automatiquement.
            SQLite reste utilisable en production si vous ne souhaitez pas Postgres.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

# ─── Résolution de l'URL de base de données ──────────────────────────────────
_DATABASE_URL = os.getenv("DATABASE_URL")

if not _DATABASE_URL:
    # Développement local : SQLite dans le dossier data/
    _db_path = Path(__file__).resolve().parent.parent / "data" / "biblioth.db"
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    _DATABASE_URL = f"sqlite:///{_db_path}"

# Railway injecte parfois "postgres://" (ancienne syntaxe) ; SQLAlchemy 2.x
# n'accepte que "postgresql://".
if _DATABASE_URL.startswith("postgres://"):
    _DATABASE_URL = _DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ─── Moteur SQLAlchemy ────────────────────────────────────────────────────────
_connect_args = {"check_same_thread": False} if _DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    _DATABASE_URL,
    connect_args=_connect_args,
    echo=False,  # Passer à True pour logger les requêtes SQL en dev
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Classe de base pour les modèles SQLAlchemy ───────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Dépendance FastAPI — injection de session dans les routes ────────────────
def get_db():
    """
    Générateur utilisé comme dépendance FastAPI (Depends(get_db)).
    Garantit la fermeture de la session après chaque requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
