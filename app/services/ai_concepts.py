"""
ai_concepts.py — Service de génération de cartes conceptuelles (Mode 2).

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


def _build_prompt(theme: str, authors: list[str]) -> str:
    authors_str = ", ".join(authors) if authors else "auteurs non précisés"
    return f"""Tu es un assistant philosophique francophone.
Génère une carte conceptuelle pour le thème suivant.

Thème : {theme}
Auteurs : {authors_str}

Réponds UNIQUEMENT avec un objet JSON valide (pas de texte avant ni après) :
{{
  "nodes": {{
    "authors": ["Auteur1", "Auteur2"],
    "concepts": ["Concept1", "Concept2", "Concept3"],
    "examples": ["Exemple historique 1", "Exemple contemporain 2"]
  }},
  "edges": [
    {{"from": "Auteur1", "to": "Concept1", "description": "relation courte"}},
    {{"from": "Concept1", "to": "Exemple historique 1", "description": "relation courte"}}
  ],
  "summary_10_lines": "Synthèse en 10 lignes maximum"
}}"""


def generate_concept_map(theme: str, authors: list[str]) -> dict:
    """Génère une carte conceptuelle via l'API Perplexity sonar-pro."""
    client = _get_client()
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant philosophique francophone. Tu réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après.",
            },
            {"role": "user", "content": _build_prompt(theme, authors)},
        ],
    )
    return _extract_json(response.choices[0].message.content)
