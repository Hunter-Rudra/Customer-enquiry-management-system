import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Permission requested from Google
SCOPES = ["https://www.googleapis.com/auth/calendar.readonaly"]

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
    
    
    now = datetime.datetime.now(
        datetime.timezone.utc
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
        
        
if __name__ == "__main__":
    
    try:
        get_upcoming_events()
        
    except HttpError as error:
        print(f"Google Calendar API error: {error}")
        
    except FileNotFoundError as error:
        print(f"Required file not found: {error}")
        
    except Exception as error:
        print(f"Something went wrong: {error}")