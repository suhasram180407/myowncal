# CalorieTracker API — Phase 1

AI-powered calorie tracking backend built with FastAPI + PostgreSQL.

---

## Quick Start (Local — VS Code)

### 1. Prerequisites
- Python 3.12+
- PostgreSQL running locally (or use Docker)
- VS Code with Python extension

### 2. Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/caloriedb
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Generate a strong SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Create PostgreSQL Database

```sql
CREATE DATABASE caloriedb;
```

### 5. Run the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on first startup.

### 6. API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc
- Health:      http://localhost:8000/health

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login, get JWT token |

### Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users/me | Get my profile + calorie targets |
| PUT | /api/users/me | Update profile (triggers calorie recalc) |

### Meals
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/meals/ | Log a food entry |
| GET | /api/meals/?day=YYYY-MM-DD | List meals for a day |
| DELETE | /api/meals/{id} | Delete a meal |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/analytics/daily-summary?day=YYYY-MM-DD | Calories consumed/remaining + macros |
| GET | /api/analytics/dataset-stats | ML dataset quality counts |

---

## Postman Authentication

1. Login → copy `access_token`
2. In Postman: Authorization → Bearer Token → paste token
3. All protected routes require this header

---

## Run Tests

```bash
cd backend
pytest
```

---

## Docker (Alternative)

```bash
cd backend
docker-compose up --build
```

---

## ML Pipeline Scripts

```bash
# Check if dataset is ready for training
python -m app.ml.readiness_check

# Split dataset into train/val/test
python -m app.ml.dataset_splitter
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, routers, middleware
│   ├── config/settings.py   # Env vars via pydantic-settings
│   ├── database/session.py  # Async SQLAlchemy engine + session
│   ├── models/              # ORM models (User, Meal, DatasetEntry)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routes/              # FastAPI routers
│   ├── services/            # Business logic
│   ├── utils/               # JWT, hashing
│   ├── middleware/          # Error handling, logging
│   ├── ml/                  # Dataset pipeline, preprocessing, AI placeholders
│   └── tests/               # pytest tests
├── datasets/                # raw/processed/train/val/test splits
├── uploads/                 # Phase 2: food images
├── logs/                    # Application logs
├── .env                     # Environment variables (never commit)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Phase 2 (Coming Later)

- Food image upload via Cloudinary
- OpenAI Vision API for food detection
- YOLOv8 food localization
- PyTorch calorie estimation model
- Indian food recognition
