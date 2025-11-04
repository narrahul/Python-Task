from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from ..core.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Book(db.Model, TimestampMixin):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(32), unique=True)
    publisher = db.Column(db.String(255))
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)

    transactions = db.relationship("Transaction", back_populates="book", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Member(db.Model, TimestampMixin):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    outstanding_debt = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    transactions = db.relationship("Transaction", back_populates="member", lazy="dynamic")

    def to_dict(self) -> dict:
        outstanding = Decimal(self.outstanding_debt or 0)
        return {
            "id": self.id,
            "full_name": self.full_name,
            "outstanding_debt": float(outstanding),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Transaction(db.Model, TimestampMixin):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="issued")
    issued_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    returned_at = db.Column(db.DateTime)
    rent_fee = db.Column(db.Numeric(10, 2), default=0)

    book = db.relationship("Book", back_populates="transactions")
    member = db.relationship("Member", back_populates="transactions")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "status": self.status,
            "book_title": self.book.title if self.book else None,
            "member_name": self.member.full_name if self.member else None,
            "issue_date": self.issued_at.isoformat() if self.issued_at else None,
            "return_date": self.returned_at.isoformat() if self.returned_at else None,
            "rent_fee": float(self.rent_fee or 0),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


