"""
models.py — Modèles SQLAlchemy.

Trois modèles principaux :
  - Book        : livres et fiches de lecture assistées par IA
  - ConceptMap  : cartes conceptuelles auteurs/concepts/exemples
  - ProblemSet  : ensembles de problématiques et plans d'essais

Les champs préfixés `ai_` sont remplis par les fonctions generate_*
situées dans app/services/.
"""

import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ─── Helpers JSON ─────────────────────────────────────────────────────────────

def _json_loads_or_default(value: str | None, default):
    """Désérialise un champ JSON stocké en texte, renvoie `default` si vide."""
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


# ═════════════════════════════════════════════════════════════════════════════
# Modèle Book — Mode 1
# ═════════════════════════════════════════════════════════════════════════════

class Book(Base):
    """
    Représente un livre de la bibliothèque personnelle.

    Champs `ai_*` : remplis automatiquement par generate_book_summary()
    dans app/services/ai_books.py. Ils sont stockés en texte (markdown ou JSON).
    """

    __tablename__ = "books"

    # ── Identifiant ───────────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Métadonnées du livre ──────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)

    # Valeurs possibles : roman | essai_philo | essai_politique | socio
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="essai_philo")

    # Valeurs possibles : en_cours | terminé
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="en_cours")

    # ── Notes brutes de l'utilisateur ─────────────────────────────────────────
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Champs générés par IA ─────────────────────────────────────────────────
    # Tous stockés en texte libre (markdown ou JSON stringifié).
    # Voir app/services/ai_books.py pour le format attendu et le branchement IA.
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_concepts: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_quotes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_links_to_themes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_usage_ideas: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Horodatage ───────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Labels d'affichage ────────────────────────────────────────────────────
    TYPE_LABELS = {
        "roman": "Roman",
        "essai_philo": "Essai philosophique",
        "essai_politique": "Essai politique",
        "socio": "Sociologie",
    }
    STATUS_LABELS = {
        "en_cours": "En cours",
        "terminé": "Terminé",
    }

    @property
    def type_label(self) -> str:
        return self.TYPE_LABELS.get(self.type, self.type)

    @property
    def status_label(self) -> str:
        return self.STATUS_LABELS.get(self.status, self.status)

    @property
    def has_ai_content(self) -> bool:
        """True si au moins un champ IA a été généré."""
        return bool(self.ai_summary or self.ai_concepts)

    def __repr__(self) -> str:
        return f"<Book id={self.id} title={self.title!r} author={self.author!r}>"


# ═════════════════════════════════════════════════════════════════════════════
# Modèle ConceptMap — Mode 2
# ═════════════════════════════════════════════════════════════════════════════

class ConceptMap(Base):
    """
    Carte conceptuelle reliant des auteurs, des concepts et des exemples
    autour d'un thème philosophique ou politique.

    `nodes` et `edges` sont stockés en JSON stringifié.
    Voir app/services/ai_concepts.py pour le format attendu.
    """

    __tablename__ = "concept_maps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Ex. : "Aliénation – Marx/Camus/Fanon"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    theme: Mapped[str] = mapped_column(String(255), nullable=False)

    # JSON list de strings : ["Marx", "Camus", "Fanon"]
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON : {"authors": [...], "concepts": [...], "examples": [...]}
    nodes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON list : [{"from": "...", "to": "...", "description": "..."}, ...]
    edges: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Synthèse en 10 lignes max
    summary_10_lines: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # ── Accesseurs désérialisés ───────────────────────────────────────────────

    @property
    def authors_list(self) -> list[str]:
        return _json_loads_or_default(self.authors, [])

    @property
    def nodes_dict(self) -> dict:
        return _json_loads_or_default(self.nodes, {"authors": [], "concepts": [], "examples": []})

    @property
    def edges_list(self) -> list[dict]:
        return _json_loads_or_default(self.edges, [])

    def __repr__(self) -> str:
        return f"<ConceptMap id={self.id} theme={self.theme!r}>"


# ═════════════════════════════════════════════════════════════════════════════
# Modèle ProblemSet — Mode 3
# ═════════════════════════════════════════════════════════════════════════════

class ProblemSet(Base):
    """
    Ensemble de problématiques philosophiques/politiques et leurs plans d'essais,
    générés à partir d'un thème, d'auteurs et d'une orientation (thread ou essai).

    `problems` et `plans` sont stockés en JSON stringifié.
    Voir app/services/ai_problems.py pour le format attendu.
    """

    __tablename__ = "problem_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Ex. : "Travail, absurde et domination"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    theme: Mapped[str] = mapped_column(String(255), nullable=False)

    # JSON list de strings
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)

    # "thread" ou "essai"
    orientation: Mapped[str] = mapped_column(String(50), nullable=False, default="essai")

    # JSON list de strings : ["Problématique 1...", "Problématique 2..."]
    problems: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON list : [{"problem": "...", "plan": {"I": {...}, "II": {...}, "III": {...}}}, ...]
    plans: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # ── Accesseurs désérialisés ───────────────────────────────────────────────

    @property
    def authors_list(self) -> list[str]:
        return _json_loads_or_default(self.authors, [])

    @property
    def problems_list(self) -> list[str]:
        return _json_loads_or_default(self.problems, [])

    @property
    def plans_list(self) -> list[dict]:
        return _json_loads_or_default(self.plans, [])

    @property
    def orientation_label(self) -> str:
        return "Threads / réseaux" if self.orientation == "thread" else "Essai académique"

    def __repr__(self) -> str:
        return f"<ProblemSet id={self.id} theme={self.theme!r}>"
