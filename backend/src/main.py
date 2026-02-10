from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Dict
from src.github_client import fetch_issues
from src.ml_model import IssueClassifier
from src.priority_scorer import PriorityScorer
from src.storage import Storage
from src.config import Config
import logging

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("IssuePilot")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="IssuePilot", description="Automated GitHub Issue Triage System", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize components
storage = Storage()
classifier = IssueClassifier()
scorer = PriorityScorer()

@app.on_event("startup")
async def startup_event():
    # Load model on startup
    try:
        classifier.load_model()
        logger.info("ML Model loaded successfully.")
    except Exception as e:
        logger.warning(f"Failed to load ML model: {e}. Please ensure it is trained.")

from fastapi import Depends, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != Config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

@app.post("/sync", summary="Fetch and sync issues from GitHub", dependencies=[Depends(get_api_key)])
@limiter.limit("5/minute")
def sync_issues(request: Request, background_tasks: BackgroundTasks, repo_name: str = None):
    """
    Triggers a background task to fetch issues from the configured GitHub repository.
    Can optionally specify a repo_name to override the default.
    """
    target_repo = repo_name or Config.REPO_NAME
    if not target_repo:
        raise HTTPException(status_code=400, detail="Repository not specified and default not configured.")
    
    background_tasks.add_task(run_sync_process, target_repo)
    return {"message": f"Issue synchronization started for {target_repo}."}


def run_sync_process(repo_name: str):
    logger.info(f"Starting sync for {repo_name}...")
    try:
        issues = fetch_issues(repo_name)
        existing_data = storage.load_data()
        
        # Simple merge logic: convert existing to dict by ID for fast lookup
        existing_map = {item["id"]: item for item in existing_data}
        
        new_count = 0
        for issue in issues:
            if issue["id"] not in existing_map:
                # Add new issue with default status
                issue["status"] = "new"
                issue["predicted_label"] = None
                issue["priority_score"] = 0
                issue["repository"] = repo_name
                existing_map[issue["id"]] = issue
                new_count += 1
            else:
                # Update repository if missing
                 if "repository" not in existing_map[issue["id"]]:
                     existing_map[issue["id"]]["repository"] = repo_name
        
        storage.bulk_save(list(existing_map.values()))
        logger.info(f"Sync complete for {repo_name}. {new_count} new issues added.")
    except Exception as e:
        logger.error(f"Sync failed for {repo_name}: {e}", exc_info=True)

@app.post("/triage", summary="Run triage on stored issues", dependencies=[Depends(get_api_key)])
@limiter.limit("5/minute")
def run_triage(request: Request):
    """
    Runs classification and priority scoring on all 'new' issues.
    """
    data = storage.load_data()
    processed_count = 0
    
    # Identify issues needing triage
    to_triage = [item for item in data] # For now, re-triage all or check status. 
    # Let's re-triage all for simplicity to update scores as time passes.
    
    texts = [item.get("title", "") + " " + item.get("body", "") for item in to_triage]
    
    try:
        predictions = classifier.predict(texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage failed (Model Error): {e}")

    for i, item in enumerate(to_triage):
        item["predicted_label"] = predictions[i]
        item["priority_score"] = scorer.calculate_score(item)
        item["status"] = "triaged"
        processed_count += 1
    
    storage.bulk_save(data)
    return {"message": "Triage complete.", "processed_count": processed_count}

@app.get("/issues", summary="List triaged issues", dependencies=[Depends(get_api_key)])
def list_issues(status: str = None, min_score: int = 0, limit: int = 20, offset: int = 0, repository: str = None):
    """
    Returns a list of issues, optionally filtered by status, minimum priority score, and repository.
    Supports pagination via limits and offsets.
    """
    data = storage.load_data()
    filtered_results = []
    
    for item in data:
        if status and item.get("status") != status:
            continue
        if item.get("priority_score", 0) < min_score:
            continue
        if repository and item.get("repository") != repository:
            continue
        filtered_results.append(item)
        
    # Sort by priority score descending
    filtered_results.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    
    # Apply pagination
    paginated_results = filtered_results[offset : offset + limit]
    
    return {
        "total": len(filtered_results),
        "limit": limit,
        "offset": offset,
        "items": paginated_results
    }

from src.webhook import verify_signature

@app.post("/webhook", summary="GitHub Webhook Endpoint")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handles incoming GitHub webhooks. Triggers triage on new issues.
    """
    # Verify signature
    # In a real app, this would be a dependency or middleware
    await verify_signature(request)
    
    payload = await request.json()
    action = payload.get("action")
    issue = payload.get("issue")
    
    if action in ["opened", "reopened", "edited"] and issue:
        # Process the issue immediately
        # We need to adapt the issue payload to our internal format
        internal_issue = {
            "id": issue.get("id"),
            "number": issue.get("number"),
            "title": issue.get("title"),
            "body": issue.get("body") or "",
            "state": issue.get("state"),
            "created_at": issue.get("created_at"),
            "html_url": issue.get("html_url"),
            "status": "new",
            "predicted_label": None,
            "priority_score": 0
        }
        
        # Save to DB
        storage.save_issue_result(internal_issue["id"], internal_issue)
        
        # Trigger triage for this specific issue
        # Note: run_triage currently re-scans everything. We could optimize to triage just one.
        # For Phase 2, let's trigger the full triage or a specific one.
        # Let's just trigger the full triage for simplicity and correctness.
        background_tasks.add_task(run_triage)
        
    return {"message": "Webhook received"}

@app.get("/stats", summary="Get issue statistics", dependencies=[Depends(get_api_key)])
def get_stats():
    """
    Returns aggregated statistics for issues (by status and label).
    """
    data = storage.load_data()
    total = len(data)
    status_counts = {}
    label_counts = {}
    
    for item in data:
        s = item.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
        
        l = item.get("predicted_label") or "unlabeled"
        label_counts[l] = label_counts.get(l, 0) + 1
        
    return {
        "total": total,
        "status_counts": status_counts,
        "label_counts": label_counts
    }

import io
import csv
from fastapi.responses import StreamingResponse

@app.get("/export", summary="Export issues to CSV", dependencies=[Depends(get_api_key)])
def export_issues():
    """
    Generates a CSV file containing all stored issues.
    """
    data = storage.load_data()
    
    # Define CSV headers
    fieldnames = ["id", "number", "title", "state", "status", "predicted_label", "priority_score", "created_at", "html_url"]
    
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(data)
    
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=issues_export.csv"
    return response

from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

class LabelUpdate(BaseModel):
    label: str

@app.patch("/issues/{issue_id}", summary="Correct issue label", dependencies=[Depends(get_api_key)])
def update_label(issue_id: int, update: LabelUpdate):
    """
    Manually correct the predicted label for an issue.
    """
    data = storage.load_data()
    for item in data:
        if item["id"] == issue_id:
            item["predicted_label"] = update.label
            item["manual_correction"] = True # Flag for future retraining
            storage.save_issue_result(issue_id, item)
            return {"message": "Label updated", "issue": item}
            
    raise HTTPException(status_code=404, detail="Issue not found")

app.mount("/dashboard", StaticFiles(directory="../frontend", html=True), name="static")

@app.get("/login", include_in_schema=False)
async def login_page():
    return FileResponse("../frontend/login.html")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("../frontend/landing.html")
