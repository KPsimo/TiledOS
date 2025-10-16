import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from github import Github

# Quick test mode and dry-run flags
TEST_MODE = os.environ.get('TASKS_TEST_MODE', '0') == '1'  # Set to '1' to enable
DRY_RUN = os.environ.get('TASKS_DRY_RUN', '0') == '1'      # Set to '1' to avoid GitHub push

# Google Tasks API setup (OAuth) - skipped in TEST_MODE
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
tasks_data = []

if TEST_MODE:
    # Provide sample tasks for testing without hitting Google APIs
    tasks_data = [
        {'title': 'Test Task 1', 'status': 'needsAction', 'due': None},
        {'title': 'Test Task 2', 'status': 'completed', 'due': '2025-09-30T12:00:00.000Z'},
    ]
else:
    creds = None
    # Load credentials from token.json or run the InstalledAppFlow
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print('Failed to load token.json, will attempt re-auth:', e)
            creds = None

    if creds is None:
        if not os.path.exists('credentials.json'):
            raise FileNotFoundError('credentials.json not found. Create OAuth client credentials in the Google Cloud Console and save as credentials.json')
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())

    # Build the Tasks service with OAuth credentials
    service = build('tasks', 'v1', credentials=creds)

    # Fetch tasks from Google Tasks (use .get() and basic error handling)
    try:
        tasklists_resp = service.tasklists().list().execute()
        tasklists = tasklists_resp.get('items', [])
    except Exception as e:
        print('Failed to fetch task lists:', e)
        tasklists = []

    for tasklist in tasklists:
        tasklist_id = tasklist.get('id')
        if not tasklist_id:
            continue
        try:
            tasks_resp = service.tasks().list(tasklist=tasklist_id).execute()
            for task in tasks_resp.get('items', []):
                tasks_data.append({
                    'title': task.get('title'),
                    'status': task.get('status'),
                    'due': task.get('due')
                })
        except Exception as e:
            print(f'Failed to fetch tasks for tasklist {tasklist_id}:', e)

# GitHub API setup - prefer token from environment
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', 'your_github_token')  # Replace or set env var
g = Github(GITHUB_TOKEN)
repo = g.get_user().get_repo('your_repo_name')  # Replace with your repository name
file_path = 'tasks.json'  # The file where tasks will be stored

# Write tasks to a GitHub file
with open('tasks.json', 'w', encoding='utf-8') as f:
    json.dump(tasks_data, f, indent=4, ensure_ascii=False)  # Pretty print the JSON

with open('tasks.json', 'r', encoding='utf-8') as f:
    content = f.read()

try:
    # Check if the file already exists
    existing_file = repo.get_contents(file_path)
    # Update the file if it exists
    repo.update_file(file_path, "Update tasks", content, existing_file.sha)
except Exception:
    # Create the file if it doesn't exist
    repo.create_file(file_path, "Create tasks", content)

print("Tasks synced successfully!")