# Library Management App

Simple librarian dashboard built with Flask + React. It keeps tabs on books, members, loans, and lets you pull new books from the public Frappe catalogue.

## What it does
- add / edit / search books and members (stock updates itself when you issue or return)
- issue books until a member would cross the Rs.500 debt ceiling
- return books, capture the rent that was paid, and show it in the running balance
- show a lightweight activity table so you can see the last few moves
- import batches of books straight from the Frappe API

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py init-db
flask --app wsgi run --reload
```
API lives at `http://localhost:5000/api`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Vite serves the UI on `http://localhost:5173` and proxies anything under `/api` to Flask.

### Environment bits
- SQLite database is stored at `backend/library.db`. Tweak `app/config.py` if you want a different path.
- Frappe import needs outbound internet access.

## API cheat sheet

| Method | Endpoint | Notes |
| ------ | -------- | ----- |
| GET | `/api/books/` | list/search books |
| POST | `/api/books/` | add a book |
| PUT | `/api/books/{id}` | update book |
| DELETE | `/api/books/{id}` | delete book (only if no active issues) |
| GET | `/api/members/` | list members |
| POST | `/api/members/` | add member |
| PUT | `/api/members/{id}` | update member |
| DELETE | `/api/members/{id}` | delete member (prompts if they still have issues) |
| GET | `/api/transactions/` | list activity, supports `status`, `book_id`, `member_id` filters |
| POST | `/api/transactions/issue` | issue a book |
| POST | `/api/transactions/return` | return a book + record rent fee |
| POST | `/api/imports/books` | import books from Frappe |

## Screenshots
Images live in `frontend/screenshots/`. 

