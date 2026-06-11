"""
ai_problems.py — Service de génération de problématiques et plans (Mode 3).

API : Perplexity sonar-pro
Clé : variable d'environnement AI_API_KEY
"""

import json
import os
import re

from openai import OpenAI


def _get_client() -> OpenAI:
    api_key = os.environ.get("AI_API_KEY")
    if not api_key:
        raise RuntimeError("Variable d'environnement AI_API_KEY manquante.")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")


def _extract_json(raw: str) -> dict:
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"Aucun JSON valide trouvé. Reçu : {raw[:300]}")


def _build_prompt(theme: str, authors: list[str], orientation: str) -> str:
    authors_str = ", ".join(authors) if authors else "auteurs non précisés"
    orientation_label = (
        "threads réseaux sociaux (courts, percutants, grand public)"
        if orientation == "thread"
        else "essais académiques (argumentés, structurés, référencés)"
    )
    return f"""Tu es un assistant philosophique francophone.
Génère 2 problématiques et leurs plans pour le thème suivant.

Thème : {theme}
Auteurs : {authors_str}
Orientation : {orientation_label}

Réponds UNIQUEMENT avec un objet JSON valide (pas de texte avant ni après) :
{{
  "problems": [
    "Problématique 1 ?",
    "Problématique 2 ?"
  ],
  "plans": [
    {{
      "problem": "Problématique 1 ?",
      "plan": {{
        "I": {{"title": "Titre partie I", "points": ["Sous-point A", "Sous-point B", "Sous-point C"]}},
        "II": {{"title": "Titre partie II", "points": ["Sous-point A", "Sous-point B", "Sous-point C"]}},
        "III": {{"title": "Titre partie III", "points": ["Sous-point A", "Sous-point B", "Sous-point C"]}}
      }}
    }},
    {{
      "problem": "Problématique 2 ?",
      "plan": {{
        "I": {{"title": "...", "points": ["...", "...", "..."]}},
        "II": {{"title": "...", "points": ["...", "...", "..."]}},
        "III": {{"title": "...", "points": ["...", "...", "..."]}}
      }}
    }}
  ]
}}"""


def generate_problems_and_plans(theme: str, authors: list[str], orientation: str) -> dict:
    """Génère des problématiques et plans via l'API Perplexity sonar-pro."""
    client = _get_client()
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant philosophique francophone. Tu réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après.",
            },
            {"role": "user", "content": _build_prompt(theme, authors, orientation)},
        ],
    )
    return _extract_json(response.choices[0].message.content)
