from __future__ import annotations

from http import HTTPStatus

from flask import Blueprint, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..core import APIError, db
from ..models import Book, Transaction

bp = Blueprint("books", __name__)


@bp.get("/")
def list_books():
    search = request.args.get("search")

    query = Book.query
    if search:
        wildcard = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Book.title).like(wildcard)
            | func.lower(Book.authors).like(wildcard)
            | func.lower(Book.publisher).like(wildcard)
        )

    books = [book.to_dict() for book in query.order_by(Book.title.asc()).all()]
    return {"items": books}


@bp.post("/")
def create_book():
    payload = request.get_json(silent=True) or {}

    title = (payload.get("title") or "").strip()
    authors = (payload.get("authors") or "").strip()
    if not title or not authors:
        raise APIError("Both title and authors are required")

    total_copies = _as_int(payload.get("total_copies", 1), field="total_copies")
    if total_copies < 1:
        raise APIError("total_copies must be at least 1")

    available_copies = payload.get("available_copies", total_copies)
    available_copies = _as_int(available_copies, field="available_copies")
    if available_copies < 0 or available_copies > total_copies:
        raise APIError("available_copies must be between 0 and total_copies")

    book = Book(
        title=title,
        authors=authors,
        isbn=(payload.get("isbn") or "").strip() or None,
        publisher=(payload.get("publisher") or "").strip() or None,
        total_copies=total_copies,
        available_copies=available_copies,
    )

    db.session.add(book)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIError("ISBN already exists", status_code=409)

    return book.to_dict(), HTTPStatus.CREATED


@bp.put("/<int:book_id>")
@bp.patch("/<int:book_id>")
def update_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    payload = request.get_json(silent=True) or {}

    if "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            raise APIError("title cannot be empty")
        book.title = title

    if "authors" in payload:
        authors = (payload.get("authors") or "").strip()
        if not authors:
            raise APIError("authors cannot be empty")
        book.authors = authors

    for attr in ("isbn", "publisher"):
        if attr in payload:
            value = (payload.get(attr) or "").strip() or None
            setattr(book, attr, value)

    issued_copies = book.total_copies - book.available_copies

    if "total_copies" in payload:
        total = _as_int(payload["total_copies"], field="total_copies")
        if total < issued_copies:
            raise APIError("total_copies cannot be less than currently issued copies")
        book.total_copies = total
        if book.available_copies > total:
            book.available_copies = total

    if "available_copies" in payload:
        available = _as_int(payload["available_copies"], field="available_copies")
        if available < 0 or available > book.total_copies:
            raise APIError("available_copies must be between 0 and total_copies")
        if available < book.total_copies - issued_copies:
            raise APIError("available_copies cannot be less than issued copies")
        book.available_copies = available

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIError("ISBN already exists", status_code=409)
    return book.to_dict()


@bp.delete("/<int:book_id>")
def delete_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    active_loans = Transaction.query.filter_by(book_id=book.id, status="issued").count()
    if active_loans:
        raise APIError("Cannot delete a book with active issues")

    db.session.delete(book)
    db.session.commit()
    return {"status": "deleted"}, HTTPStatus.NO_CONTENT


def _as_int(value, *, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise APIError(f"{field} must be an integer")


