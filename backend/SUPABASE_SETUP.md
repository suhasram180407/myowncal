# Supabase PostgreSQL setup

## 1. Configure `backend/.env`

Copy from `.env.example` and fill:

- `DATABASE_URL` — Supabase **Connection string** (URI), change prefix to `postgresql+asyncpg://`
- `SUPABASE_URL` — project URL
- `SUPABASE_ANON_KEY` — anon key (frontend future use only)
- `SECRET_KEY` — random string for JWT

Example shape (do not commit real values):

```env
DATABASE_URL=postgresql+asyncpg://postgres.[ref]:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?ssl=require
```

## 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 3. Run migrations

```bash
cd backend
alembic upgrade head
```

## 4. Start API (LAN for Expo Go)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 5. Verify

```bash
curl http://127.0.0.1:8000/health
```

Expect `"database": "connected"`.

## API smoke test

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"password\":\"secret123\"}"

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"secret123\"}"
```

Use `access_token` as `Authorization: Bearer <token>` for `/api/users/me`, `/api/meals/`, `/api/analytics/daily`.
