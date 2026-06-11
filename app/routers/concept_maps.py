"""
routers/concept_maps.py — Routes Mode 2 : cartes conceptuelles.

Routes :
    GET  /concept-maps          → liste des cartes
    GET  /concept-maps/new      → formulaire de création
    POST /concept-maps          → création + génération IA
    GET  /concept-maps/{id}     → détail d'une carte
    POST /concept-maps/{id}/delete → suppression
"""

import json

import traceback

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ConceptMap
from app.services.ai_concepts import generate_concept_map

router = APIRouter(prefix="/concept-maps", tags=["concept_maps"])

# ─── Liste prédéfinie d'auteurs (éditable ici ou déplaçable en config) ────────
PREDEFINED_AUTHORS = [
    "Marx", "Camus", "Fanon", "Arendt", "Foucault",
    "Bourdieu", "Gramsci", "Mhalla", "Sartre", "Althusser",
    "Spinoza", "Nietzsche", "Deleuze", "Weil",
]


# ─── Liste des cartes ─────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def list_concept_maps(request: Request, db: Session = Depends(get_db)):
    maps = db.query(ConceptMap).order_by(ConceptMap.created_at.desc()).all()
    return request.app.state.templates.TemplateResponse(
        "concept_maps/list.html",
        {"request": request, "maps": maps},
    )


# ─── Formulaire de création ───────────────────────────────────────────────────

@router.get("/new", response_class=HTMLResponse)
async def new_map_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        "concept_maps/new.html",
        {"request": request, "predefined_authors": PREDEFINED_AUTHORS},
    )


# ─── Création + génération ────────────────────────────────────────────────────

@router.post("", response_class=RedirectResponse)
async def create_concept_map(
    request: Request,
    title: str = Form(...),
    theme: str = Form(...),
    authors: list[str] = Form(default=[]),
    extra_author: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Crée une carte et appelle generate_concept_map() pour la remplir.

    ── POINT DE BRANCHEMENT IA ──────────────────────────────────────────────
    Rien à modifier ici : remplacez uniquement le mock dans ai_concepts.py.
    ─────────────────────────────────────────────────────────────────────────
    """
    # Fusion auteurs prédéfinis + auteur libre
    all_authors = list(authors)
    if extra_author.strip():
        all_authors.append(extra_author.strip())

    try:
        result = generate_concept_map(theme=theme, authors=all_authors)
    except Exception as e:
        error_detail = traceback.format_exc()
        return request.app.state.templates.TemplateResponse(
            "concept_maps/new.html",
            {
                "request": request,
                "predefined_authors": PREDEFINED_AUTHORS,
                "error": f"Erreur lors de la génération IA : {e}",
                "error_detail": error_detail,
            },
            status_code=500,
        )

    concept_map = ConceptMap(
        title=title.strip(),
        theme=theme.strip(),
        authors=json.dumps(all_authors, ensure_ascii=False),
        nodes=json.dumps(result.get("nodes", {}), ensure_ascii=False),
        edges=json.dumps(result.get("edges", []), ensure_ascii=False),
        summary_10_lines=result.get("summary_10_lines"),
    )
    db.add(concept_map)
    db.commit()
    db.refresh(concept_map)
    return RedirectResponse(url=f"/concept-maps/{concept_map.id}", status_code=303)


# ─── Détail d'une carte ───────────────────────────────────────────────────────

@router.get("/{map_id}", response_class=HTMLResponse)
async def concept_map_detail(request: Request, map_id: int, db: Session = Depends(get_db)):
    concept_map = db.get(ConceptMap, map_id)
    if not concept_map:
        raise HTTPException(status_code=404, detail="Carte introuvable")
    return request.app.state.templates.TemplateResponse(
        "concept_maps/detail.html",
        {"request": request, "map": concept_map},
    )


# ─── Suppression ──────────────────────────────────────────────────────────────

@router.post("/{map_id}/delete", response_class=RedirectResponse)
async def delete_concept_map(map_id: int, db: Session = Depends(get_db)):
    concept_map = db.get(ConceptMap, map_id)
    if not concept_map:
        raise HTTPException(status_code=404, detail="Carte introuvable")
    db.delete(concept_map)
    db.commit()
    return RedirectResponse(url="/concept-maps?flash=map_deleted", status_code=303)
