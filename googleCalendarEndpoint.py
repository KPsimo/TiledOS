import os
import threading
from datetime import datetime, timedelta, timezone, date as date_cls

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/tasks",
]
# now both scopes in endpoints match

# Service singleton (prevents rebuilding service repeatedly)
_service = None
_service_lock = threading.Lock()

# In-memory response cache to reduce duplicate API calls
_events_cache = {}
_events_cache_lock = threading.Lock()

def _get_paths():
    root = os.path.dirname(os.path.abspath(__file__))
    return (
        os.path.join(root, "data", "credentials.json"),
        os.path.join(root, "data", "token.json"),  # singular needed
    )

def _get_service():
    global _service
    with _service_lock:
        if _service is not None:
            return _service

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

        _service = build("calendar", "v3", credentials=creds)
        return _service

def _rfc3339_utc(dt_obj: datetime) -> str:
    return dt_obj.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

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

    # Google Calendar API requires RFC3339 timestamps with timezone
    start_dt = datetime.fromisoformat(date_yyyy_mm_dd + "T00:00:00").replace(tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1)

    response = service.events().list(
        calendarId=calendar_id,
        timeMin=_rfc3339_utc(start_dt),
        timeMax=_rfc3339_utc(end_dt),
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results,
    ).execute()

    events = []
    for ev in response.get("items", []):
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date") or ""
        end = ev.get("end", {}).get("dateTime") or ev.get("end", {}).get("date") or ""
        summary = ev.get("summary", "(No title)")
        events.append({"start": start, "end": end, "summary": summary})

    return events

def get_events_for_range(start_dt: datetime, end_dt: datetime, calendar_id: str = "primary", max_results: int = 250):
    """
    Fetch events between start_dt (inclusive) and end_dt (exclusive).
    Returns list of dicts: {start, end, summary}
    """
    service = _get_service()

    time_min = _rfc3339_utc(start_dt)
    time_max = _rfc3339_utc(end_dt)

    cache_key = (calendar_id, time_min, time_max, max_results)
    with _events_cache_lock:
        if cache_key in _events_cache:
            return _events_cache[cache_key]

    resp = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results,
    ).execute()

    items = []
    for ev in resp.get("items", []):
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date") or ""
        end = ev.get("end", {}).get("dateTime") or ev.get("end", {}).get("date") or ""
        summary = ev.get("summary", "(No title)")
        items.append({"start": start, "end": end, "summary": summary})

    with _events_cache_lock:
        _events_cache[cache_key] = items

    return items

def get_events_by_date_for_month_grid(year: int, month: int, calendar_id: str = "primary"):
    """
    Builds a map:
        { datetime.date -> [ {start,end,summary}, ... ] }
    for the 6-week grid (spillover included).
    """
    import calendar as pycal

    cal = pycal.Calendar(firstweekday=0)  # Monday

    month_days = cal.monthdatescalendar(year, month)

    # Force 6 rows (same shape as your UI)
    while len(month_days) < 6:
        last_day = month_days[-1][-1]
        next_week = [last_day + timedelta(days=i) for i in range(1, 8)]
        month_days.append(next_week)
    month_days = month_days[:6]

    grid_start = month_days[0][0]
    grid_end_exclusive = month_days[-1][-1] + timedelta(days=1)

    start_dt = datetime(grid_start.year, grid_start.month, grid_start.day, 0, 0, 0, tzinfo=timezone.utc)
    end_dt = datetime(grid_end_exclusive.year, grid_end_exclusive.month, grid_end_exclusive.day, 0, 0, 0, tzinfo=timezone.utc)

    events = get_events_for_range(start_dt, end_dt, calendar_id=calendar_id)

    by_date = {}
    for ev in events:
        start_str = ev.get("start", "")
        if len(start_str) >= 10:
            try:
                d = date_cls.fromisoformat(start_str[:10])
            except Exception:
                continue
            by_date.setdefault(d, []).append(ev)

    return (grid_start, grid_end_exclusive, by_date)