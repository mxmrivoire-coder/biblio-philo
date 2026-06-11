"""
routers/books.py — Routes Mode 1 : gestion des livres et fiches de lecture.

Routes :
    GET  /books                     → liste des livres
    GET  /books/new                 → formulaire de création
    POST /books                     → enregistrement d'un nouveau livre
    GET  /books/{id}                → fiche détaillée
    POST /books/{id}/notes          → mise à jour des notes brutes
    POST /books/{id}/generate       → génération de la fiche IA
    POST /books/{id}/delete         → suppression
"""

import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book
from app.services.ai_books import generate_book_summary

router = APIRouter(prefix="/books", tags=["books"])

# ─── Liste des types et statuts (utilisée dans les formulaires) ───────────────
BOOK_TYPES = [
    ("roman", "Roman"),
    ("essai_philo", "Essai philosophique"),
    ("essai_politique", "Essai politique"),
    ("socio", "Sociologie"),
]
BOOK_STATUSES = [
    ("en_cours", "En cours"),
    ("terminé", "Terminé"),
]


# ─── Liste des livres ─────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def list_books(request: Request, db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.created_at.desc()).all()
    return request.app.state.templates.TemplateResponse(
        "books/list.html",
        {"request": request, "books": books},
    )


# ─── Formulaire de création ───────────────────────────────────────────────────

@router.get("/new", response_class=HTMLResponse)
async def new_book_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        "books/new.html",
        {
            "request": request,
            "book_types": BOOK_TYPES,
            "book_statuses": BOOK_STATUSES,
        },
    )


# ─── Enregistrement d'un nouveau livre ───────────────────────────────────────

@router.post("", response_class=RedirectResponse)
async def create_book(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    type: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    book = Book(title=title.strip(), author=author.strip(), type=type, status=status)
    db.add(book)
    db.commit()
    db.refresh(book)
    return RedirectResponse(url=f"/books/{book.id}", status_code=303)


# ─── Fiche détaillée ──────────────────────────────────────────────────────────

@router.get("/{book_id}", response_class=HTMLResponse)
async def book_detail(request: Request, book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return request.app.state.templates.TemplateResponse(
        "books/detail.html",
        {"request": request, "book": book},
    )


# ─── Mise à jour des notes brutes ─────────────────────────────────────────────

@router.post("/{book_id}/notes", response_class=RedirectResponse)
async def update_notes(
    book_id: int,
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    book.user_notes = notes.strip() or None
    db.commit()
    return RedirectResponse(url=f"/books/{book_id}?flash=notes_saved", status_code=303)


# ─── Génération de la fiche IA ────────────────────────────────────────────────

@router.post("/{book_id}/generate", response_class=RedirectResponse)
async def generate_fiche(
    book_id: int,
    db: Session = Depends(get_db),
):
    """
    Appelle generate_book_summary() (app/services/ai_books.py),
    puis met à jour les champs ai_* du livre.

    ── POINT DE BRANCHEMENT IA ──────────────────────────────────────────────
    Rien à modifier ici : remplacez uniquement le mock dans ai_books.py.
    ─────────────────────────────────────────────────────────────────────────
    """
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")

    result = generate_book_summary(book)

    book.ai_summary = result.get("summary")
    book.ai_concepts = result.get("concepts")
    book.ai_quotes = result.get("quotes")
    book.ai_links_to_themes = result.get("links_to_themes")
    book.ai_usage_ideas = result.get("usage_ideas")
    db.commit()

    return RedirectResponse(url=f"/books/{book_id}?flash=fiche_generated", status_code=303)


# ─── Suppression ──────────────────────────────────────────────────────────────

@router.post("/{book_id}/delete", response_class=RedirectResponse)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    db.delete(book)
    db.commit()
    return RedirectResponse(url="/books?flash=book_deleted", status_code=303)
