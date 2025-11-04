from __future__ import annotations

from decimal import Decimal
from http import HTTPStatus

from flask import Blueprint, request
from sqlalchemy import func

from ..core import APIError, db
from ..models import Member, Transaction

bp = Blueprint("members", __name__)


@bp.get("/")
def list_members():
    search = request.args.get("search")
    query = Member.query

    if search:
        wildcard = f"%{search.lower()}%"
        query = query.filter(func.lower(Member.full_name).like(wildcard))

    members = [member.to_dict() for member in query.order_by(Member.full_name.asc()).all()]
    return {"items": members}


@bp.post("/")
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


@bp.put("/<int:member_id>")
@bp.patch("/<int:member_id>")
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
        if debt > Decimal("500"):
            raise APIError("Outstanding debt cannot exceed Rs.500")
        member.outstanding_debt = debt

    db.session.commit()
    return member.to_dict()


@bp.delete("/<int:member_id>")
def delete_member(member_id: int):
    member = Member.query.get_or_404(member_id)
    active_loans = Transaction.query.filter_by(member_id=member.id, status="issued").count()
    if active_loans:
        raise APIError("Cannot delete member with active transactions")

    Transaction.query.filter_by(member_id=member.id).delete(synchronize_session=False)
    db.session.delete(member)
    db.session.commit()
    return {"status": "deleted"}, HTTPStatus.NO_CONTENT



def _non_negative_decimal(value, field: str) -> Decimal:
    try:
        amount = Decimal(str(value or 0))
    except (TypeError, ValueError, ArithmeticError):
        raise APIError(f"{field} must be numeric")
    if amount < 0:
        raise APIError(f"{field} cannot be negative")
    return amount
