"""
ai_books.py — Service de génération de fiche de lecture (Mode 1).

Contient la fonction principale :
    generate_book_summary(book: Book) -> dict

──────────────────────────────────────────────────────────────────────────────
COMMENT BRANCHER VOTRE API IA
──────────────────────────────────────────────────────────────────────────────
1. Installez le SDK de votre fournisseur dans requirements.txt :
     - Perplexity / OpenAI  : openai>=1.0.0
     - Anthropic            : anthropic>=0.25.0

2. Ajoutez votre clé dans .env :
     AI_API_KEY=votre_cle
     AI_PROVIDER=perplexity  # ou : openai | anthropic

3. Dans la fonction generate_book_summary() ci-dessous, repérez le bloc
   marqué "── REMPLACER LE MOCK ICI ──" et substituez-y l'appel API.

4. Le prompt de base est déjà construit dans _build_prompt(book).
   Adaptez-le si nécessaire selon le modèle choisi.
──────────────────────────────────────────────────────────────────────────────
"""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Book


# ─── Construction du prompt ───────────────────────────────────────────────────

def _build_prompt(book: "Book") -> str:
    """
    Construit le prompt envoyé à l'API IA à partir des métadonnées du livre
    et des notes brutes de l'utilisateur.

    Personnalisez ce prompt selon le modèle / fournisseur utilisé.
    """
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

Réponds en JSON valide avec exactement ces clés :
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
    Génère la fiche de lecture d'un livre.

    Retourne un dict avec les clés :
        summary, concepts, quotes, links_to_themes, usage_ideas

    ── REMPLACER LE MOCK ICI ────────────────────────────────────────────────
    Décommentez et adaptez le bloc correspondant à votre fournisseur IA.

    ❶ Perplexity / OpenAI (API compatible)
    ─────────────────────────────────────
    # from openai import OpenAI
    # client = OpenAI(
    #     api_key=os.environ["AI_API_KEY"],
    #     base_url="https://api.perplexity.ai",  # Supprimer pour OpenAI pur
    # )
    # response = client.chat.completions.create(
    #     model="llama-3.1-sonar-large-128k-online",  # Adapter selon modèle
    #     messages=[
    #         {"role": "system", "content": "Tu es un assistant philosophique."},
    #         {"role": "user", "content": _build_prompt(book)},
    #     ],
    #     response_format={"type": "json_object"},
    # )
    # import json
    # return json.loads(response.choices[0].message.content)

    ❷ Anthropic Claude
    ──────────────────
    # import anthropic, json
    # client = anthropic.Anthropic(api_key=os.environ["AI_API_KEY"])
    # message = client.messages.create(
    #     model="claude-opus-4-5",
    #     max_tokens=2048,
    #     messages=[{"role": "user", "content": _build_prompt(book)}],
    # )
    # return json.loads(message.content[0].text)
    ─────────────────────────────────────────────────────────────────────────
    """

    # ── MOCK — À remplacer par l'un des blocs ci-dessus ──────────────────────
    return {
        "summary": (
            f"[MOCK] {book.title} de {book.author} est un ouvrage majeur "
            f"de type {book.type_label}. Ce résumé est un placeholder "
            f"en attente du branchement de l'API IA. "
            f"Il abordera les thèmes centraux de l'œuvre, ses enjeux "
            f"philosophiques et son contexte historique."
        ),
        "concepts": (
            "- **[MOCK] Concept 1** : description placeholder\n"
            "- **[MOCK] Concept 2** : description placeholder\n"
            "- **[MOCK] Concept 3** : description placeholder"
        ),
        "quotes": (
            "[MOCK] Citation 1 — p. XX\n"
            "[MOCK] Citation 2 — p. XX\n"
            "[MOCK] Citation 3 — p. XX"
        ),
        "links_to_themes": (
            "[MOCK] Ce livre s'articule aux thèmes suivants : aliénation, "
            "domination, post-vérité, capitalisme. "
            "Détail à générer via l'API IA."
        ),
        "usage_ideas": (
            "1. [MOCK] Idée de thread\n"
            "2. [MOCK] Idée de scène de roman\n"
            "3. [MOCK] Argument d'essai"
        ),
    }
    # ── FIN MOCK ──────────────────────────────────────────────────────────────
