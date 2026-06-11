"""
ai_concepts.py — Service de génération de cartes conceptuelles (Mode 2).

Contient la fonction principale :
    generate_concept_map(theme: str, authors: list[str]) -> dict

──────────────────────────────────────────────────────────────────────────────
COMMENT BRANCHER VOTRE API IA — même procédure que ai_books.py
Repérez le bloc "── REMPLACER LE MOCK ICI ──" ci-dessous.
──────────────────────────────────────────────────────────────────────────────
"""

import os


# ─── Construction du prompt ───────────────────────────────────────────────────

def _build_prompt(theme: str, authors: list[str]) -> str:
    authors_str = ", ".join(authors) if authors else "auteurs non précisés"
    return f"""
Tu es un assistant philosophique et politique.
Génère une carte conceptuelle structurée autour du thème suivant.

Thème : {theme}
Auteurs impliqués : {authors_str}

Réponds en JSON valide avec exactement ces clés :
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


# ─── Fonction principale ──────────────────────────────────────────────────────

def generate_concept_map(theme: str, authors: list[str]) -> dict:
    """
    Génère la structure d'une carte conceptuelle.

    Retourne un dict avec les clés :
        nodes       : {"authors": [...], "concepts": [...], "examples": [...]}
        edges       : [{"from": ..., "to": ..., "description": ...}, ...]
        summary_10_lines : str

    ── REMPLACER LE MOCK ICI ────────────────────────────────────────────────
    # from openai import OpenAI
    # import json, os
    # client = OpenAI(
    #     api_key=os.environ["AI_API_KEY"],
    #     base_url="https://api.perplexity.ai",  # Supprimer pour OpenAI pur
    # )
    # response = client.chat.completions.create(
    #     model="llama-3.1-sonar-large-128k-online",
    #     messages=[
    #         {"role": "system", "content": "Tu es un assistant philosophique."},
    #         {"role": "user", "content": _build_prompt(theme, authors)},
    #     ],
    #     response_format={"type": "json_object"},
    # )
    # return json.loads(response.choices[0].message.content)
    ─────────────────────────────────────────────────────────────────────────
    """

    # ── MOCK ──────────────────────────────────────────────────────────────────
    mock_authors = authors if authors else ["Auteur A", "Auteur B"]
    return {
        "nodes": {
            "authors": mock_authors,
            "concepts": [
                "[MOCK] Concept central 1",
                "[MOCK] Concept central 2",
                "[MOCK] Concept dérivé 3",
            ],
            "examples": [
                "[MOCK] Exemple historique 1",
                "[MOCK] Exemple contemporain 2",
            ],
        },
        "edges": [
            {
                "from": mock_authors[0] if mock_authors else "Auteur A",
                "to": "[MOCK] Concept central 1",
                "description": "[MOCK] théorise",
            },
            {
                "from": "[MOCK] Concept central 1",
                "to": "[MOCK] Exemple historique 1",
                "description": "[MOCK] s'illustre dans",
            },
            {
                "from": mock_authors[-1] if len(mock_authors) > 1 else "[MOCK] Auteur B",
                "to": "[MOCK] Concept central 2",
                "description": "[MOCK] critique via",
            },
        ],
        "summary_10_lines": (
            f"[MOCK] Synthèse de la carte conceptuelle sur le thème : {theme}.\n"
            "Cette synthèse est un placeholder en attente du branchement IA.\n"
            "Elle résumera en 10 lignes les articulations entre les auteurs,\n"
            "les concepts clés et les exemples concrets identifiés."
        ),
    }
    # ── FIN MOCK ──────────────────────────────────────────────────────────────
