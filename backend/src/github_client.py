import requests
import os
from typing import List, Dict, Optional
from src.config import Config

GITHUB_API_URL = "https://api.github.com"

def fetch_issues(repo_name: str, token: Optional[str] = None) -> List[Dict]:
    """
    Fetches open issues from a GitHub repository processing pagination.
    """
    if not token:
        token = Config.GITHUB_TOKEN
    
    if not token:
         # Log warning or error but proceed (might be public repo, but severe limit)
         pass

    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"

    issues = []
    page = 1
    per_page = 100

    while True:
        url = f"{GITHUB_API_URL}/repos/{repo_name}/issues"
        params = {
            "state": "open",
            "per_page": per_page,
            "page": page
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            for item in data:
                # Basic filtering: skip pull requests as they are also returned in issues endpoint
                if "pull_request" in item:
                    continue
                
                filtered_issue = {
                    "id": item.get("id"),
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "body": item.get("body") or "",
                    "state": item.get("state"),
                    "created_at": item.get("created_at"),
                    "labels": [label["name"] for label in item.get("labels", [])],
                    "html_url": item.get("html_url")
                }
                issues.append(filtered_issue)
            
            # Check Link header for pagination, but simplest logic is just data empty check or < per_page
            if len(data) < per_page:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues: {e}")
            break

    return issues
