from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from http import HTTPStatus

import requests
from flask import request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..core import APIError, db
from ..models import Book, Member, Transaction

MAX_ALLOWED_DEBT = Decimal("500.00")
DAILY_RENT_FEE = Decimal("5.00")
FRAPPE_API_URL = "https://frappe.io/api/method/frappe-library"


def register_routes(app):
    @app.get("/api/books/")
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

        items = [book.to_dict() for book in query.order_by(Book.title.asc()).all()]
        return {"items": items}

    @app.post("/api/books/")
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

    @app.put("/api/books/<int:book_id>")
    @app.patch("/api/books/<int:book_id>")
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

    @app.delete("/api/books/<int:book_id>")
    def delete_book(book_id: int):
        book = Book.query.get_or_404(book_id)
        active_loans = Transaction.query.filter_by(book_id=book.id, status="issued").count()
        if active_loans:
            raise APIError("Cannot delete a book with active issues")

        db.session.delete(book)
        db.session.commit()
        return {"status": "deleted"}, HTTPStatus.NO_CONTENT

    @app.get("/api/members/")
    def list_members():
        search = request.args.get("search")
        query = Member.query

        if search:
            wildcard = f"%{search.lower()}%"
            query = query.filter(func.lower(Member.full_name).like(wildcard))

        items = [member.to_dict() for member in query.order_by(Member.full_name.asc()).all()]
        return {"items": items}

    @app.post("/api/members/")
    def create_member():
        payload = request.get_json(silent=True) or {}

        full_name = (payload.get("full_name") or "").strip()
        if not full_name:
            raise APIError("full_name is required")

        member = Member(
            full_name=full_name,
            outstanding_debt=_non_negative_decimal(payload.get("outstanding_debt", 0), "outstanding_debt")
        )

        db.session.add(member)
        db.session.commit()

        return member.to_dict(), HTTPStatus.CREATED

    @app.put("/api/members/<int:member_id>")
    @app.patch("/api/members/<int:member_id>")
    def update_member(member_id: int):
        member = Member.query.get_or_404(member_id)
        payload = request.get_json(silent=True) or {}

        if "full_name" in payload:
            full_name = (payload.get("full_name") or "").strip()
            if not full_name:
                raise APIError("full_name cannot be empty")
            member.full_name = full_name

        if "outstanding_debt" in payload:
            debt = _non_negative_decimal(payload.get("outstanding_debt"), "outstanding_debt")
            if debt > MAX_ALLOWED_DEBT:
                raise APIError("Outstanding debt cannot exceed Rs.500")
            member.outstanding_debt = debt

        db.session.commit()
        return member.to_dict()

    @app.delete("/api/members/<int:member_id>")
    def delete_member(member_id: int):
        member = Member.query.get_or_404(member_id)
        active_loans = Transaction.query.filter_by(member_id=member.id, status="issued").count()
        if active_loans:
            raise APIError("Cannot delete member with active transactions")

        Transaction.query.filter_by(member_id=member.id).delete(synchronize_session=False)
        db.session.delete(member)
        db.session.commit()
        return {"status": "deleted"}, HTTPStatus.NO_CONTENT

    @app.get("/api/transactions/")
    def list_transactions():
        status = request.args.get("status")
        member_id = request.args.get("member_id", type=int)
        book_id = request.args.get("book_id", type=int)

        query = Transaction.query
        if status:
            query = query.filter(Transaction.status == status)
        if member_id:
            query = query.filter(Transaction.member_id == member_id)
        if book_id:
            query = query.filter(Transaction.book_id == book_id)

        items = [txn.to_dict() for txn in query.order_by(Transaction.issued_at.asc()).all()]
        return {"items": items}

    @app.post("/api/transactions/issue")
    def issue_book():
        payload = request.get_json(silent=True) or {}
        try:
            book_id = int(payload.get("book_id"))
            member_id = int(payload.get("member_id"))
        except (TypeError, ValueError):
            raise APIError("book_id and member_id must be integers")

        book = Book.query.get(book_id)
        if not book:
            raise APIError("Book not found", status_code=404)

        member = Member.query.get(member_id)
        if not member:
            raise APIError("Member not found", status_code=404)

        if Decimal(member.outstanding_debt or 0) > MAX_ALLOWED_DEBT:
            raise APIError("Member outstanding debt exceeds Rs.500", status_code=409)

        if book.available_copies < 1:
            raise APIError("No available copies for this book", status_code=409)

        issued_at = datetime.utcnow()
        due_at = issued_at + timedelta(days=14)

        transaction = Transaction(
            book=book,
            member=member,
            status="issued",
            issued_at=issued_at,
            due_at=due_at,
        )

        book.available_copies -= 1
        db.session.add(transaction)
        db.session.commit()

        return transaction.to_dict(), HTTPStatus.CREATED

    @app.post("/api/transactions/return")
    def return_book():
        payload = request.get_json(silent=True) or {}
        try:
            transaction_id = int(payload.get("transaction_id"))
        except (TypeError, ValueError):
            raise APIError("transaction_id must be provided and numeric")

        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            raise APIError("Transaction not found", status_code=404)

        if transaction.status != "issued":
            raise APIError("Only issued transactions can be returned", status_code=409)

        book = transaction.book
        member = transaction.member

        if book.available_copies >= book.total_copies:
            raise APIError(
                "Book inventory mismatch: all copies are already marked as available",
                status_code=409,
            )

        completed_at = datetime.utcnow()
        days_out = max((completed_at.date() - transaction.issued_at.date()).days, 1)
        rent_fee = DAILY_RENT_FEE * Decimal(days_out)

        outstanding = Decimal(member.outstanding_debt or 0) + rent_fee
        payment_amount = payload.get("payment_amount")
        if payment_amount not in (None, ""):
            try:
                payment_value = Decimal(str(payment_amount))
            except (ArithmeticError, ValueError):
                raise APIError("payment_amount must be numeric")
            outstanding -= payment_value

        if outstanding < 0:
            outstanding = Decimal("0")

        if outstanding > MAX_ALLOWED_DEBT:
            raise APIError(
                "Outstanding debt would exceed Rs.500. Collect payment before returning the book.",
                status_code=409,
            )

        transaction.status = "returned"
        transaction.returned_at = completed_at
        transaction.rent_fee = rent_fee

        book.available_copies += 1
        member.outstanding_debt = outstanding

        db.session.commit()

        return {
            "transaction": transaction.to_dict(),
            "member": member.to_dict(),
            "rent_fee": float(rent_fee)
        }

    @app.post("/api/imports/books")
    def import_books():
        payload = request.get_json(silent=True) or {}
        total_to_import = _as_positive_int(payload.get("count", 20), "count")

        filters = {
            key: value
            for key, value in payload.items()
            if key in {"title", "authors", "isbn", "publisher"} and value
        }

        imported = 0
        duplicates = 0
        new_books: list[Book] = []
        current_page = 1
        session = requests.Session()

        while imported < total_to_import:
            response = session.get(
                FRAPPE_API_URL,
                params={"page": current_page, **filters},
                timeout=15,
            )
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


def _as_int(value, *, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise APIError(f"{field} must be an integer")


def _non_negative_decimal(value, field: str) -> Decimal:
    try:
        amount = Decimal(str(value or 0))
    except (TypeError, ValueError, ArithmeticError):
        raise APIError(f"{field} must be numeric")
    if amount < 0:
        raise APIError(f"{field} cannot be negative")
    return amount


def _as_positive_int(value, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise APIError(f"{field} must be an integer")
    if number <= 0:
        raise APIError(f"{field} must be greater than zero")
    return number
