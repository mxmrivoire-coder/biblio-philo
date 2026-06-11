"""
ai_books.py — Service de génération de fiche de lecture (Mode 1).

API : Perplexity sonar-pro
Clé : variable d'environnement AI_API_KEY
"""

import json
import os
import re
from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from app.models import Book


def _get_client() -> OpenAI:
    api_key = os.environ.get("AI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Variable d'environnement AI_API_KEY manquante. "
            "Ajoutez-la dans Railway (Variables) ou dans votre fichier .env local."
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )


def _extract_json(raw: str) -> dict:
    """
    Extrait un objet JSON depuis une réponse texte qui peut contenir :
    - des balises markdown ```json ... ```
    - du texte introductif avant le JSON
    - des balises <think>...</think>
    """
    # Supprimer les blocs <think>
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Cas 1 : bloc ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Cas 2 : premier { ... } trouvé dans le texte
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError(f"Aucun JSON valide trouvé dans la réponse. Extrait reçu : {raw[:300]}")


def _build_prompt(book: "Book") -> str:
    themes = (
        "aliénation, domination, contrat de domination vs contrat social, "
        "post-vérité, méritocratie, capitalisme"
    )
    notes_section = (
        f"Notes personnelles de lecture :\n{book.user_notes}"
        if book.user_notes
        else "Aucune note personnelle fournie."
    )
    return f"""Tu es un assistant philosophique et politique francophone.
Génère une fiche de lecture structurée pour le livre suivant.

Titre : "{book.title}"
Auteur : {book.author}
Type : {book.type_label}
Statut : {book.status_label}
{notes_section}

Thèmes de référence : {themes}

Réponds UNIQUEMENT avec un objet JSON valide (pas de texte avant ni après), avec exactement ces 5 clés :
{{
  "summary": "Résumé en 5-8 lignes",
  "concepts": "Liste markdown des concepts clés (- Concept : explication)",
  "quotes": "3-5 citations essentielles",
  "links_to_themes": "Articulation avec les thèmes de référence",
  "usage_ideas": "3 idées d'usage (thread, scène de roman, argument d'essai)"
}}"""


def generate_book_summary(book: "Book") -> dict:
    """Génère la fiche de lecture via l'API Perplexity sonar-pro."""
    client = _get_client()
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant philosophique francophone. Tu réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après, sans balises markdown.",
            },
            {"role": "user", "content": _build_prompt(book)},
        ],
    )
    raw = response.choices[0].message.content
    return _extract_json(raw)
