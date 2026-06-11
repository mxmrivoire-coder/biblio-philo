"""
ai_problems.py — Service de génération de problématiques et plans (Mode 3).

API : Perplexity (compatible OpenAI SDK)
Modèle : llama-3.1-sonar-large-128k-online
Clé   : variable d'environnement AI_API_KEY
"""

import json
import os

from openai import OpenAI


def _get_client() -> OpenAI:
    api_key = os.environ.get("AI_API_KEY")
    if not api_key:
        raise RuntimeError("Variable d'environnement AI_API_KEY manquante.")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )


def _build_prompt(theme: str, authors: list[str], orientation: str) -> str:
    authors_str = ", ".join(authors) if authors else "auteurs non précisés"
    orientation_label = (
        "threads / publications sur les réseaux sociaux (courts, percutants, grand public)"
        if orientation == "thread"
        else "essais académiques ou philosophiques (argumentés, structurés, référencés)"
    )
    return f"""
Tu es un assistant philosophique et politique spécialisé dans la construction d'argumentaires.
Génère 2 problématiques et leurs plans détaillés pour le thème suivant.

Thème : {theme}
Auteurs de référence : {authors_str}
Orientation des plans : {orientation_label}

Réponds UNIQUEMENT en JSON valide, sans texte avant ou après, avec exactement ces clés :
{{
  "problems": [
    "Problématique 1 sous forme de question philosophique précise ?",
    "Problématique 2 sous forme de question philosophique précise ?"
  ],
  "plans": [
    {{
      "problem": "Problématique 1 (reprendre exactement)",
      "plan": {{
        "I": {{
          "title": "Titre de la partie I",
          "points": ["Sous-point A", "Sous-point B", "Sous-point C"]
        }},
        "II": {{
          "title": "Titre de la partie II",
          "points": ["Sous-point A", "Sous-point B", "Sous-point C"]
        }},
        "III": {{
          "title": "Titre de la partie III",
          "points": ["Sous-point A", "Sous-point B", "Sous-point C"]
        }}
      }}
    }},
    {{
      "problem": "Problématique 2 (reprendre exactement)",
      "plan": {{
        "I": {{"title": "...", "points": ["...", "...", "..."]}},
        "II": {{"title": "...", "points": ["...", "...", "..."]}},
        "III": {{"title": "...", "points": ["...", "...", "..."]}}
      }}
    }}
  ]
}}
""".strip()


def generate_problems_and_plans(theme: str, authors: list[str], orientation: str) -> dict:
    """
    Génère des problématiques et leurs plans I/II/III via l'API Perplexity.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant philosophique francophone. "
                    "Tu réponds UNIQUEMENT en JSON valide, sans markdown autour."
                ),
            },
            {"role": "user", "content": _build_prompt(theme, authors, orientation)},
        ],
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
