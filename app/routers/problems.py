"""
routers/problems.py — Routes Mode 3 : problématiques et plans d'essais.

Routes :
    GET  /problems              → liste des ensembles
    GET  /problems/new          → formulaire de création
    POST /problems              → création + génération IA
    GET  /problems/{id}         → détail (problématiques + plans)
    GET  /problems/{id}/export  → téléchargement en markdown
    POST /problems/{id}/delete  → suppression
"""

import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ProblemSet
from app.services.ai_problems import generate_problems_and_plans

router = APIRouter(prefix="/problems", tags=["problems"])

# ─── Même liste que concept_maps (centralisable dans une config si besoin) ────
PREDEFINED_AUTHORS = [
    "Marx", "Camus", "Fanon", "Arendt", "Foucault",
    "Bourdieu", "Gramsci", "Mhalla", "Sartre", "Althusser",
    "Spinoza", "Nietzsche", "Deleuze", "Weil",
]

ORIENTATIONS = [
    ("thread", "Threads / réseaux sociaux"),
    ("essai", "Essai académique"),
]


# ─── Liste ────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def list_problems(request: Request, db: Session = Depends(get_db)):
    problem_sets = db.query(ProblemSet).order_by(ProblemSet.created_at.desc()).all()
    return request.app.state.templates.TemplateResponse(
        "problems/list.html",
        {"request": request, "problem_sets": problem_sets},
    )


# ─── Formulaire de création ───────────────────────────────────────────────────

@router.get("/new", response_class=HTMLResponse)
async def new_problem_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        "problems/new.html",
        {
            "request": request,
            "predefined_authors": PREDEFINED_AUTHORS,
            "orientations": ORIENTATIONS,
        },
    )


# ─── Création + génération ────────────────────────────────────────────────────

@router.post("", response_class=RedirectResponse)
async def create_problem_set(
    request: Request,
    title: str = Form(...),
    theme: str = Form(...),
    authors: list[str] = Form(default=[]),
    extra_author: str = Form(""),
    orientation: str = Form("essai"),
    db: Session = Depends(get_db),
):
    """
    Crée un ProblemSet et appelle generate_problems_and_plans().

    ── POINT DE BRANCHEMENT IA ──────────────────────────────────────────────
    Rien à modifier ici : remplacez uniquement le mock dans ai_problems.py.
    ─────────────────────────────────────────────────────────────────────────
    """
    all_authors = list(authors)
    if extra_author.strip():
        all_authors.append(extra_author.strip())

    result = generate_problems_and_plans(
        theme=theme,
        authors=all_authors,
        orientation=orientation,
    )

    problem_set = ProblemSet(
        title=title.strip(),
        theme=theme.strip(),
        authors=json.dumps(all_authors, ensure_ascii=False),
        orientation=orientation,
        problems=json.dumps(result.get("problems", []), ensure_ascii=False),
        plans=json.dumps(result.get("plans", []), ensure_ascii=False),
    )
    db.add(problem_set)
    db.commit()
    db.refresh(problem_set)
    return RedirectResponse(url=f"/problems/{problem_set.id}", status_code=303)


# ─── Détail ───────────────────────────────────────────────────────────────────

@router.get("/{ps_id}", response_class=HTMLResponse)
async def problem_set_detail(request: Request, ps_id: int, db: Session = Depends(get_db)):
    ps = db.get(ProblemSet, ps_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Ensemble introuvable")
    return request.app.state.templates.TemplateResponse(
        "problems/detail.html",
        {"request": request, "ps": ps},
    )


# ─── Export Markdown ──────────────────────────────────────────────────────────

@router.get("/{ps_id}/export")
async def export_markdown(ps_id: int, db: Session = Depends(get_db)):
    """
    Retourne un fichier .md téléchargeable contenant les problématiques et plans.
    """
    ps = db.get(ProblemSet, ps_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Ensemble introuvable")

    lines = [
        f"# {ps.title}",
        f"\n**Thème :** {ps.theme}",
        f"**Auteurs :** {', '.join(ps.authors_list)}",
        f"**Orientation :** {ps.orientation_label}",
        "\n---\n",
    ]

    for i, plan_item in enumerate(ps.plans_list, start=1):
        problem_text = plan_item.get("problem", "")
        plan = plan_item.get("plan", {})
        lines.append(f"## Problématique {i}\n")
        lines.append(f"{problem_text}\n")
        for part_key in ("I", "II", "III"):
            part = plan.get(part_key, {})
            part_title = part.get("title", "")
            lines.append(f"### {part_key}. {part_title}\n")
            for point in part.get("points", []):
                lines.append(f"- {point}")
            lines.append("")
        lines.append("\n---\n")

    content = "\n".join(lines)
    filename = f"plan_{ps.id}_{ps.theme[:30].replace(' ', '_')}.md"

    return PlainTextResponse(
        content=content,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/markdown; charset=utf-8",
        },
    )


# ─── Suppression ──────────────────────────────────────────────────────────────

@router.post("/{ps_id}/delete", response_class=RedirectResponse)
async def delete_problem_set(ps_id: int, db: Session = Depends(get_db)):
    ps = db.get(ProblemSet, ps_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Ensemble introuvable")
    db.delete(ps)
    db.commit()
    return RedirectResponse(url="/problems?flash=ps_deleted", status_code=303)
