import requests
import data.keys as keys

BASE_URL = "https://mcpsmd.instructure.com"
TOKEN = keys.canvasKey

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

params = {
    "start_date": "2026-01-20",
    "end_date": "2026-01-31",
    "per_page": 100
}

courseId = 956426

assignments = requests.get(
    f"{BASE_URL}/api/v1/courses/{courseId}/assignments",
    headers=headers,
    params=params
).json()

assignmentNames = [assignment['name'] for assignment in assignments]
assignmentDates = [assignment['due_at'] for assignment in assignments]

print(assignmentNames)

print(assignmentDates)