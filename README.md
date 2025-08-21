# FastAPI Backend Boilerplate

A scalable, modular, and production-ready FastAPI backend for commercial use, designed to integrate with a Next.js (TypeScript) frontend.

## Features
- JWT authentication (email/password & social login)
- Role-based access control with page-wise permissions
- User profiles with encrypted passwords
- File uploads (floor plans)
- Floor plan analysis (background task)
- Chatbot API
- Blog/content system (CRUD)
- Analytics & usage limits
- Legal endpoints
- MySQL + Alembic migrations
- CORS for Next.js frontend

## Quickstart

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Set up MySQL database:**
   ```sh
   python setup_mysql.py
   ```
3. **Configure environment:**
   - Copy `.env.example` to `.env` and fill in your secrets and DB config.
   - Set `DATABASE_URL=mysql+pymysql://user:root@localhost/brahmavastu`
4. **Initialize database with roles:**
   ```sh
   python init_database.py
   ```
5. **Start the server:**
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
