from src.storage import Storage

print("Initializing Storage...")
s = Storage()

issues = [
    {
        "id": 101,
        "number": 101,
        "title": "Deep Learning model crashes on GPU",
        "body": "When running on colab, the model throws CUDA out of memory error.",
        "state": "open",
        "created_at": "2023-10-01T12:00:00Z",
        "html_url": "http://github.com/owner/repo/issues/101",
        "status": "triaged",
        "predicted_label": "bug",
        "priority_score": 95
    },
    {
        "id": 102,
        "number": 102,
        "title": "Add dark mode support",
        "body": "Please add a dark theme option to the settings.",
        "state": "open",
        "created_at": "2023-10-02T14:30:00Z",
        "html_url": "http://github.com/owner/repo/issues/102",
        "status": "triaged",
        "predicted_label": "feature",
        "priority_score": 60
    },
    {
        "id": 103,
        "number": 103,
        "title": "Missing API documentation for /users",
        "body": "The /users endpoint is not documented in the README.",
        "state": "open",
        "created_at": "2023-10-03T09:15:00Z",
        "html_url": "http://github.com/owner/repo/issues/103",
        "status": "triaged",
        "predicted_label": "documentation",
        "priority_score": 40
    },
     {
        "id": 104,
        "number": 104,
        "title": "Typo in README line 45",
        "body": "Fixed typo on line 45.",
        "state": "closed",
        "created_at": "2023-10-04T10:00:00Z",
        "html_url": "http://github.com/owner/repo/issues/104",
        "status": "triaged",
        "predicted_label": "documentation",
        "priority_score": 10
    },
    {
        "id": 105,
        "number": 105,
        "title": "Security vulnerability in numpy dependency",
        "body": "Critical CVE found in package version 1.25.",
        "state": "open",
        "created_at": "2023-10-05T16:45:00Z",
        "html_url": "http://github.com/owner/repo/issues/105",
        "status": "new",
        "predicted_label": "bug",
        "priority_score": 100
    }
]

for issue in issues:
    print(f"Saving issue {issue['number']}...")
    s.save_issue_result(issue["id"], issue)

print("Seed data inserted successfully.")
