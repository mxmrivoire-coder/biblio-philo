"""
ai_books.py — Service de génération de fiche de lecture (Mode 1).

API : Perplexity (compatible OpenAI SDK)
Modèle : llama-3.1-sonar-large-128k-online
Clé   : variable d'environnement AI_API_KEY
"""

import json
import os
from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from app.models import Book


# ─── Client Perplexity (réutilisé à chaque appel) ────────────────────────────

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


# ─── Construction du prompt ───────────────────────────────────────────────────

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
    return f"""
Tu es un assistant philosophique et politique.
À partir des informations suivantes sur un livre, génère une fiche de lecture structurée.

Livre : "{book.title}"
Auteur : {book.author}
Type : {book.type_label}
Statut de lecture : {book.status_label}
{notes_section}

Thèmes principaux de l'utilisateur : {themes}

Réponds UNIQUEMENT en JSON valide, sans texte avant ou après, avec exactement ces clés :
{{
  "summary": "Résumé en 5-8 lignes du livre",
  "concepts": "Liste markdown des concepts clés (- Concept : explication)",
  "quotes": "3-5 citations essentielles avec numéro de page approximatif si connu",
  "links_to_themes": "Comment ce livre s'articule aux thèmes : {themes}",
  "usage_ideas": "3 idées d'usage concrètes (thread, scène de roman, argument d'essai)"
}}
""".strip()


# ─── Fonction principale ──────────────────────────────────────────────────────

def generate_book_summary(book: "Book") -> dict:
    """
    Génère la fiche de lecture d'un livre via l'API Perplexity.

    Retourne un dict avec les clés :
        summary, concepts, quotes, links_to_themes, usage_ideas
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant philosophique et politique francophone. "
                    "Tu réponds UNIQUEMENT en JSON valide, sans markdown autour, "
                    "sans texte introductif ni conclusif."
                ),
            },
            {"role": "user", "content": _build_prompt(book)},
        ],
    )
    raw = response.choices[0].message.content.strip()
    # Nettoyage au cas où le modèle entoure le JSON de ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
