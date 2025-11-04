from __future__ import annotations

from flask.cli import FlaskGroup

from app import create_app
from app.core import db

app = create_app()
cli = FlaskGroup(app)


@cli.command("init-db")
def init_db():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        print("Database initialised.")


if __name__ == "__main__":
    cli()
