from __future__ import annotations

from http import HTTPStatus

from flask import Blueprint, request

from ..core import APIError
from ..models import Transaction
from ..services.library_service import LibraryService

bp = Blueprint("transactions", __name__)


@bp.get("/")
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

    transactions = [txn.to_dict() for txn in query.order_by(Transaction.issued_at.asc()).all()]
    return {"items": transactions}


@bp.post("/issue")
def issue_book_route():
    payload = request.get_json(silent=True) or {}

    try:
        result = LibraryService.issue_book(
            book_id=int(payload.get("book_id")),
            member_id=int(payload.get("member_id"))
        )
    except (TypeError, ValueError):
        raise APIError("book_id and member_id must be integers")

    return result.transaction.to_dict(), HTTPStatus.CREATED


@bp.post("/return")
def return_book_route():
    payload = request.get_json(silent=True) or {}

    try:
        result = LibraryService.return_book(
            transaction_id=int(payload.get("transaction_id")),
            payment_amount=payload.get("payment_amount"),
        )
    except (TypeError, ValueError):
        raise APIError("transaction_id must be provided and numeric")

    return {
        "transaction": result.transaction.to_dict(),
        "member": result.member.to_dict(),
        "rent_fee": float(result.rent_fee)
    }

