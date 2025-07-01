# FastAPI Backend Boilerplate

A scalable, modular, and production-ready FastAPI backend for commercial use, designed to integrate with a Next.js (TypeScript) frontend.

## Features
- JWT authentication (email/password & social login)
- Role-based access (user/admin)
- User profiles
- File uploads (floor plans)
- Floor plan analysis (background task)
- Chatbot API
- Blog/content system (CRUD)
- Analytics & usage limits
- Legal endpoints
- PostgreSQL + Alembic migrations
- CORS for Next.js frontend

## Quickstart

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Configure environment:**
   - Copy `.env.example` to `.env` and fill in your secrets and DB config.
3. **Run migrations:**
   ```sh
   alembic upgrade head
   ```
4. **Start the server:**
   ```sh
   uvicorn app.main:app --reload
   ```

## Folder Structure
```
app/
  main.py
  core/
  models/
  schemas/
  api/
  services/
  db/
  utils/
  static/
  legal/
.env
alembic.ini
```

## CORS
- By default, allows all `http://localhost:*` origins for development.
- Set `FRONTEND_ORIGINS` in `.env` for production domains.

---
