"""
routers/admin.py — Routes d'administration (export / import de données).

Routes :
    GET  /admin/export          → télécharge toutes les données en JSON
    GET  /admin/export/books    → uniquement les livres en JSON
    POST /admin/import          → réimporte un fichier JSON exporté précédemment
    GET  /admin                 → page d'administration
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, ConceptMap, ProblemSet

router = APIRouter(prefix="/admin", tags=["admin"])


# ─── Page d'administration ────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    nb_books = db.query(Book).count()
    nb_maps = db.query(ConceptMap).count()
    nb_problems = db.query(ProblemSet).count()
    return request.app.state.templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "nb_books": nb_books,
            "nb_maps": nb_maps,
            "nb_problems": nb_problems,
        },
    )


# ─── Export complet en JSON ───────────────────────────────────────────────────

@router.get("/export")
async def export_all(db: Session = Depends(get_db)):
    """
    Exporte l'intégralité de la bibliothèque en JSON téléchargeable.
    Inclut : livres, cartes conceptuelles, ensembles de problématiques.
    """
    books = db.query(Book).order_by(Book.id).all()
    maps = db.query(ConceptMap).order_by(ConceptMap.id).all()
    problems = db.query(ProblemSet).order_by(ProblemSet.id).all()

    data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "books": [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "type": b.type,
                "status": b.status,
                "user_notes": b.user_notes,
                "ai_summary": b.ai_summary,
                "ai_concepts": b.ai_concepts,
                "ai_quotes": b.ai_quotes,
                "ai_links_to_themes": b.ai_links_to_themes,
                "ai_usage_ideas": b.ai_usage_ideas,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in books
        ],
        "concept_maps": [
            {
                "id": m.id,
                "title": m.title,
                "theme": m.theme,
                "authors": m.authors,
                "nodes": m.nodes,
                "edges": m.edges,
                "summary_10_lines": m.summary_10_lines,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in maps
        ],
        "problem_sets": [
            {
                "id": p.id,
                "title": p.title,
                "theme": p.theme,
                "authors": p.authors,
                "orientation": p.orientation,
                "problems": p.problems,
                "plans": p.plans,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in problems
        ],
    }

    filename = f"bibliothecaire_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─── Import depuis un fichier JSON exporté ────────────────────────────────────

@router.post("/import", response_class=RedirectResponse)
async def import_data(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Réimporte un fichier JSON produit par /admin/export.
    Les entrées dont l'id existe déjà en base sont ignorées (pas d'écrasement).
    """
    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return request.app.state.templates.TemplateResponse(
            "admin.html",
            {"request": request, "error": "Fichier JSON invalide."},
            status_code=400,
        )

    imported = {"books": 0, "maps": 0, "problems": 0}

    for b in data.get("books", []):
        if not db.get(Book, b["id"]):
            db.add(Book(
                id=b["id"],
                title=b["title"],
                author=b["author"],
                type=b.get("type", "essai_philo"),
                status=b.get("status", "en_cours"),
                user_notes=b.get("user_notes"),
                ai_summary=b.get("ai_summary"),
                ai_concepts=b.get("ai_concepts"),
                ai_quotes=b.get("ai_quotes"),
                ai_links_to_themes=b.get("ai_links_to_themes"),
                ai_usage_ideas=b.get("ai_usage_ideas"),
            ))
            imported["books"] += 1

    for m in data.get("concept_maps", []):
        if not db.get(ConceptMap, m["id"]):
            db.add(ConceptMap(
                id=m["id"],
                title=m["title"],
                theme=m["theme"],
                authors=m.get("authors"),
                nodes=m.get("nodes"),
                edges=m.get("edges"),
                summary_10_lines=m.get("summary_10_lines"),
            ))
            imported["maps"] += 1

    for p in data.get("problem_sets", []):
        if not db.get(ProblemSet, p["id"]):
            db.add(ProblemSet(
                id=p["id"],
                title=p["title"],
                theme=p["theme"],
                authors=p.get("authors"),
                orientation=p.get("orientation", "essai"),
                problems=p.get("problems"),
                plans=p.get("plans"),
            ))
            imported["problems"] += 1

    db.commit()
    msg = f"import_ok_{imported['books']}livres_{imported['maps']}cartes_{imported['problems']}problematiques"
    return RedirectResponse(url=f"/admin?flash={msg}", status_code=303)
