# IssuePilot

A high-performance, automated GitHub issue triage system designed to help open source maintainers manage their repositories more efficiently. It classifies issues, prioritizes them, and provides a real-time "coder-style" dashboard for management.

## Problem
Open source maintainers are drowning in issues. Bugs, feature requests, and questions pile up faster than they can be sorted. Valuable time is wasted manually tagging issues and deciding what to work on next. Important bugs get buried under a mountain of support questions.

## Solution
**IssuePilot** automates the chaos. It uses a **Machine Learning model** (TF-IDF + Naive Bayes) to instantly classify incoming issues. It assigns a **priority score** based on keywords and age, ensuring critical bugs drift to the top. A dark-mode, IDE-inspired dashboard gives maintainers a clear, filterable view of their repository's health across multiple projects.

## Quick Start (Docker)

The fastest way to get started is using Docker.

```bash
# Clone repository
git clone https://github.com/Rhytam23/issuepilot.git
cd issuepilot

# Create .env file
cp backend/.env.example backend/.env

# Update .env with your credentials
# (See Configuration section below)

# Run application
docker-compose up --build
```
Now open → `http://localhost:8000`

## Quick Start (Manual)

If you prefer running without Docker:

**1. Backend Setup**
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# Run server
uvicorn src.main:app --reload
```

**2. Access Dashboard**
Open `http://localhost:8000/dashboard` in your browser.

## Tech Stack
-   **Backend**: Python, FastAPI, SQLAlchemy
-   **Database**: SQLite (Production-ready file storage)
-   **ML**: Scikit-learn (TF-IDF + Naive Bayes)
-   **Frontend**: Vanilla HTML/JS, Chart.js
-   **Infrastructure**: Docker, GitHub Actions

## Core Features
### For Maintainers
-   **Automated Triage** → Instantly tags issues as `bug`, `feature`, or `doc`.
-   **Smart Prioritization** → Calculates a score (0-100) based on urgency.
-   **IDE-Style Dashboard** → Dark mode interface that feels like VS Code.
-   **Multi-Repo Support** → Manage `owner/repo-A` and `owner/repo-B` in one place.
-   **Real-time Webhooks** → Reacts immediately to new GitHub issues.
-   **CSV Export** → Download issue data for offline analysis.

### Security
-   **API Key Authentication** → Protects your dashboard and API.
-   **Rate Limiting** → Prevents API abuse.

## Configuration

You need to configure `backend/.env` for the app to work.

### 1. Generating Your IssuePilot API Key
This key protects your dashboard. Generate a strong key:
```bash
openssl rand -hex 32
# Result: 8f3... (copy this)
```
Add to `.env`: `API_KEY=your_secure_key`

### 2. Getting a GitHub Token
Required for fetching issues.
1.  Go to **GitHub Settings** -> **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**.
2.  Generate new token with `repo` scope.
3.  Add to `.env`: `GITHUB_TOKEN=ghp_...`

## Project Structure
```
issuepilot/
├── backend/
│   ├── src/           → FastAPI app & ML logic
│   ├── tests/         → Pytest suite
│   ├── Dockerfile     → Backend container
│   └── requirements.txt
├── frontend/
│   ├── index.html     → Dashboard (Main UI)
│   ├── login.html     → Authentication Page
│   └── landing.html   → Landing Page
├── data/              → Training datasets
├── .github/           → CI/CD workflows
└── docker-compose.yml → Orchestration
```

## Database Schema
`Issues` Table:
-   `id` (PK): GitHub Issue ID
-   `repository`: Repository Name (e.g. `owner/repo`)
-   `title`: Issue Title
-   `body`: Issue Description
-   `status`: Current Status (`new`, `triaged`)
-   `predicted_label`: ML Prediction (`bug`, `feature`)
-   `priority_score`: Calculated Score

## Contributing
PRs are welcome! Please run tests before submitting:
```bash
pytest backend/tests
```

## License
MIT License. Open Source for everyone.

---

## 📖 Project Understanding (Future Reference)

An automated GitHub issue triage system for open-source maintainers: a TF-IDF + Naive Bayes
model classifies incoming issues, a priority score (keywords + age) surfaces what matters, and a
dark-mode, IDE-styled dashboard gives a filterable, multi-repo view of issue health. Ships with a
one-command Docker Compose setup.

**Stack:** Python/ML backend (TF-IDF + Naive Bayes classifier), frontend dashboard, SQLite
storage (`storage.db`), Docker Compose deployment.
**Status:** functional dev-tooling project with a working quick-start.

## 🎯 Where This Can Be Used

- Real tooling for maintaining your own (or a team's) open-source repos.
- Portfolio piece demonstrating applied ML + a real operational dashboard, not just a notebook.
- **Hackathons:** strong fit for "dev tools" / "AI for open source" tracks — the Docker
  quick-start means it can be demoed live in minutes without a fragile local setup.
