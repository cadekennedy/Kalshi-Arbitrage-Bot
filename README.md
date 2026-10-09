# Kalshi Arbitrage Bot

A modular trading system for detecting and evaluating arbitrage opportunities in Kalshi prediction markets.

## Project Structure

- `backend/` — API, trading logic, market data, execution, and risk management
- `frontend/` — React dashboard
- `docs/` — project documentation
- `scripts/` — utility and development scripts
- `.github/` — GitHub Actions workflows

## Development Status

Current development phase:

**Iteration 0 — Foundation**

## Project Structure 

```
└── 📁Kalshi-Arbitrage-Bot
    └── 📁.github
        └── 📁workflow
    └── 📁backend
        └── 📁app
            └── 📁api
            └── 📁execution
            └── 📁market_data
            └── 📁models
            └── 📁risk
            └── 📁strategy
            ├── config.py
            ├── main.py
        └── 📁tests
        ├── Dockerfile
        ├── pyproject.toml
        ├── pytest.ini
        ├── requirements.txt
    └── 📁docs
    └── 📁frontend
    └── 📁scripts
    ├── .env.example
    ├── .gitignore
    ├── docker-compose.yml
    └── README.md
```
###### Special thanks to "Draw Folder Structure" for this markdown. 

## Requirements 

Install the following before starting development:

- Git
- Python 3.11+
- Node.js 22+
- npm
- Docker Desktop

## Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Kalshi-Arbitrage-Bot
```

The initial environment variables are:

```text
KALSHI_API_KEY=
KALSHI_PRIVATE_KEY_PATH=
TRADING_MODE=paper
LOG_LEVEL=INFO
```

**Do NOT commit `.env`** 

## Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a Python virtual environment: 

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux/Windows:

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app
```

The backend will run at:

```text
http://127.0.0.1:8000
```

Health/docs endpoint:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Backend Testing

From the `backend` directory

```bash
pytest
```

## Backend Linting

Check, fix, or verify linting and formatting issues
```bash
ruff check .
ruff check . --fix
ruff format .
ruf format . --check
```

## Frontend Setup

From the repository root:

```bash
cd frontend
npm install
```

The frontend will normally run at:

```text
http://localhost:5173
```

Run ESLint:

```bash
npm run lint
```

Build the frontend:

```bash
npm run build
```

## Docker Development

**Make sure Docker Desktop is running.**

From the repository root:

```bash
docker compose up --build
```

```text
Backend:
http://127.0.0.1:8000

Frontend:
http://localhost:5173
```

Stop the environement with:
```bash
docker compose down
```

## Development Workflow

For any GitHub issues, please create a branch for each:

```bash
git checkout main
git pull
git checkout -b feature/example-feature
```

After development:

```bash
git add .
git commit -m "Describe the change"
git push -u origin feature/example-feature
```

Open a pull request into `dev`.

**Every pull request should pass:**

- Backend Ruff checks
- Backend formatting checks
- Backend pytest tests
- Frontend ESLint checks
- Frontend production build
- GitHub Actions CI