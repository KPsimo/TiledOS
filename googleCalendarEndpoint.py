import os
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/tasks",
]
#now both scopes in endpoints match

def _get_paths():
    root = os.path.dirname(os.path.abspath(__file__))
    return (
        os.path.join(root, "data", "credentials.json"),
        os.path.join(root, "data", "token.json"), #singular needed
    )

def _get_service():
    credentials_path, token_path = _get_paths()

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

from datetime import datetime, timedelta, timezone

def get_events_for_day(date_yyyy_mm_dd: str, calendar_id: str = "primary", max_results: int = 25):
    """
    Fetch Google Calendar events for a specific day.

    Args:
        date_yyyy_mm_dd (str): Date in YYYY-MM-DD format
        calendar_id (str): Calendar ID (default: primary)
        max_results (int): Max number of events to return

    Returns:
        List[Dict]: [{start, end, summary}, ...]
    """
    service = _get_service()

    # Google Calendar API REQUIRES RFC3339 timestamps with timezone
    start_dt = datetime.fromisoformat(date_yyyy_mm_dd + "T00:00:00").replace(tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1)

    response = service.events().list(
        calendarId=calendar_id,
        timeMin=start_dt.isoformat().replace("+00:00", "Z"),
        timeMax=end_dt.isoformat().replace("+00:00", "Z"),
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results,
    ).execute()

    events = []
    for ev in response.get("items", []):
        start = (
            ev.get("start", {}).get("dateTime")
            or ev.get("start", {}).get("date")
            or ""
        )
        end = (
            ev.get("end", {}).get("dateTime")
            or ev.get("end", {}).get("date")
            or ""
        )
        summary = ev.get("summary", "(No title)")

        events.append({
            "start": start,
            "end": end,
            "summary": summary,
        })

    return events


    items = []
    for ev in resp.get("items", []):
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date") or ""
        end = ev.get("end", {}).get("dateTime") or ev.get("end", {}).get("date") or ""
        summary = ev.get("summary", "(No title)")
        items.append({"start": start, "end": end, "summary": summary})

    return items
