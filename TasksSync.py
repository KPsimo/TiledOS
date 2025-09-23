import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from github import Github

# Google Tasks API setup
# Use OAuth to access user data. This requires a local `credentials.json` (client
# secrets) and will store the resulting user tokens in `token.json`.
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
creds = None

# Load credentials from token.json or run the InstalledAppFlow
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
else:
    if not os.path.exists('credentials.json'):
        raise FileNotFoundError('credentials.json not found. Create OAuth client credentials in the Google Cloud Console and save as credentials.json')
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w', encoding='utf-8') as token:
        token.write(creds.to_json())

# Build the Tasks service with OAuth credentials
service = build('tasks', 'v1', credentials=creds)

# Fetch tasks from Google Tasks (use .get() and basic error handling)
tasks_data = []
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
