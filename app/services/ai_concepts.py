"""
ai_concepts.py — Service de génération de cartes conceptuelles (Mode 2).

API : Perplexity (compatible OpenAI SDK)
Modèle : sonar-pro
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


def _build_prompt(theme: str, authors: list[str]) -> str:
    authors_str = ", ".join(authors) if authors else "auteurs non précisés"
    return f"""
Tu es un assistant philosophique et politique.
Génère une carte conceptuelle structurée autour du thème suivant.

Thème : {theme}
Auteurs impliqués : {authors_str}

Réponds UNIQUEMENT en JSON valide, sans texte avant ou après, avec exactement ces clés :
{{
  "nodes": {{
    "authors": ["Auteur1", "Auteur2"],
    "concepts": ["Concept1", "Concept2", "Concept3"],
    "examples": ["Exemple1", "Exemple2"]
  }},
  "edges": [
    {{"from": "Auteur1", "to": "Concept1", "description": "relation courte"}},
    {{"from": "Concept1", "to": "Exemple1", "description": "relation courte"}}
  ],
  "summary_10_lines": "Synthèse en 10 lignes maximum"
}}

Les nœuds `authors` doivent reprendre exactement les auteurs fournis.
Les `concepts` doivent être des notions philosophiques ou politiques précises.
Les `examples` doivent être des situations historiques, œuvres ou événements concrets.
""".strip()


def generate_concept_map(theme: str, authors: list[str]) -> dict:
    """
    Génère la structure d'une carte conceptuelle via l'API Perplexity.
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant philosophique francophone. "
                    "Tu réponds UNIQUEMENT en JSON valide, sans markdown autour."
                ),
            },
            {"role": "user", "content": _build_prompt(theme, authors)},
        ],
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
