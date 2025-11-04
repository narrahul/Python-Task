from __future__ import annotations

from http import HTTPStatus

import requests
from flask import Blueprint, request

from ..core import APIError, db
from ..models import Book

bp = Blueprint("imports", __name__)

FRAPPE_API_URL = "https://frappe.io/api/method/frappe-library"


@bp.post("/books")
def import_books():
    payload = request.get_json(silent=True) or {}

    total_to_import = _as_positive_int(payload.get("count", 20), "count")

    imported = 0
    duplicates = 0
    new_books: list[Book] = []
    current_page = 1

    session = requests.Session()

    while imported < total_to_import:
        response = session.get(FRAPPE_API_URL, params={"page": current_page}, timeout=15)
        response.raise_for_status()
        data = response.json()
        books = data.get("message", [])

        if not books:
            break

        for record in books:
            if imported >= total_to_import:
                break

            isbn = record.get("isbn") or record.get("isbn13")
            if isbn and Book.query.filter_by(isbn=isbn).first():
                duplicates += 1
                continue

            book = Book(
                title=record.get("title", "Untitled"),
                authors=record.get("authors", "Unknown"),
                isbn=isbn,
                publisher=record.get("publisher"),
                total_copies=1,
                available_copies=1,
            )
            db.session.add(book)
            new_books.append(book)
            imported += 1

        current_page += 1

    if new_books:
        db.session.commit()
    else:
        db.session.rollback()

    return {
        "imported": imported,
        "duplicates": duplicates,
        "inserted_ids": [book.id for book in new_books],
    }, HTTPStatus.CREATED


def _as_positive_int(value, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise APIError(f"{field} must be an integer")
    if number <= 0:
        raise APIError(f"{field} must be greater than zero")
    return number

