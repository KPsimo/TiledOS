import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from github import Github

# ============================================================
# CONFIGURATION
# ============================================================

# base and data paths
base = Path(__file__).resolve().parent
data_dir = base / "data"
data_dir.mkdir(exist_ok=True)

# Look for credentials in ./data/credentials.json, fallback to ./credentials.json
CREDENTIALS_PATH = data_dir / "credentials.json"
if not CREDENTIALS_PATH.exists():
    alt = base / "credentials.json"
    if alt.exists():
        CREDENTIALS_PATH = alt #need to check alternative because we might change credentials path

# Token and output files
TOKEN_PATH = data_dir / "token.json"
TASKS_JSON_PATH = base / "tasks.json"

# Google Tasks API scope
SCOPES = ["https://www.googleapis.com/auth/tasks"] #used to be readonly but changed cuz we want to edit

# ============================================================
# AUTHENTICATION (Google)
# ============================================================

creds = None

if TOKEN_PATH.exists():
    # Reuse saved token
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
else:
    # No token yet; need credentials.json to authorize
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Google OAuth client secrets not found.\n"
            f"Expected at: {CREDENTIALS_PATH}\n\n"
            "Download an OAuth 2.0 Client ID (Desktop) JSON from Google Cloud Console "
            "and save it as credentials.json in the data folder."
        )

    # Launch browser to complete Google OAuth
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token for next time
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

# ============================================================
# FETCH TASKS FROM GOOGLE
# ============================================================

service = build("tasks", "v1", credentials=creds)

print("Connected to Google Tasks API.")
tasklists_resp = service.tasklists().list(maxResults=100).execute()
tasklists = tasklists_resp.get("items", [])

tasks_data = []

for tl in tasklists:
    list_id = tl["id"]
    list_title = tl.get("title", "")
    tasks_resp = service.tasks().list(
        tasklist=list_id, showCompleted=True, maxResults=200
    ).execute()
    tasks = tasks_resp.get("items", [])

    tasks_data.append({
        "taskListId": list_id,
        "taskListTitle": list_title,
        "tasks": [
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "notes": t.get("notes"),
                "status": t.get("status"),
                "due": t.get("due"),
                "completed": t.get("completed"),
                "updated": t.get("updated"),
                "parent": t.get("parent"),
                "position": t.get("position"),
                "links": t.get("links", []),
            } for t in tasks
        ]
    })

# Save locally
with open(TASKS_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(tasks_data, f, indent=2, ensure_ascii=False)

print(f"Saved tasks to {TASKS_JSON_PATH}")

# ============================================================
# OPTIONAL: UPLOAD TO GITHUB
# ============================================================

# To enable GitHub upload, set these environment variables:
#   GITHUB_TOKEN  = your personal access token (with repo scope)
#   GITHUB_REPO   = "username/repository"
#   GITHUB_PATH   = "folder/tasks.json" (optional; defaults to "tasks.json")

gh_token = os.getenv("GITHUB_TOKEN")
gh_repo_fullname = os.getenv("GITHUB_REPO")
gh_repo_path = os.getenv("GITHUB_PATH", "tasks.json")

if gh_token and gh_repo_fullname:
    print("Connecting to GitHub...")
    gh = Github(gh_token)
    repo = gh.get_repo(gh_repo_fullname)

    with open(TASKS_JSON_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        # Try to update if file exists
        existing = repo.get_contents(gh_repo_path)
        repo.update_file(gh_repo_path, "Update tasks.json", content, existing.sha)
        print(f"Updated {gh_repo_path} in {gh_repo_fullname}")
    except Exception:
        # Otherwise, create new file
        repo.create_file(gh_repo_path, "Create tasks.json", content)
        print(f"Created {gh_repo_path} in {gh_repo_fullname}")
else:
    print("GitHub upload skipped — missing GITHUB_TOKEN or GITHUB_REPO.")

print("Done! Your Google Tasks have been synced.")
