from . import books, members, transactions, imports

def register_api_blueprints(app):
    app.register_blueprint(books.bp, url_prefix="/api/books")
    app.register_blueprint(members.bp, url_prefix="/api/members")
    app.register_blueprint(transactions.bp, url_prefix="/api/transactions")
    app.register_blueprint(imports.bp, url_prefix="/api/imports")
