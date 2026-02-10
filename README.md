# IssuePilot

IssuePilot is an automated GitHub issue triage system designed to help open source maintainers manage their repositories more efficiently. It fetches open issues, classifies them using a Machine Learning model (TF-IDF + Naive Bayes), assigns a priority score, and provides a real-time dashboard for management.

## Features

- **Automated Triage**: Classifies issues as `bug`, `feature`, or `documentation`.
- **Priority Scoring**: Calculates priority based on keywords and issue age.
- **Real-time Webhooks**: Reacts immediately to new or updated issues.
- **Visual Dashboard**: View charts, filter by repository, and manually correct labels.
- **Multi-Repository Support**: Manage issues from multiple repositories in one place.
- **Analytics & Export**: Download issue data as CSV and view label distribution.
- **Authentication**: Secured API endpoints using API Key.
- **Production Ready**: Dockerized, with SQLite database and rate limiting.

## Tech Stack

-   **Backend**: Python, FastAPI, SQLAlchemy, SQLite (in `backend/`)
-   **Frontend**: HTML5, Chart.js (in `frontend/`)
-   **ML**: Scikit-learn (TF-IDF + Naive Bayes)
-   **Infra**: Docker, Docker Compose
-   **CI/CD**: GitHub Actions

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd IssuePilot
    ```

2.  **Environment Setup:**
    Copy `.env.example` to `backend/.env` and configure:
    ```bash
    cp .env.example backend/.env
    ```
    Edit `backend/.env`:
    ```env
    GITHUB_TOKEN=your_token
    REPO_NAME=owner/repo
    API_KEY=your_secure_key
    ```

3.  **Run with Docker (Recommended):**
    ```bash
    docker-compose up --build
    ```
    The application will be available at `http://localhost:8000`.

## Configuration

### 1. Generating Your IssuePilot API Key
This key protects your dashboard and API. You can generate a strong random key via terminal:
```bash
# Mac/Linux/WSL
openssl rand -hex 32
```
Or simply create a strong password. Add it to your `backend/.env` file:
```ini
API_KEY=your_generated_secure_key
```

### 2. Getting a GitHub Token
Required for fetching issues from your repository.
1.  Go to **GitHub Settings** -> **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**.
2.  Click **Generate new token (classic)**.
3.  Select scopes:
    *   `repo` (Full control of private repositories)
    *   `read:org` (If your repo is in an organization)
4.  Copy the token starting with `ghp_` and add it to `backend/.env`:
    ```ini
    GITHUB_TOKEN=ghp_xxxxxxxxxxxx
    ```

## Usage

### Dashboard
Visit `http://localhost:8000/dashboard` to view the dashboard, charts, and manage issues.
-   **Filter**: Use the input box to filter issues by repository (e.g., `owner/repo`).

### API Endpoints
-   `POST /sync`: Fetch issues (supports `?repo_name=...`).
-   `GET /issues`: List issues (supports `?repository=...`).
-   `POST /triage`: Run classification.
-   `GET /stats`: Get issue statistics.
-   `GET /export`: Download issues CSV.
-   `PATCH /issues/{id}`: Correct issue label.
-   `POST /webhook`: GitHub Webhook handler.
-   `GET /docs`: Interactive Swagger UI.

## Development

1.  **Backend Setup:**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Run Tests:**
    ```bash
    # From root
    $env:PYTHONPATH="backend"
    pytest backend/tests
    ```

3.  **Run Locally:**
    ```bash
    cd backend
    uvicorn src.main:app --reload
    ```
