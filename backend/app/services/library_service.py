from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ..core import APIError, db
from ..models import Book, Member, Transaction

MAX_ALLOWED_DEBT = Decimal("500.00")
DAILY_RENT_FEE = Decimal("5.00")


@dataclass(slots=True)
class IssueResult:
    transaction: Transaction
    book: Book
    member: Member


@dataclass(slots=True)
class ReturnResult:
    transaction: Transaction
    book: Book
    member: Member
    rent_fee: Decimal


class LibraryService:
    @staticmethod
    def issue_book(*, book_id: int, member_id: int) -> IssueResult:
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

        transaction = Transaction(
            book=book,
            member=member,
            status="issued",
            issued_at=issued_at,
        )

        book.available_copies -= 1

        db.session.add(transaction)
        db.session.commit()

        return IssueResult(transaction=transaction, book=book, member=member)

    @staticmethod
    def return_book(
        *,
        transaction_id: int,
        payment_amount: Decimal | float | int | None = None,
        return_date: datetime | None = None,
    ) -> ReturnResult:
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

        completed_at = return_date or datetime.utcnow()
        days_out = (completed_at.date() - transaction.issued_at.date()).days
        days_out = max(days_out, 1)
        rent_fee = DAILY_RENT_FEE * Decimal(days_out)

        outstanding = Decimal(member.outstanding_debt or 0) + rent_fee
        payment = Decimal(payment_amount or 0)
        if payment > 0:
            outstanding -= payment

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

        return ReturnResult(
            transaction=transaction,
            book=book,
            member=member,
            rent_fee=rent_fee,
        )
