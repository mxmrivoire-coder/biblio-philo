"""
ai_problems.py — Service de génération de problématiques et plans (Mode 3).

Contient la fonction principale :
    generate_problems_and_plans(theme, authors, orientation) -> dict

──────────────────────────────────────────────────────────────────────────────
COMMENT BRANCHER VOTRE API IA — même procédure que ai_books.py
Repérez le bloc "── REMPLACER LE MOCK ICI ──" ci-dessous.
──────────────────────────────────────────────────────────────────────────────
"""

import os


# ─── Construction du prompt ───────────────────────────────────────────────────

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

Réponds en JSON valide avec exactement ces clés :
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


# ─── Fonction principale ──────────────────────────────────────────────────────

def generate_problems_and_plans(
    theme: str, authors: list[str], orientation: str
) -> dict:
    """
    Génère des problématiques et leurs plans I/II/III.

    Paramètres :
        theme       : thème libre (ex. "Travail, absurde et domination")
        authors     : liste d'auteurs (ex. ["Marx", "Camus", "Fanon"])
        orientation : "thread" ou "essai"

    Retourne un dict avec les clés :
        problems : list[str]
        plans    : list[{"problem": str, "plan": {"I": {...}, "II": {...}, "III": {...}}}]

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
    #         {"role": "user", "content": _build_prompt(theme, authors, orientation)},
    #     ],
    #     response_format={"type": "json_object"},
    # )
    # return json.loads(response.choices[0].message.content)
    ─────────────────────────────────────────────────────────────────────────
    """

    # ── MOCK ──────────────────────────────────────────────────────────────────
    pb1 = f"[MOCK] En quoi le thème « {theme} » révèle-t-il une tension fondamentale entre liberté et contrainte ?"
    pb2 = f"[MOCK] Comment les auteurs {', '.join(authors[:2]) if authors else 'choisis'} permettent-ils de repenser « {theme} » à l'aune des rapports de domination contemporains ?"

    plan_template = lambda pb: {
        "problem": pb,
        "plan": {
            "I": {
                "title": "[MOCK] Première thèse : le constat",
                "points": [
                    "[MOCK] Sous-point 1A : ancrage théorique",
                    "[MOCK] Sous-point 1B : illustration",
                    "[MOCK] Sous-point 1C : limite du constat",
                ],
            },
            "II": {
                "title": "[MOCK] Deuxième thèse : la contradiction",
                "points": [
                    "[MOCK] Sous-point 2A : retournement critique",
                    "[MOCK] Sous-point 2B : apport d'un auteur de référence",
                    "[MOCK] Sous-point 2C : tension non résolue",
                ],
            },
            "III": {
                "title": "[MOCK] Troisième thèse : le dépassement",
                "points": [
                    "[MOCK] Sous-point 3A : proposition constructive",
                    "[MOCK] Sous-point 3B : ancrage dans le réel contemporain",
                    "[MOCK] Sous-point 3C : ouverture",
                ],
            },
        },
    }

    return {
        "problems": [pb1, pb2],
        "plans": [plan_template(pb1), plan_template(pb2)],
    }
    # ── FIN MOCK ──────────────────────────────────────────────────────────────
