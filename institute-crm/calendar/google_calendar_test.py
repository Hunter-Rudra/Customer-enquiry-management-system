from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import traceback

# Permission requested from Google
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Find the main institute-crm folder
PROJECT_DIR = Path(__file__).resolve().parents[1]

CREDENTIALS_FILE = PROJECT_DIR / "credentials.json"
TOKEN_FILE = PROJECT_DIR / "token.json"

def get_google_credentials():
    
    credentials = None
    
    # Check whether we already have a saved login
    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), 
            SCOPES
        )
        
    # Login again or refresh the existing login
    if not credentials or not credentials.valid:
        
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )
            
            credentials = flow.run_local_server(port=0)
        
        # Save the login for future runs
        TOKEN_FILE.write_text(credentials.to_json())
        
    return credentials


def get_upcoming_events():
    
    credentials = get_google_credentials()
    
    service = build(
        "calendar",
        "v3",
        credentials=credentials
    )
    
    
    now = datetime.now(
        timezone.utc
    ).isoformat()
    
    events_result = service.events().list(
        calendarId = "primary",
        timeMin = now,
        maxResults = 5,
        singleEvents = True,
        orderBy = "startTime"        
    ).execute()
    
    events = events_result.get("items", [])
    
    if not events:
        print("No upcoming events found.")
        return
    
    print("\nYour upcoming Google Calendar events:\n")
    
    for event in events:
        
        start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )
        
        title = event.get("summary", "untitled event")
        
        print(f"Event: {title}")
        print(f"Time: {start}")
        print("_" * 40)
        

def create_calendar_event(service, title, start_time, end_time, description=""):
    
    # Check that the end time is after the start time
    if end_time <= start_time:
        raise ValueError("End time must be after start time.")
    
    if start_time.tzinfo is None or end_time.tzinfo is None:
        raise ValueError("Both times must include timezone information.")
    
    # Prepare the event in Google's required format
    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata"
        }
    }
    
    # Send the event to Google calendar
    created_event = service.events().insert(
        calendarId = "primary",
        body = event
    ).execute()
    
    print("Event Created successfully!")
    print("Event ID:", created_event["id"])
    print("Event link:", created_event.get("htmlLink"))
    
    return created_event

def test_create_event():
    
    credentials = get_google_credentials()
    
    service = build(
        "calendar",
        "v3",
        credentials=credentials
    )
    
    # Current time in Indian Standard Time
    start_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ) + timedelta(minutes=10)

    end_time = start_time + timedelta(hours=1)
    
    create_calendar_event(
        service=service,
        title="InstituteFlow Python Test",
        start_time = start_time,
        end_time = end_time,
        description = "Testing event creation from InstituteFlow CRM."
    )
        
        
if __name__ == "__main__":
    
    try:
        test_create_event()
        
    except HttpError as error:
        print(f"Google Calendar API error: {error}")
        
    except FileNotFoundError as error:
        print(f"Required file not found: {error}")
        
    # except Exception as error:
    #     print(f"Something went wrong: {error}")
        
    except Exception:
        traceback.print_exc()
        
        