# AI Briefing Agent with Render & PostgreSQL

A serverless AI agent that autonomously searches, filters, and summarizes custom news using LangGraph workflows. Delivers personalized briefings via email at user-scheduled times.

## Architecture

**Stack:**
- **Backend**: FastAPI + APScheduler on Render
- **Database**: PostgreSQL on Render
- **Frontend**: React + TypeScript + Vite
- **AI**: LangGraph workflow with Groq LLM and Tavily search
- **Email**: SMTP (Gmail)

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## Features

- **Autonomous LangGraph Workflow**: 8-node pipeline (search → deduplication → summarize → email)
- **Real-Time Search**: Instant news search via REST API
- **Scheduled Briefings**: Per-user timezone-aware daily briefings
- **User Management**: Registration, preferences, metrics via REST API
- **Deduplication**: Article-level and user-level duplicate prevention
- **React Dashboard**: Onboarding, real-time search, and metrics

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- PostgreSQL (local development) or Render account (deployment)
- API keys:
  - Groq API (https://console.groq.com/)
  - Tavily API (https://tavily.com/)
  - Gmail SMTP (App Password)

### Backend Setup

1. **Clone and install:**
```bash
git clone <repository-url>
cd Serverless-AI-Briefing-Agent-with-AWS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
# Copy example
cp .env.example .env

# Edit .env with your credentials
```

Required environment variables:
```env
# API Keys
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

# Database (for local: use Docker PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/briefing_db

# SMTP (Gmail)
SMTP_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
```

3. **Setup database:**

**Option A: Docker PostgreSQL (recommended for local dev)**
```bash
# Start PostgreSQL container
docker run -d \
  --name briefing-postgres \
  -e POSTGRES_USER=briefing_user \
  -e POSTGRES_PASSWORD=briefing_pass \
  -e POSTGRES_DB=briefing_db \
  -p 5432:5432 \
  postgres:15

# Run migrations
alembic upgrade head
```

**Option B: Local PostgreSQL**
```bash
# Create database
createdb briefing_db

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://your_user:your_pass@localhost:5432/briefing_db

# Run migrations
alembic upgrade head
```

4. **Start backend:**
```bash
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

Frontend: http://localhost:3000

## Usage

### Via Frontend

1. **Register** (Get Started tab):
   - Enter email
   - Select topics
   - Set timezone and briefing time
   - Click "Start Receiving Briefings"

2. **Real-Time Search** (Search Now tab):
   - Enter email and query
   - Get instant results

3. **View Metrics** (My Metrics tab):
   - Enter email
   - See total articles sent and topics

### Via API

**Register a user:**
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "preferences": {"topics": ["AI", "technology"]},
    "timezone": "America/New_York",
    "briefing_time": "09:00"
  }'
```

**Real-time query:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "query": "latest AI breakthroughs",
    "max_results": 5
  }'
```

**Get metrics:**
```bash
curl http://localhost:8000/api/metrics/user@example.com
```

### Manually Trigger Briefing (Admin)

```bash
curl -X POST http://localhost:8000/api/admin/trigger-briefing/user@example.com
```

## Deployment to Render

### Step 1: Create PostgreSQL Database

1. Sign up at [render.com](https://render.com)
2. Dashboard → "New" → "PostgreSQL"
3. Name: `briefing-db`
4. Plan: Free
5. Copy "Internal Database URL"

### Step 2: Deploy Backend

1. Push code to GitHub
2. Render Dashboard → "New" → "Web Service"
3. Connect your repository
4. Settings:
   - **Name**: `ai-briefing-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   ```
   DATABASE_URL=<from Step 1>
   GROQ_API_KEY=<your key>
   TAVILY_API_KEY=<your key>
   SMTP_ENABLED=true
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=<your Gmail>
   SMTP_PASSWORD=<your Gmail app password>
   SMTP_FROM_EMAIL=<your Gmail>
   ```
6. Click "Create Web Service"

### Step 3: Deploy Frontend (Optional)

**Option A: Vercel**
1. Connect GitHub repo
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Environment variable: `VITE_API_URL=https://your-backend.onrender.com`

**Option B: Netlify**
1. Connect GitHub repo
2. Base directory: `frontend`
3. Build command: `npm run build`
4. Publish directory: `frontend/dist`
5. Environment variable: `VITE_API_URL=https://your-backend.onrender.com`

### Step 4: Test

1. Visit: `https://your-backend.onrender.com/docs`
2. Test `/api/health` endpoint
3. Register via `/api/register`
4. Check email for briefing!

## LangGraph Workflow

The agent workflow consists of 8 nodes:

1. **Calendar Check**: Validates timezone-aware send time
2. **Query Analysis**: Generates search queries (Groq LLM)
3. **Search**: Executes Tavily searches
4. **Deduplication**: Filters duplicate articles
5. **Summarize**: Creates 1-2 line summaries (Groq LLM)
6. **Store**: Saves to PostgreSQL
7. **Format**: Generates HTML email (Groq LLM)
8. **Email**: Sends via SMTP

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/register` | POST | Register user |
| `/api/preferences/{email}` | GET | Get user preferences |
| `/api/preferences/{email}` | PUT | Update preferences |
| `/api/preferences/{email}` | DELETE | Delete user |
| `/api/query` | POST | Real-time search |
| `/api/metrics/{email}` | GET | User metrics |
| `/api/admin/jobs` | GET | List scheduled jobs |
| `/api/admin/trigger-briefing/{email}` | POST | Trigger briefing |

See full API docs at `/docs` (Swagger UI) when server is running.

## Database Schema

**users**
- email (PK)
- preferences (JSON)
- timezone
- briefing_time
- created_at

**articles**
- id (PK, SHA256 hash)
- url_hash (unique, indexed)
- title
- url
- summary
- created_at

**user_articles**
- user_email (FK)
- article_id (FK)
- sent_at

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent --cov=app --cov-report=html

# Run specific tests
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Project Structure

```
/
├── app/                      # FastAPI application
│   ├── main.py               # FastAPI app with endpoints
│   ├── scheduler.py          # APScheduler configuration
│   └── agent_runner.py       # LangGraph runner wrapper
├── agent/                    # LangGraph agent
│   ├── workflow.py           # 8-node workflow
│   ├── state.py              # State schema
│   └── tools/
│       ├── tavily_tool.py
│       ├── groq_tool.py
│       ├── database_tool.py  # PostgreSQL operations
│       ├── email_tool.py     # SMTP email
│       └── calendar_tool.py
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Onboarding.tsx
│   │   │   ├── QueryInterface.tsx
│   │   │   └── Metrics.tsx
│   │   └── api/client.ts
│   └── package.json
├── alembic/                  # Database migrations
│   └── versions/
├── tests/                    # Test suite
├── database.py               # SQLAlchemy models
├── config.py                 # Configuration
├── requirements.txt
├── Procfile                  # Render deployment
├── render.yaml               # Render infrastructure
└── README.md
```

## Development

### Create Database Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Local Development with Hot Reload

```bash
# Backend (FastAPI hot reload)
uvicorn app.main:app --reload

# Frontend (Vite hot reload)
cd frontend && npm run dev
```

## Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| Render Web Service | Free (750 hrs/month) | $0 |
| Render PostgreSQL | Free (1 GB) | $0 |
| Groq API | Free tier | $0 |
| Tavily API | Free tier (1K searches/month) | $0 |
| Gmail SMTP | Free | $0 |
| **Total** | | **$0/month** |

**Notes:**
- Free tier spins down after 15 min inactivity (~30s cold start)
- For always-on: Render Starter ($7/month)
- Supports 100+ users on free tier

## Gmail SMTP Setup

1. Enable 2-factor authentication on Gmail
2. Generate App Password:
   - Google Account → Security → 2-Step Verification → App Passwords
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password
3. Add to `.env`:
   ```
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=<16-char app password>
   ```

## Troubleshooting

**Database connection failed:**
- Check `DATABASE_URL` format: `postgresql://user:pass@host:5432/dbname`
- Verify PostgreSQL is running: `docker ps` or `pg_isready`

**Scheduler not starting:**
- Check logs: Database must be initialized first
- Run: `alembic upgrade head`

**Frontend can't connect to backend:**
- Check `VITE_API_URL` in frontend `.env`
- Verify CORS settings in `app/main.py`

**Emails not sending:**
- Check Gmail App Password (not regular password)
- Verify `SMTP_ENABLED=true` in `.env`
- Check logs for SMTP errors

## License

See [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
